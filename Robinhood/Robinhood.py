import sys
import requests

URL_DICT = {
    "login": "https://api.robinhood.com/api-token-auth/",
    "logout": "https://api.robinhood.com/api-token-logout/",
    "investment_profile": "https://api.robinhood.com/user/investment_profile/",
    "accounts": "https://api.robinhood.com/accounts/",
    "ach_iav_auth": "https://api.robinhood.com/ach/iav/auth/",
    "ach_relationships": "https://api.robinhood.com/ach/relationships/",
    "ach_transfers": "https://api.robinhood.com/ach/transfers/",
    "applications": "https://api.robinhood.com/applications/",
    "dividends": "https://api.robinhood.com/dividends/",
    "edocuments": "https://api.robinhood.com/documents/",
    "instruments": "https://api.robinhood.com/instruments/",
    "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
    "markets": "https://api.robinhood.com/markets/",
    "notifications": "https://api.robinhood.com/notifications/",
    "orders": "https://api.robinhood.com/orders/",
    "password_reset": "https://api.robinhood.com/password_reset/request/",
    "portfolios": "https://api.robinhood.com/portfolios/",
    "positions": "https://api.robinhood.com/positions/",
    "quotes": "https://api.robinhood.com/quotes/",
    "historicals": "https://api.robinhood.com/quotes/historicals/",
    "document_requests": "https://api.robinhood.com/upload/document_requests/",
    "user": "https://api.robinhood.com/user/",
    "watchlists": "https://api.robinhood.com/watchlists/",
    "news": "https://api.robinhood.com/midlands/news/",
    "fundamentals": "https://api.robinhood.com/fundamentals/",
}
        
