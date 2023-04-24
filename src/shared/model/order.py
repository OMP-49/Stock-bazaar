class Order:
    def __init__(self, order_id, stockname, trade_type, quantity):
        self.order_id = order_id
        self.stockname = stockname
        self.trade_type = trade_type
        self.quantity = quantity
    
    def to_string(self):
        '''
        Function to convert the order object to string 
        :return order object attributes in a string form
        '''
        return f'{self.order_id},{self.stockname},{self.trade_type},{self.quantity}'

    def __str__(self):
        return self.to_string()

