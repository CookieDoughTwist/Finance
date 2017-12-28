import sys
import time
import requests
import Queue
import winsound
import numpy as np

import DataStructures
import Robinhood
import Utilities

class RobinhoodTrader:

    active = False
    period = 1 # seconds

    def __init__(self,login_path,log_loc='.'):
        self.login_path = login_path
        self.log_loc = log_loc
        self.rb = Robinhood.Robinhood()
        self.login()
        self.trackers = dict()
        self.session = requests.session()
    
    def login(self):
        f = open(self.login_path,'r')
        us = f.readline().strip()
        pw = f.readline().strip()
        f.close()
        self.active = self.rb.login(us,pw)        
          
    def load(self):
        self.rb.load_trackers(self.trackers)
        for key in self.trackers:            
            sys.stdout.write("%s: %d\n" % (key,self.trackers[key].quantity))
        
    #def load_active_orders(self):        
        #orders = self.rb.list_orders()
        #for order in orders:
            #print order.state        
            
    def update(self):      
        start = time.time()
        #self.rb.order_history('2017-12-08')
        #listoforders = self.rb.list_orders() #all the orders recent to old
        #print self.rb.order_details(listoforders[len(listoforders)-1])['instrument'].json()['symbol']
        #firstorder = Robinhood.Order(listoforders[0]) #most recent order
        #firstorder.id
        #print self.rb.list_order_details()
        #print self.rb.order_status(firstorder) #prints "cancelled" etc
        #self.load_active_orders()        
        #print self.trackers
        
        end = time.time()
        sys.stdout.write("Update time: %f\n" % (end - start))
        sys.stdout.flush()



        
class Trader:
    
    cash = 10000
    
    def __init__(self):
        self.syms = list()
        self.windows = dict()
        self.windows_open = dict()
        self.holdings = dict()
        
    def assign_data_source(self,data_source):
        self.data_source = data_source
        
    def add_syms(self,syms):
        self.syms += syms
        self.data_source.add_syms(syms)
        for sym in syms:
            self.windows[sym] = DataStructures.CircularQueue(50)
            self.windows_open[sym] = DataStructures.CircularQueue(10)
            self.holdings[sym] = 0
    
    def buy(self,sym,num,price):
        cost = num*price
        if cost <= self.cash:
            self.holdings[sym] += num
            self.cash -= cost
            return True
        return False
        
    def sell(self,sym,num,price):
        if self.holdings[sym] >= num:
            cost = num*price
            self.cash += cost
            self.holdings[sym] -= num
            return True
        return False

    def buy_dollar(self,sym,dollars,price):
        num = int(dollars / price)
        if num < 1:            
            return False
        return self.buy(sym,num,price)
        
    def sell_dollar(self,sym,dollars,price):
        num = int(dollars / price)
        if num < 1:
            return False
        return self.sell(sym,num,price)
            
    def current_value(self):
        output = self.cash
        for sym in self.syms:
            output += self.holdings[sym] * self.windows[sym].last()
        return output
    
    def run(self):
        buy_unit = 1000
        start_value = self.cash
        sys.stdout.write("Starting value: $%.2f\n"%start_value)
        arr = self.data_source.poll()
        n_idx = 0
        while arr is not None:
            closings = arr[0]
            openings = arr[1]
            for idx in range(len(self.syms)):
                sym = self.syms[idx]             
                self.windows[sym].push(closings[idx])
                self.windows_open[sym].push(openings[idx])
            for sym in self.syms:
                window = self.windows[sym]
                mm = window.mean()
                cur_price = window.last()
                if n_idx == 0:
                    self.buy_dollar(sym,start_value/2/len(self.syms),cur_price)                    
                frac = (cur_price-mm)/cur_price
                if frac > .03:
                    self.sell_dollar(sym,3*buy_unit,cur_price)
                elif frac > .02:
                    self.sell_dollar(sym,2*buy_unit,cur_price)
                elif frac > .01:
                    self.sell_dollar(sym,1*buy_unit,cur_price)
                elif frac < -.03:
                    self.buy_dollar(sym,3*buy_unit,cur_price)
                elif frac < -.02:
                    self.buy_dollar(sym,2*buy_unit,cur_price)
                elif frac < -.01:
                    self.buy_dollar(sym,1*buy_unit,cur_price)            
                
            #value_ratio = self.current_value()/start_value   
            #aug_ratio = 2*(value_ratio-1)+value_ratio
            #winsound.Beep(int(2500*aug_ratio),25)    
            self.print_portfolio()
            arr = self.data_source.poll()
            n_idx += 1
            
        print self.current_value()
        
    def print_portfolio(self):
        sys.stdout.write("Value: $%.02f Cash: $%.02f; Holdings: "%(self.current_value(),self.cash))
        for sym in self.syms:
            sys.stdout.write("%s(%d), "%(sym,self.holdings[sym]))            
        sys.stdout.write("\b\b \n")

class TickerTracker:
    
    def __init__(self):
        self.SMAs = dict() # simple moving averages
        
    def initialize_historicals(self,historicals):
        window_intervals = [5,10,25,50,100]        
        closings = map(float,historicals['close_price'])        
        for val in window_intervals:
            tag = str(val) + 'day'
            self.SMAs[tag] = np.mean(closings[-val:])        
            
    def initialize_daily(self,historicals):
        print historicals
      
class DayTrader():
    
    def __init__(self):
        self.trackers = dict()
        
    def set_fetcher(self,fetcher):
        self.fetcher = fetcher
        
    def add_syms(self,syms):
        h_day = self.fetcher.get_historical_prices(syms,'day')
        h_5minute = self.fetcher.get_historical_prices(syms,'5minute')
        #print self.fetcher.get
        for idx in range(len(syms)):
            sym = syms[idx]                        
            cur_h_day = h_day[idx]
            cur_h_5minute = h_5minute[idx]
            h_day_dict = Utilities.consolidate_dict_array(cur_h_day['historicals'])            
            h_5minute_dict = Utilities.consolidate_dict_array(cur_h_5minute['historicals'])            
            tracker = TickerTracker()
            tracker.initialize_historicals(h_day_dict)
            tracker.initialize_daily(h_5minute_dict)
            self.trackers[sym] = tracker
            
        
        
def test_DayTrader():
    dt = DayTrader()
    dt.set_fetcher(Robinhood.RobinhoodFetcher())
    dt.add_syms(['AAPL','TSLA'])
    
def test_RobinhoodTrader():
    sys.stdout.write("Hajimeyou!\n")
    sys.stdout.flush()
    
    login_path = ''
    if len(sys.argv) > 1:
        login_path = sys.argv[1]
    
    td = RobinhoodTrader(login_path)
    td.load(['SPY','SPYG','SPYD','SPHD'])
    #td.load_active_orders()
    
    td.update()
    #while True:
        #td.update()
        #time.sleep(td.period)

    
def test_Trader():
    syms = ['AAPL','TSLA']
    #syms = ['SPY']
    td = Trader()
    td.assign_data_source(Robinhood.RobinhoodPlayer())
    td.add_syms(syms)
    td.run()
    
        
def main():
    #test_Trader()
    test_DayTrader()


if __name__ == "__main__":
    main()
    
    
    
    
    