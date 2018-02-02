import Robinhood

def set_dynamic_stop_losses(rh,tickers=None):
    if tickers is None:
        print("Feature not yet implemented. Input 'tickers' is required...")
        return
    rl = Robinhood.Robinhood() # Local robinhood for data access
    #rh.print_positions()
    rh.stop_loss('UPRO',1,0)
    rh.limit_sell('UPRO',1,200)
    

def main():
    rh = Robinhood.Robinhood()
    #rh.login('C:/Users/Lucy/Documents/use_pw.txt')
    rh.login('C:/Users/Derek/OneDrive/Documents/use_pw.txt')
    leveraged_tickers = ['SPXL','TQQQ',
    'SOXL','UPRO','KORU','FAS','YINN',
    'CWEB','EDC']
    set_dynamic_stop_losses(rh,leveraged_tickers)
    
    rh.logout()
    
    
    
    
if __name__ == "__main__":
    main()    
        
        