import DataManager
import Utilities

class TickerTracker():
    
    def __init__(self):
        self.data = dict()
        self.indicators = dict()        
    
    def initialize_historicals(self,historicals):
        array_dict = Utilities.consolidate_dict_array(historicals)
        self.data.update(array_dict)

class TradeSimulator():
    
    def __init__(self,principal=10000,start_date=None,end_date=None):
        self.cash = principal
        self.holdings = dict()
        self.start_date = start_date
        self.end_date = end_date
                
        self.trackers = dict()
        
    def set_data_source(self,source):
        self.data_source = source
        
    def set_data_fetcher(self,fetcher):
        self.data_fetcher = fetcher
        
    def add_syms(self,syms):        
        self.data_source.add_syms(syms)
        self.data_fetcher.add_syms(syms)
        for sym in syms:
            self.holdings[sym] = 0
            tt = TickerTracker()
            # We initialize the "past" data. Here we load up to the start date.
            historicals = self.data_source.get_range(sym,None,self.start_date)            
            tt.initialize_historicals(historicals)
            self.trackers[sym] = tt            
            
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
        
    def update(self):
        print self.data_fetcher.poll()
        
    def run(self):
        new_data = self.update()
        while not new_data is None:
        

def main():
    ts = TradeSimulator(10000,'2017-06-10','2017-07-20')
    ts.set_data_source(DataManager.DayLoader())
    ts.set_data_fetcher(DataManager.DayPlayer())
    ts.add_syms(['AAPL','GE','ASDFG','VLY.W'])
    ts.run()
    

if __name__ == "__main__":
    main()