import Robinhood

def set_dynamic_stop_losses(rh,tickers):
    rl = Robinhood.Robinhood()
    


def main():
    rh = Robinhood.Robinhood()
    leveraged_tickers = ['SPXL','TQQQ',
    'SOXL','UPRO','KORU','FAS','YINN',
    'CWEB','EDC']
    set_dynamic_stop_losses(rh,leveraged_tickers)
    
if __name__ == "__main__":
    main()    
        
        
        