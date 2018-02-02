import Robinhood

def set_dynamic_stop_losses(rh,tickers=None):
    if tickers is None:
        print("Feature not yet implemented. Input 'tickers' is required...")
        return
    rl = Robinhood.Robinhood() # Local robinhood for data access
    
    rh.print_positions()


def main():
    rh = Robinhood.Robinhood()
    rh.login('C:/Users/Lucy/Documents/use_pw.txt')
    leveraged_tickers = ['SPXL','TQQQ',
    'SOXL','UPRO','KORU','FAS','YINN',
    'CWEB','EDC']
    set_dynamic_stop_losses(rh,leveraged_tickers)
    
    rh.logout()
    
    
    
    
if __name__ == "__main__":
    main()    
        
        