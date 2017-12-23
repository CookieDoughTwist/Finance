import sys
import time
import requests
import Queue


import DataStructures
import Robinhood


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
        self.holdings = dict()
        
    def assign_data_source(self,data_source):
        self.data_source = data_source
        
    def add_syms(self,syms):
        self.syms += syms
        self.data_source.add_syms(syms)
        for sym in syms:
            self.windows[sym] = DataStructures.CircularQueue(10)
            self.holdings[sym] = 0
    
    def buy(self,sym,num,price):
        cost = num*price
        if cost <= self.cash:
            self.holdings[sym] += num
            self.cash -= cost
        
    def sell(self,sym,num,price):
        if self.holdings[sym] >= num:
            cost = num*price
            self.cash += cost
            self.holdings[sym] -= num

    #def buy_dollar(self,sym,dollar):
        
            
    def current_value(self):
        output = self.cash
        for sym in self.syms:
            output += self.holdings[sym] * self.windows[sym].last()
        return output
    
    def run(self):        
        arr = self.data_source.poll()
        while arr is not None:
            for idx in range(len(self.syms)):
                sym = self.syms[idx]
                self.windows[sym].push(arr[idx])                
            for sym in self.syms:
                window = self.windows[sym]
                mm = window.mean()
                cur = window.last()
                frac = (cur-mm)/cur
                if frac > .01:
                    self.sell(sym,1,cur)
                elif frac < -.01:
                    self.buy(sym,1,cur)
                
            arr = self.data_source.poll()
            print self.current_value()
        
    
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
    td = Trader()
    td.assign_data_source(Robinhood.RobinhoodPlayer())
    td.add_syms(syms)
    td.run()
    
        
def main():
    test_Trader()


if __name__ == "__main__":
    main()
    
    
    
    
    