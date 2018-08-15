
import time
import datetime
import winsound
import sys
import requests
import DataStructures

tol_frac = .015     # Tolerance fraction: the deviance from the window mean to cause response
window_size = 60    # Window size: number of stored values in the window
update_period = 10  # Update period: how long to wait between updates in seconds

# For example, with window_size = 60 and update_period = 10, 
# the window would provide the 10 minute (60*10sec=10min) sliding average.
# For tol_frac = .01, there will be a response if the current price is 0.01% greater
# than the sliding mean or 1% less than the sliding mean. The beeps played will ring
# up or ring down depending on this. It has been set this way for illustrative purposes.
# The tol_frac values would probably be want to be around .01 for a 10 minute window.

frequency = 3000
duration = 100

# The BTCUDT ticker must always be here for the fiat conversion to work.
#tickers = ['BTCUSDT','XRPBTC','IOTABTC','DASHBTC','XMRBTC']
#tickers = ['BTCUSDT','XRPBTC','XLMBTC','TRXBTC','BNBBTC']
#tickers = ['BTCUSDT','XRPBTC','BNBBTC','IOTABTC','XMRBTC']
#tickers = ['BTCUSDT','XRPBTC','BNBBTC','IOTABTC','XLMBTC']
#tickers = ['BTCUSDT','XRPBTC','BNBBTC','IOTABTC','XLMBTC','XMRBTC']
#tickers = ['BTCUSDT','ADABTC','BATBTC','BNBBTC','ETHBTC','GASBTC','IOTABTC','MODBTC','NANOBTC','NEOBTC','OMGBTC','REQBTC','STRATBTC','VENBTC','XLMBTC','XMRBTC','XRPBTC']
tickers = ['BTCUSDT','ADABTC','BNBBTC','ETHBTC','GASBTC','IOTABTC','MODBTC','NANOBTC','NEOBTC','OMGBTC','REQBTC','STRATBTC','VENBTC','XLMBTC','XMRBTC','XRPBTC']
ticker_idx = [0]*len(tickers)
window_dict = dict()

uri = 'https://api.binance.com/api/v1/ticker/allPrices'

for sym in tickers:
    window_dict[sym] = DataStructures.CircularQueue(window_size)

def main():

    if len(sys.argv) < 2:
        show_usd = False
    else:
        show_usd = sys.argv[1]

    price_array = requests.get(uri).json()    
    
    for idx in range(len(price_array)):
        cur_price = price_array[idx]      
        for tt in range(len(tickers)):        
            if cur_price['symbol'] == tickers[tt]:
                ticker_idx[tt] = idx
                break
                
    btc_price = price_array[ticker_idx[0]]['price']   

    while True:        
        sys.stdout.write("%s - " % datetime.datetime.now())        
        try:
            price_array = requests.get(uri).json()
        except:
            continue        
        for tt in range(len(tickers)):      
            cur_price = price_array[ticker_idx[tt]]
            sym = tickers[tt]
            gain = False
            loss = False
            try:     
                price = float(cur_price['price'])            
                window_dict[sym].push(price)                
                cur_mean = window_dict[sym].mean()
                dev_frac = (price-cur_mean)/cur_mean
                if not sym == 'BTCUSDT':
                    if dev_frac > tol_frac:
                        gain = True
                        winsound.Beep(frequency, duration)
                        winsound.Beep(3*frequency/2, duration)
                        if dev_frac > 2*tol_frac:
                            winsound.Beep(2*frequency, duration)
                    elif dev_frac < -tol_frac:
                        loss = True
                        winsound.Beep(frequency, duration)
                        winsound.Beep(2*frequency/3, duration)
                        if dev_frac < -2*tol_frac:
                            winsound.Beep(frequency/2, duration)
            except:
                price = 0
                dev_frac = 0
            if sym == 'BTCUSDT':
                if price > 0:
                    btc_price = price
            else:
                if gain:
                    sys.stdout.write("\033[0;32m") # Green
                elif loss:
                    sys.stdout.write("\033[1;31m") # Red
                sys.stdout.write("%s: %.8f" % (sym[:-3],price))
                sys.stdout.write("(%.2f%%)" % (dev_frac*100))
                sys.stdout.write("\033[0;0m") # Reset color
                sys.stdout.write(", ")
            if tt % 5 == 0:
                sys.stdout.write("\n")
        sys.stdout.write("\b\b \n")
        if show_usd:
            sys.stdout.write(" " * 34)
            for tt in range(len(tickers)):
                sym = tickers[tt]
                if sym == 'BTCUSDT':
                    continue
                price_usd = btc_price * window_dict[sym].last()
                sys.stdout.write("$%.4f" % price_usd)
                if tt < len(tickers)-1:
                    sys.stdout.write(" " * 19)
            sys.stdout.write("\n");
                
        sys.stdout.flush()

        time.sleep(update_period)

if __name__ == "__main__":
    main()