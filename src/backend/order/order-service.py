from concurrent import futures

import grpc
import threading
import time
import argparse
from threading import Lock
from queue import Queue
import atexit
import sys
sys.path.append('../../..')
from src import config
from src.shared.proto import stocktrade_pb2
from src.shared.proto import stocktrade_pb2_grpc
from src.shared.util import logging
from src.shared.model import order

stockorders_db = {}     # stock orders db to store all the stock trade requests
curr_tran = 0           # current transaction number to keep track of transactions
lock = Lock()           # lock to access the above global variables
updated_stocks_queue = Queue()             # queue to stream db updates
leader_id = 0

# Implementing Trade method defined in proto file
class OrderService(stocktrade_pb2_grpc.OrderServiceServicer):

    def Trade(self, request, context):
        ''' 
        Funtion to return the transaction status and transaction number for a requested trade order
        :param  request: contains the stockname, trade type and quantity
        :return response: contains the stockname, transaction status and number
        '''
        try:
            name = request.stockname
            type = request.trade_type
            quantity = request.quantity
            typew = 'SELL' if type == 1 else 'BUY'
            logger.info(f'Received Trade request for: {name},{typew},{quantity} on order-service_{service_id}')
    
            hostAddr = config.catalog_hostname + ':' + str(config.catalog_port)
            # sending the trade request to catalog for checking and updating the stockDB at catalog
            with grpc.insecure_channel(hostAddr) as channel:
                stub = stocktrade_pb2_grpc.CatalogServiceStub(channel)
                response = stub.Update(stocktrade_pb2.UpdateRequest(stockname=name, trade_type=type, quantity=quantity ))
                logger.info(f"Trade request: {name},{typew},{quantity}, response: status: {response.status}")
                global updated_stocks_queue
                updated_stocks_queue.put(name)
                # if trade is processed correctly, increase the transaction number and save it to in-memory stockorders_db
                if response.status == 1:
                    with lock:
                        # TODO : write lock
                        global curr_tran
                        global stockorders_db
                        curr_tran = curr_tran + 1
                        stockorders_db[curr_tran] = order.Order(order_id=curr_tran, stockname=name, trade_type=typew, quantity=quantity)
                        write_order_to_file()
                        # TODO: can run replicate_order on seperate thread instead of sequentially
                        replicate_order(curr_tran, name, typew, quantity)
                        return stocktrade_pb2.TradeResponse(stockname=name,status=response.status, transaction_number=curr_tran)
                # if trade is not processed, return status with transaction number -1 to indicate failure.
                return stocktrade_pb2.TradeResponse(stockname=name,status=response.status, transaction_number=-1)
        except Exception as e:
            logger.error(f"Failed to process Trade request in order-service_{service_id} for request : {request}. Failed with exception: {e}")
        return stocktrade_pb2.TradeResponse(stockname=name,status=-1, transaction_number=-1)

    def OrderLookup(self, request, context):
        ''' 
        Funtion to query am existing order. Returns the order id, stockname, type, and quantity of the order
        :param  request:  contains the id of the order to perform lookup on
        :return response: contains the order id, name, type and quantity traded in the order.
        status field is also added in the response. If the order is found, status is set to 1, otherwise -1.
        '''
        try:
            order_id = int(request.order_id)  # id of the order to perform lookup on
            logger.info(f'Received lookup request for order: {order_id} on order service {service_id}')
            # if the order is present in database return name, type, and quantity from db
            global stockorders_db
            if order_id in stockorders_db:
                with lock:
                    # TODO: read lock
                    order_info = stockorders_db[order_id]
                    print(order_info)
                    return stocktrade_pb2.OrderLookupResponse(order_id=1, status= 1, stockname=order_info.stockname,
                             trade_type=order_info.trade_type, quantity=order_info.quantity)
            # if order is not present in database return status as -1
            return stocktrade_pb2.OrderLookupResponse(order_id=order_id, status = -1)
        except Exception as e:
            logger.error(f"Failed to process lookup request for request : {request} with exception: {e}")
            return stocktrade_pb2.LookupResponse(order_id=order_id, status = -1)
    
    def StreamDBUpdates(self, request, context):
        global updated_stocks_queue
        while True:
            if (not updated_stocks_queue.empty()):
                yield stocktrade_pb2.CacheInvalidateRequest(stockname= updated_stocks_queue.get())          

    
    def Save(self, request, context):
        dump_to_disk()
        return stocktrade_pb2.Empty()

    def IsAlive(self, request, context):
        ''' 
        Funtion to check if the service is alive or not from frontend
        :param  request: does not contain any field
        :return response: returns alive response with boolean True
        '''
        return stocktrade_pb2.AliveResponse(is_alive=True)

    def SetLeader(self, request, context):
        ''' 
        Funtion to set elected leader from the leader election 
        :param  request:  contains the id of the elected leader
        :return response: Empty response
        '''
        global leader_id
        leader_id = request.leader_id
        return stocktrade_pb2.Empty()

    def SyncOrderRequest(self, request, context):
        ''' 
        Funtion to sync the latest processed trade request at leader service - stores the order to the local service db
        :param  request:  contains the transaction_number, stockname, trade type and quantity
        '''
        logger.info(f"Sync Order Request: {request.stockname},{request.trade_type},{request.quantity}, transaction_number: {request.transaction_number} at order-service_{service_id}")
        with lock:
            # TODO : write lock
            global curr_tran
            global stockorders_db
            curr_tran = request.transaction_number
            stockorders_db[curr_tran] = order.Order(order_id=curr_tran, stockname=request.stockname, trade_type=request.trade_type, quantity=request.quantity)
            write_order_to_file()
        return stocktrade_pb2.Empty()

    def SyncOrderDB(self, request, context):
        ''' 
        Funtion to sync DB data with a service that just came from crash/started
        :param  request:  contains the maximum transaction id at the restarted service
        :return response: stream of order database item containing order details
        '''
        global stockorders_db
        for k,order_info in stockorders_db.items():
            if k > request.max_transaction_number:
                yield stocktrade_pb2.OrderDBItem(
                    stockname=order_info.stockname, trade_type=order_info.trade_type, quantity=order_info.quantity, transaction_number=order_info.transaction_number)


