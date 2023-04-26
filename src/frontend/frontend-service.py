from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
import socketserver
import grpc
import threading
from threading import Lock 
import sys
sys.path.append('../..')

from src.shared.util import logging
from src import config
from src.shared.proto import stocktrade_pb2
from src.shared.proto import stocktrade_pb2_grpc
from src.shared.model import stock

cache = {}
lock = Lock()
leader_id = 0

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    #setting HTTP protocol version to 1.1
    protocol_version = 'HTTP/1.1'
    def do_GET(self):
        '''
        overriding function do_GET to handle get requests
        '''
        #get path and request parameters from url
        path, request_params = self._parse_url()
        if (path == '/hello'):
            # /hello?name=<> path. Return a hello response
            name = request_params.get('name', [None])[0]
            message = f"Hello, {name}!"
            self._send_response(message)
        elif (path == '/stocks'):
            #handle /stock?stockname=<> endpoint. Requests to this url are used to perform lookup on a stockname
            stockname = request_params.get('stockname', [None])[0] #get stockname from query parameters
            response = lookup(stockname) #perform lookup on the stockname
            self._send_response(response) #send http response
        elif (path == '/orders'):
            #handle /orders/<order_number> endpoint. Endpoint to get query existing orders
            order_id =  request_params.get('order-number', [None])[0] #get order number from query parameters
            response = order_lookup(order_id)
            self._send_response(response)
        else:
            #Send 404 error for all other paths
            logger.warning(f'Path does not exist : {path}')
            self.send_error(404)

    def do_POST(self):
        #get path from url
        path, _ = self._parse_url()
        #get request body
        request_body = self._get_request_body()
        if (path == '/orders'):
            #handle /orders endpoint. Used to perform a trade on a stock
            response = trade(request_body['name'],request_body['quantity'], request_body['type']) #perform trade on the stockname
            self._send_response(response) #send http response
        else:
             #Send 404 error for all other paths
            logger.warning(f'Path does not exist : {path}')
            self.send_error(404)

    def log_message(self, format, *args):
        #Overriding function to use custom logging
        logger.info('%s %s', self.address_string(), format % args)

    def _parse_url(self):
        '''
        Function to parse url
        return path: the base path in the url
        return request_params: the request parameters in the path
        '''
        parsed_url = urlparse(self.path)
        base_path = parsed_url.path
        request_params = parse_qs(parsed_url.query)
        return base_path, request_params

    def _get_request_body(self):
        '''
        Function to read request body and parse json
        return request body: the json request body
        '''
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            return json.loads(body)
        except Exception as e:
            logger.error(f'Failed to read request body with exception: {e}')

    def _send_response(self, response):
        '''
        Function to send http response to client
        '''
        response = response.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header("Connection", "keep-alive")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)


def lookup(stockname):
    '''
    Function to initiate lookup on a stock
    :param stockname: name of the stock to initiate lookup on
    '''
    logger.info(f"Sending lookup request for : {stockname}")
    try:
        #check in cache
        global cache
        if stockname in cache:
            logger.info(f"Performing lookup on stock: {stockname} in cache")
            with lock:
                lookup_stock= cache[stockname]
                response =  {
                    'name' : lookup_stock.name,
                    'price' : lookup_stock.getPrice(),
                    'quantity' : lookup_stock.volume
                }
                return get_http_response(response)
        else:
            #call catalog service
            hostAddr = config.catalog_hostname + ':' + str(config.catalog_port)
            with grpc.insecure_channel(hostAddr) as channel:
                stub = stocktrade_pb2_grpc.CatalogServiceStub(channel)
                lookup_response = stub.Lookup(stocktrade_pb2.LookupRequest(stockname= stockname))
                logger.info(
                    f"Lookup request: {lookup_response.stockname}, response: Price of stock: {lookup_response.price}, Volume of the stock: {lookup_response.volume}")
                if lookup_response.price != -1:
                    response =  {
                        'name' : lookup_response.stockname,
                        'price' : lookup_response.price,
                        'quantity' : lookup_response.volume
                    }
                    cache[stockname] = stock.Stock(name= lookup_response.stockname, price= lookup_response.price, vol=lookup_response.volume)
                    return get_http_response(response) #prepare http response
                else:
                    return get_http_error_response(404, 'stock not found') #prepare http error response
    except Exception as e:
        logger.error(f"Failed to get lookup response for {stockname} with expception: {e}") 
    return get_http_error_response(404, 'Internal Server Error')

def trade(stockname, quantity, trade_type):
    '''
    Function to initiate trade on a stock
    :param stockname: name of the stock to initiate trade on
    :param quantity: quantity being traded
    :param trade_type: type of the trade. BUY or SELL
    '''
    logger.info(f"Sending trade request of type: {trade_type} for : {stockname} with quantity: {quantity}")
    try:
        #call order service
        hostAddr = config.order_hostname + ':' + str(config.order_port)
        with grpc.insecure_channel(hostAddr) as channel:
            stub = stocktrade_pb2_grpc.OrderServiceStub(channel)
            order_response = stub.Trade(stocktrade_pb2.TradeRequest(
                stockname=stockname, quantity=quantity, trade_type=trade_type))
            logger.info(
                f"Trade request: {stockname}, {quantity}, response status : {order_response.status}")
            if (order_response.status == 1):
                response = {
                    'transaction_number' : order_response.transaction_number
                }
                return get_http_response(response) #prepare http response
            elif (order_response.status == 0):
                return get_http_error_response(404, 'Trading not permitted due to insufficient volume') #prepare order response
            else:
                return get_http_error_response(404, 'Stock not found')
    except Exception as e:
        logger.error(f"Failed to get trade response for {stockname} with exception: {e}")
        return get_http_error_response(404, 'Internal Server Error')
    
