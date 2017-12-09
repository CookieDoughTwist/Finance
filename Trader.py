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
    
    def login(self):
        f = open(self.login_path,'r')
        us = f.readline().strip()
        pw = f.readline().strip()
        f.close()
        self.active = self.rb.login(us,pw)        
    
        
    def update(self):
        print self.rb.get_price('AAPL')
        self.rb.limit_sell('AAPL',10,1000.2)
        sys.stdout.flush()

def main():
    sys.stdout.write("Hajimeyou!\n")
    sys.stdout.flush()
    
    login_path = ''
    if len(sys.argv) > 1:
        login_path = sys.argv[1]
    
    td = RobinhoodTrader(login_path)
    td.update()
    #while True:
        #td.update()
        #time.sleep(td.period)


if __name__ == "__main__":
    main()
    
    
    
    
    