def replicate_order(transaction_number, stockname, trade_type, quantity):
    '''
    Function to send the latest successful trade order to the replica order services to maintain data sync
    '''
    global service_id
    for i in range(len(config.order_ports)):
        if i == service_id-1:
            continue
        hostAddr = config.order_hostname + ':' + str(config.order_ports[i])
        logger.info(f"Sending SyncOrderRequest to the order service replica at {hostAddr}, orderId = {transaction_number}")
        try:
            with grpc.insecure_channel(hostAddr) as channel:
                stub = stocktrade_pb2_grpc.OrderServiceStub(channel)
                sync_response = stub.SyncOrderRequest(stocktrade_pb2.OrderDBItem(stockname=stockname, quantity=quantity, trade_type=trade_type, transaction_number=transaction_number))
        except Exception as e:
            logger.error(f"Failed to sync transaction with service replica at {hostAddr}, orderId= {transaction_number}\nWith exception: {e}")
    return



def serve(hostAddr):
    ''' 
    Funtion that starts order server on the given port and serves incoming requests
    :param hostaddr: the host and port on which the order service is serving requests
    '''
    logger.info(f"Order-service serving on port: {hostAddr}")
    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=config.order_threadpool_size))
    stocktrade_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    # to connect between 2 machines, keep the server hostname here with port eg: "elnux3.cs.umass.edu:50051"
    server.add_insecure_port(hostAddr)
    server.start()
    server.wait_for_termination()


def load_stockorders_db():
    '''
    Function to initilize in-memory database from local disk database
    '''
    
    logger.info("Loading stock orders from local disk database")
    # add the stock objects to db
    global stockorders_db
    global curr_tran
    global service_id
    stockorders_db = {}
    curr_tran = 0
    try:
        with open(f'data/stockOrderDB_{service_id}.txt') as file:
            # to skip the first line - first line is header
            file.readline()
            for line in file:
                trans_num,stockname,type,quantity =line.rstrip().split(',')
                trans_num,stockname,type,quantity = int(trans_num.strip()), stockname.strip(), type.strip(), int(quantity.strip())
                stockorders_db[trans_num] = order.Order(order_id=trans_num, stockname=stockname, trade_type=type, quantity=quantity)
                curr_tran = max(curr_tran,trans_num)
        logger.info("Done!")
    except FileNotFoundError as e:
        logger.error(f"DB file is not present, starting server for the first time. File will be created if a trade happens\nException: {e}")
    except Exception as e:
        logger.error(f"cannot read the text, please make sure the formatting in the file is correct\nException: {e}")
    

