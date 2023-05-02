from concurrent import futures

import grpc
import argparse
from threading import Lock
import atexit
import sys
sys.path.append('../../..')
from src import config
from src.shared.proto import stocktrade_pb2
from src.shared.proto import stocktrade_pb2_grpc
from src.shared.util import logging
from src.shared.model import order
import order_service_pb2

# stockorders_db = {}     # stock orders db to store all the stock trade requests
# curr_tran = 0           # current transaction number to keep track of transactions
lock = Lock()           # lock to access the above global variables
# updated_stocks_queue = Queue()             # queue to stream db updates
# leader_id = 0

def serve(hostAddr):
    ''' 
    Funtion that starts order server on the given port and serves incoming requests
    :param hostaddr: the host and port on which the order service is serving requests
    '''
    logger.info(f"Order-service serving on port: {hostAddr}")
    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=config.order_threadpool_size))
    stocktrade_pb2_grpc.add_OrderServiceServicer_to_server(order_service_pb2.OrderService(), server)
    # to connect between 2 machines, keep the server hostname here with port eg: "elnux3.cs.umass.edu:50051"
    server.add_insecure_port(hostAddr)
    server.start()
    syncDBOnStart()
    logger.info(f"Starting server...")
    server.wait_for_termination()


def load_stockorders_db():
    '''
    Function to initilize in-memory database from local disk database
    '''
    
    logger.info("Loading stock orders from local disk database")
    # add the stock objects to db
    global service_id
    order_service_pb2.stockorders_db = {}
    order_service_pb2.curr_tran = 0
    try:
        with open(f'data/stockOrderDB_{service_id}.txt') as file:
            # to skip the first line - first line is header
            file.readline()
            for line in file:
                trans_num,stockname,type,quantity =line.rstrip().split(',')
                trans_num,stockname,type,quantity = int(trans_num.strip()), stockname.strip(), type.strip(), int(quantity.strip())
                order_service_pb2.stockorders_db[trans_num] = order.Order(order_id=trans_num, stockname=stockname, trade_type=type, quantity=quantity)
                order_service_pb2.curr_tran = max(order_service_pb2.curr_tran,trans_num)
        logger.info("Done!")
    except FileNotFoundError as e:
        logger.error(f"DB file is not present, starting server for the first time. File will be created if a trade happens\nException: {e}")
    except Exception as e:
        logger.error(f"cannot read the text, please make sure the formatting in the file is correct\nException: {e}")
    

def dump_to_disk():
    '''
    Function to write back to the local disk database.
    '''
    
    logger.info("Saving data to disk...")
    global service_id
    try:
        # Adding header to the database
        header = ['transaction_number,stockname,ordertype,quantity'] 
        lines = header + [value.to_string() for value in order_service_pb2.stockorders_db.values()]
        with open(f'data/stockOrderDB_{service_id}.txt','w') as file:
            file.write('\n'.join(lines))
        logger.info("Done!")
    except Exception as e:
        logger.error(f"Cannot write to the file.Failed with Exception: {e}")


def syncDBOnStart():
    '''
    Function to find one of the available order services and get data from them after coming from a crash
    '''
    
    logger.info("Syncing database...")
    global service_id

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
                        for orderDBItem in stub.SyncOrderDB(stocktrade_pb2.SyncRequest(max_transaction_number=order_service_pb2.curr_tran)):
                            trade_type_word = 'SELL' if orderDBItem.trade_type == 1 else 'BUY'
                            order_service_pb2.curr_tran = max(order_service_pb2.curr_tran, orderDBItem.transaction_number)
                            order_service_pb2.stockorders_db[orderDBItem.transaction_number] = order.Order(
                                order_id=orderDBItem.transaction_number, stockname=orderDBItem.stockname, trade_type=trade_type_word, quantity=orderDBItem.quantity)
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
        else:
            print("Order service id is either missing or not in bounds, please start service with a valid ID")
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt")
    except Exception as e:
        logger.error(f"Exiting with exception: {e}")

    # calls the funtion to write back to disk when exiting the server
    # atexit.register(dump_to_disk)