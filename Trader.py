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
        #results = self.rb.securities_owned()['results']
        #for holding in results:
            #instrument = self.rb.raise_session(holding['instrument'])            
            #tracker = TickerTracker(instrument['symbol'],instrument)
            #tracker.load(
            #self.trackers[tracker.sym] = tracker
        
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
        self.load()
        #print self.trackers
        
        end = time.time()
        sys.stdout.write("Update time: %f\n" % (end - start))
        sys.stdout.flush()
        

def main():
    sys.stdout.write("Hajimeyou!\n")
    sys.stdout.flush()
    
    login_path = ''
    if len(sys.argv) > 1:
        login_path = sys.argv[1]
    
    td = RobinhoodTrader(login_path)
    #td.load(['AAPL','TSLA','F'])
    #td.load_active_orders()
    
    td.update()
    #while True:
        #td.update()
        #time.sleep(td.period)


if __name__ == "__main__":
    main()
    
    
    
    
    