def write_order_to_file():
    '''
    Function to write the last processed order to the local disk database.
    '''
    
    print("Saving order to disk", end='...')
    global stockorders_db
    global curr_tran
    global service_id
    try:
        # Adding header to the database
        if curr_tran == 1:
            dbwithheader = ['transaction_number,stockname,ordertype,quantity', stockorders_db[curr_tran].to_string()]
            with open(f'data/stockOrderDB_{service_id}.txt','w') as file:
                file.write('\n'.join(dbwithheader))
        else:
            line = '\n' + stockorders_db[curr_tran].to_string()
            with open(f'data/stockOrderDB_{service_id}.txt','a') as file:
                file.write(line)
        print("Done!")
    except Exception as e:
        print(f"Cannot write to the file. Failed with Exception: {e}")
    


def dump_to_disk():
    '''
    Function to write back to the local disk database.
    '''
    
    logger.info("Saving data to disk...")
    global stockorders_db
    global service_id
    try:
        # Adding header to the database
        header = ['transaction_number,stockname,ordertype,quantity'] 
        lines = header + [value.to_string() for value in stockorders_db.values()]
        with open(f'data/stockOrderDB_{service_id}.txt','w') as file:
            file.write('\n'.join(lines))
        logger.info("Done!")
    except Exception as e:
        logger.error(f"Cannot write to the file.Failed with Exception: {e}")


def syncDataBase():
    '''
    Function to find one of the available order services and get data from them after coming from a crash
    '''
    
    logger.info("Syncing database...")
    global curr_tran
    global service_id
    global stockorders_db

    for i in range(len(config.order_ports)-1, -1,-1):
        if i == service_id-1:
            continue
        try:
            hostAddr = config.order_hostname + ':' + str(config.order_ports[i])
            logger.info(f"Sending IsAlive to the order service instance at {hostAddr}")
            with grpc.insecure_channel(hostAddr) as channel:
                stub = stocktrade_pb2_grpc.OrderServiceStub(channel)
                alive_response = stub.IsAlive(stocktrade_pb2.Empty())
                if alive_response.is_alive:
                    logger.info(f"Syncing data from the order service instance at {hostAddr}")
                    with lock:
                        for orderDBItem in stub.SyncOrderDB(stocktrade_pb2.SyncRequest(max_transaction_number=curr_tran)):
                            typew = 'SELL' if orderDBItem.trade_type == 1 else 'BUY'
                            stockorders_db[orderDBItem.transaction_number] = order.Order(
                                order_id=orderDBItem.transaction_number, stockname=orderDBItem.stockname, trade_type=typew, quantity=orderDBItem.quantity)
                    # TODO: should we keep dump to disk in the lock or not
                    dump_to_disk()
                    break
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                logger.error(f"Order service instance at {hostAddr} is not alive/unavailable")
            else:
                logger.error(f" Failed to connect the Order service instance at {hostAddr}\nException: {rpc_error}")
        except Exception as e:
            logger.error(f" Failed to connect the Order service instance at {hostAddr}\nException: {e}")
    return


def getHostAddr():
    # returns the host address for the order service based on its service_id
    global service_id
    if service_id >= config.minID and service_id <= config.maxID:
        return config.order_hostname + ':' + str(config.order_ports[service_id-1])
    else:
        print("Invalid order service id number")
        return ""

if __name__ == '__main__':
    try:
        logger = logging.logger('order-service')
        # command line arguments for reading ID number of a order server instance
        parser = argparse.ArgumentParser(description='OrderService')
        parser.add_argument('-id', type=int, default=-1, help='input order service id for this instance')
        args = parser.parse_args()
        if args.id >= config.minID  and args.id <= config.maxID:
            global service_id
            service_id = args.id    
            # initialize database
            load_stockorders_db()
            # start the server on hostAddr to receive requests
            hostAddr = getHostAddr()
            serve(hostAddr)
            syncDataBase()
        else:
            print("Order service id is either missing or not in bounds, please start service with a valid ID")
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt")
    except Exception as e:
        logger.error(f"Exiting with exception: {e}")

    # calls the funtion to write back to disk when exiting the server
    atexit.register(dump_to_disk)