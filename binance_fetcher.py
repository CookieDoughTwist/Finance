from binance.client import Client
import time
import datetime
import winsound
import sys
import DataStructures

tol_frac = .012
frequency = 3000
duration = 100

tickers = ['BTCUSDT','XRPBTC','IOTABTC','DASHBTC','XMRBTC']
ticker_idx = [0]*len(tickers)
window_dict = dict()

for sym in tickers:
    window_dict[sym] = DataStructures.CircularQueue(60)

def main():

    if len(sys.argv) < 2:
        show_usd = False
    else:
        show_usd = sys.argv[1]

    client = Client()
    price_array = client.get_all_tickers()
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
            price_array = client.get_all_tickers()
        except:
            continue        
        for tt in range(len(tickers)):      
            cur_price = price_array[ticker_idx[tt]]
            sym = tickers[tt]
            try:                
                price = float(cur_price['price'])            
                window_dict[sym].push(price)                
                cur_mean = window_dict[sym].mean()
                dev_frac = (price-cur_mean)/cur_mean
                if not sym == 'BTCUSDT':
                    if dev_frac > tol_frac:
                        winsound.Beep(frequency, duration)
                        winsound.Beep(2*frequency, duration)
                    elif dev_frac < -tol_frac:
                        winsound.Beep(frequency, duration)
                        winsound.Beep(frequency/2, duration)
            except:
                price = 0
                dev_frac = 0
            if sym == 'BTCUSDT':
                if price > 0:
                    btc_price = price
            else:
                sys.stdout.write("%s: %.8f" % (sym[:-3],price))
                sys.stdout.write("(%.2f%%)" % (dev_frac*100))
                sys.stdout.write(", ")
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

        time.sleep(10)

if __name__ == "__main__":
    main()