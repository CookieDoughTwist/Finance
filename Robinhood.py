import sys
import requests
import urllib

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
        
    def login(self,username,password):
        """ Login with username and password inputs """
        payload = {
            'password': password,
            'username': username
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
        try:
            req = self.session.post(URL_DICT['logout'])
            req.raise_for_status()
        except:
            sys.stdout.write("Logout error!\n")
        return req
        
    def get_account(self):
        """ Fetch account information """
        res = self.session.get(URL_DICT['accounts'])
        res.raise_for_status()  #auth required
        res = res.json()
        return res['results'][0]
        
    def investment_profile(self):
        """ Fetch investment_profile """
        res = self.session.get(URL_DICT['investment_profile'])
        res.raise_for_status()  #will throw without auth
        data = res.json()
        return data
        
    def instruments(self, stock):
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
    
    def place_order(self,instrument,quantity=1,bid_price=0.0,transaction=None,
                    trigger='immediate',order='market',time_in_force = 'gfd'):        
        """ Place an order with Robinhood """
        if not bid_price:
            bid_price = self.get_price(instrument['symbol'],'bid_price')        
        payload = {
            'account': self.get_account()['url'],
            'instrument': instrument['url'],
            'price': float(bid_price),
            'quantity': quantity,
            'side': transaction,
            'symbol': instrument['symbol'],
            'time_in_force': time_in_force.lower(),
            'trigger': trigger,
            'type': order.lower()
        }
        tries = 0
        while tries < 3:
            try:
                res = self.session.post(URL_DICT['orders'],data=payload)
                res.raise_for_status()
                break
            except:
                sys.stdout.write("Order placement failed!\n")
                tries += 1                            
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
        
def main():
    print "cheese"
    
if __name__ == "__main__":
    main()    
        
        
        