class Robinhood:

    header_dict = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "X-Robinhood-API-Version": "1.0.0",
        "Connection": "keep-alive",
        "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
    }
    
    def __init__(self):
        self.session = requests.session()
        self.session.headers = self.header_dict  
        
    def login(self,username,password=None):
        """ Login with username and password inputs 
            Interprets first argument as path to credentials
            if only ones input is passed.
        """
        
        if password is None:
            with open(username,'r') as f:
                u = f.readline()
                p = f.readline()                
                payload = {
                    'username': u,
                    'password': p
                }                
        else:
            payload = {
                'username': username,
                'password': password
            }      
        try:
            res = self.session.post(URL_DICT['login'], data=payload)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.HTTPError:
            sys.stdout.write("Login error!\n")
        if 'token' in data.keys():
            self.session.headers['Authorization'] = 'Token ' + data['token']            
            return True
        return False
        
    def logout(self):
        """ Log out of current session """
        try:
            req = self.session.post(URL_DICT['logout'])
            req.raise_for_status()
        except:
            sys.stdout.write("Logout error!\n")
        return req
    
    def get_account(self,type=None):
        """ Fetch account information """
        res = self.session.get(URL_DICT['accounts'])
        res.raise_for_status()  #auth required
        res = res.json()
        if type is None:
            return res['results'][0]
        else:
            return res['results'][0][type]
        
    def investment_profile(self):
        """ Fetch investment_profile """
        res = self.session.get(URL_DICT['investment_profile'])
        res.raise_for_status()  #will throw without auth
        data = res.json()
        return data
                
    def positions(self):
        return self.session.get(URL_DICT['positions']).json()

    def securities_owned(self):
        return self.session.get(URL_DICT['positions']+'?nonzero=true').json()
    
    def portfolios(self,type=None):
        """ type = 'adjusted_equity_previous_close' / 'equity' / 'equity_previous_close' /
                   'excess_margin' / 'extended_hours_equity' / 'extended_hours_market_value' /
                   'last_core_equity' / 'last_core_market_value' / 'market_value' """
        req = self.session.get(URL_DICT['portfolios'])
        req.raise_for_status()
        if type is None:
            return req.json()['results'][0]
        else:
            return req.json()['results'][0][type]
    
    def order_history(self,date=None,sym=None):
        payload = dict()
        if date is not None:
            payload['updated_at'] = date # ex: date = '2017-08-15'
        if sym is not None:
            instrument = self.instruments(sym)[0]
            payload['instrument'] = instrument['url']        
        return self.session.get(URL_DICT['orders'],data=payload).json()

    def list_order_ids(self):
        ''' returns a list of all order_IDs, ordered from newest to oldest '''
        res = self.session.get(URL_DICT['orders'])
        if res.status_code == 200:
            orders = []
            for i in res.json()['results']:
                URL = i['url']
                orders.append(URL[URL.index("orders")+7:-1])
            return orders
        else:
            raise Exception("Could not retrieve orders: " + res.text)
    
    def order_details(self, order_ID):
        ''' Returns an order object which contains information about an order 
        and its status'''
        res = self.session.get(URL_DICT['orders'] + order_ID + "/")
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception("Could not get order status: " + res.text)
    
    def order_status(self, order_ID):
        ''' Returns an order status string'''
        return self.order_details(order_ID)['state']
    
    def list_order_details(self):
        ''' Generates a dictionary where keys are order_IDs and values are 
        order objects. '''
        detailed_orders = {}
        for i in self.list_order_ids():
            order = self.order_details(i)
            order['symbol'] = self.session.get(order['instrument']).json()['symbol']
            detailed_orders[i] = order
        return detailed_orders
    
    def cancel_order(self, order_ID):
        ''' Cancels order with order_ID'''
        res = self.session.post(URL_DICT['orders'] + order_ID + "/cancel/")
        if res.status_code == 200:
            return res
        else:
            raise Exception("Could not cancel order: " + res.text)
    
    def cancel_stop_orders(self):
        """ Clears all stop orders 
            TODO: Doesn't work if more than 100 orders back"""
        ids = self.list_order_ids()
        for id in ids:
            order = self.order_details(id)
            if order['state'] == 'queued' and order['trigger'] == 'stop':
                self.cancel_order(id)
        
    
    def place_order(self,instrument,quantity=1,bid_price=0.0,transaction=None,
                    trigger='immediate',order='market',time_in_force = 'gfd'):        
        """ Place an order with Robinhood """
        if not bid_price:
            bid_price = self.get_price(instrument['symbol'],'bid_price')      
        payload = {
            'account': self.get_account()['url'],
            'instrument': instrument['url'],
            'quantity': quantity,
            'side': transaction,
            'symbol': instrument['symbol'],
            'time_in_force': time_in_force.lower(),
            'trigger': trigger,
            'type': order.lower()            
        }
        if trigger == 'stop':
            payload['stop_price'] = float(bid_price)
        else:
            payload['price'] = float(bid_price)
        res = self.session.post(URL_DICT['orders'],data=payload)
        res.raise_for_status()                          
        return res
        
    def limit_buy(self,sym,quantity=1,bid_price=0.0):
        instrument = self.instruments(sym)[0]
        return self.place_order(instrument, quantity, bid_price, 'buy', 'immediate', 'limit')        
        
    def limit_sell(self,sym,quantity=1,bid_price=0.0):
        instrument = self.instruments(sym)[0]
        return self.place_order(instrument, quantity, bid_price, 'sell', 'immediate', 'limit')                    
        
    def buy(self,sym,quantity):
        instrument = self.instruments(sym)[0]
        return self.place_order(instrument, quantity, 0.0, 'buy')
        
    def sell(self,sym,quantity):
        instrument = self.instruments(sym)[0]
        return self.place_order(instrument, quantity, 0.0, 'sell')
      
    def stop_loss(self,sym,quantity=1,bid_price=0.0):
        instrument = self.instruments(sym)[0]
        return self.place_order(instrument, quantity, bid_price, 'sell', 'stop', 'market')                     
        
    def print_positions(self):
        pos = self.positions()
        next = pos['next']
        if next is not None:
            sys.stdout.write("Next has something!\n")
            return
        results = pos['results']
        for res in results:
            quantity = float(res['quantity'])
            if quantity > 0:            
                symbol = self.session.get(res['instrument']).json()['symbol']
                sys.stdout.write("%s: %d\n" % (symbol,quantity))
    
    def print_open_orders(self):
        ids = self.list_order_ids()
        for id in ids:
            order = self.order_details(id)
            if order['state'] == 'queued':
                sym = self.session.get(order['instrument']).json()['symbol']
                print sym
                print order
      
    """
    Functions that do not require a logged in session.
    """
    
    def instruments(self, stock):
        """ Fetches instruments for specified stock """
        res = self.session.get(URL_DICT['instruments'], params={'query': stock.upper()})
        res.raise_for_status()
        res = res.json()
        # if requesting all, return entire object so may paginate with ['next']
        if (stock == ""):
            return res
        return res['results']
        
    def get_price(self,sym,type='last_trade_price'):
        """ type = 'last_trade_price' / 'ask_price' / 'bid_price' """
        url = URL_DICT['quotes'] + sym + '/'
        try:
            response = requests.get(url).json()
            price = round(float(response[type]), 2)
            return price
        except:
            return None  
    
    def get_historical(self,sym,interval='day'):
        url = URL_DICT['historicals'] + sym + '/' + '?interval=' + interval
        try:
            response = requests.get(url).json()
            return response
        except:
            return None
      
def main():
    print "cheese"
    
if __name__ == "__main__":
    main()    
        
        
        