def order_lookup(order_id):
    '''
    Function to query an existing order
    :param order_id: order id of the order to perform lookup on
    '''
    logger.info(f"Performing get request for order: {order_id}")
    try:
        #query the order service
        order_id = int(order_id)
        hostAddr = config.order_hostname + ':' + str(config.order_port)
        with grpc.insecure_channel(hostAddr) as channel:
            stub = stocktrade_pb2_grpc.OrderServiceStub(channel)
            order_lookup_response = stub.OrderLookup(stocktrade_pb2.OrderLookupRequest(order_id= order_id))
            logger.info(
                f"Order lookup request: {order_id}, response: Name of stock: {order_lookup_response.stockname}, type of trade: {order_lookup_response.trade_type}, quantity : {order_lookup_response.quantity}")
            if order_lookup_response.status == 1:
                response =  {
                    'number' : order_lookup_response.order_id,
                    'name' : order_lookup_response.stockname,
                    'type' : 'SELL' if order_lookup_response.trade_type == 1 else 'BUY',
                    'quantity' : order_lookup_response.quantity
                }
                return get_http_response(response) #prepare http response
            else:
                return get_http_error_response(404, 'order not found') #prepare http error response
    except Exception as e:
        logger.error(f"Failed to query order {order_id} with expception: {e}") 
    return get_http_error_response(404, 'Internal Server Error')

def subscribe_to_db_updates():
    logger.info(f"Subscribing to db updates messages")
    try:
        hostAddr = config.order_hostname + ':' + str(config.order_port)
        with grpc.insecure_channel(hostAddr) as channel:
            stub = stocktrade_pb2_grpc.OrderServiceStub(channel)
            global cache
            for response in stub.StreamDBUpdates(stocktrade_pb2.Empty()):
                stockname = response.stockname
                logger.info(f"Invalidating stock : {stockname} in cache")
                if stockname in cache:
                    with lock: 
                        del cache[stockname]
    except Exception as e:
        logger.error(f"Failed to subscribe to order updates")
        print(e)

#TODO: remove the function (not using)
def save_file():
    '''
    Function to call save files before exiting.
    '''
    hostAddr = config.order_hostname + ':' + str(config.order_port)  
    with grpc.insecure_channel(hostAddr) as channel:
        stub = stocktrade_pb2_grpc.OrderServiceStub(channel)
        stub.Save(stocktrade_pb2.Empty())
        

def get_http_response(response):
    '''
    Function to prepare http response.
    Response is of the structure {'data' : response}
    '''
    response = {
            'data': response
        }
    return convert_to_json(response)

def get_http_error_response(error_code, error_message):
    '''
    Function to error http response.
    Response is of the structure {'error' : {'code' : ..., 'message' : ...}}
    '''
    response = {
        'error': {
            'code': error_code,
            'message': error_message
        }
    }
    return convert_to_json(response)

def convert_to_json(obj):
    '''
    Function to convert python object to json.
    return json object: the json equivalent of the python object
    '''
    try:
        json_obj = json.dumps(obj)
        return json_obj
    except Exception as e:
        return None

def leader_election():
    '''
    Function to elect leader among all the order service instances
    sends isAlive request to all the instances in reverse order of their IDs, whenever a response is received stops the election and broadcasts the leader.
    '''
    print("Leader election")
    global leader_id
    leader_id = 0
    for i in range(len(config.order_ports)-1, -1,-1):
        try:
            hostAddr = config.order_hostname + ':' + str(config.order_ports[i])
            logger.info(f"Sending IsAlive to the order service instance at {hostAddr}")
            with grpc.insecure_channel(hostAddr) as channel:
                stub = stocktrade_pb2_grpc.OrderServiceStub(channel)
                alive_response = stub.IsAlive(stocktrade_pb2.Empty())
                if alive_response.is_alive:
                    leader_id = i+1
                    break
        except Exception as e:
            logger.error(f"Order service instance at {hostAddr} is not alive or an exception occured conneting to the service\nException: {e}")
    
    if leader_id != 0:
        print(f"Leader found in leader election: order service instance: {leader_id}")
        broadcast_leader(leader_id)
    else:
        print("Leader cannot be found - Please be sure that atleast one order service instance is up and running")
    return


def broadcast_leader(id):
    '''
    Function to broadcast the elected leader to all the order service instances
    :param id: id of the leader order service
    '''
    print("Broadcast leader")
    for i in range(len(config.order_ports)):
        try:
            hostAddr = config.order_hostname + ':' + str(config.order_ports[i])
            logger.info(f"Sending SetLeader to the order service instance at {hostAddr}, leader_id={id}")
            with grpc.insecure_channel(hostAddr) as channel:
                stub = stocktrade_pb2_grpc.OrderServiceStub(channel)
                set_leader_response = stub.SetLeader(stocktrade_pb2.SetLeaderRequest(leader_id=id))
        except Exception as e:
            logger.error(f"Failed to send SetLeader to the service instance at {hostAddr}, leader_id= {id}\nWith exception: {e}")
    return


if __name__ == "__main__":
    #create a custom logger for frontend service
    logger = logging.logger('frontend-service')
    hostname = '0.0.0.0' 
    port = config.frontend_port
    webServer = ThreadedHTTPServer((hostname, port), Handler)
    logger.info("Server started http://%s:%s" % (hostname, port))
    leader_election()
    db_thread = threading.Thread(target=subscribe_to_db_updates, args=())
    db_thread.start()

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    # atexit.register(save_file)
    webServer.server_close()
    db_thread.join()
    logger.warning("Server stopped.")
