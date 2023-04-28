import os

# Make this variable True while running with Docker, False when running normally on local machine
mode_docker = False

# servers host addresses
if mode_docker:
    frontend_hostname = 'localhost' #os.getenv("FRONTEND_HOST", "localhost")
    catalog_hostname = os.getenv("CATALOG_HOST", "catalog")
    order_hostname = os.getenv("ORDER_HOST", "order")
else:
    frontend_hostname = 'localhost'
    catalog_hostname = 'localhost'
    order_hostname = 'localhost'

# ports on which each service is hosted
frontend_port = 26111
catalog_port = 26119
order_port = 26117

# catalog service threadpool size
catalog_threadpool_size = 25

# order service threadpool size
order_threadpool_size = 25

# probability with which client sends a trade request after sending a lookup request
prob = 0.7

# client sends a trade request with random quantity between 1 and below max_order_quantity
max_order_quantity = 30

# number of lookup and optional trade requests sent from client in a single session 
num_session_requests = 10

# minimum and maximum order service IDs - IDs are expected to be given in sequential order ranging bw min and max
minID = 1
maxID = 3

# port numbers for order service instances - in order from minID to maxID
order_ports = [9721,9722,9723]