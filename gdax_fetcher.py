from datetime import datetime, timedelta

import requests
import time
import datetime
import winsound
import sys
import DataStructures


crypto_symbols = ('BTC','ETH','LTC')
warning_tolerance = (10000,400,90)
tol_frac = .009
frequency = 2500
duration = 1000
tol_dict = dict(zip(crypto_symbols,warning_tolerance))
sys.stdout.write("%s\n\n" % tol_dict)
url_dict = dict()
window_dict = dict()


for sym in crypto_symbols:
    url_dict[sym] = 'https://api.gdax.com/products/%s-USD/ticker' % sym
    window_dict[sym] = DataStructures.CircularQueue(60)
    


def main():
    while True:
        sys.stdout.write("%s     " % datetime.datetime.now())
        for sym in crypto_symbols:         
            url = url_dict[sym]
            # Query CoinDesk Current price API                       
            try:
                response = requests.get(url).json() 
                price = round(float(response['bid']), 2)                
                window_dict[sym].push(price)                
                cur_mean = window_dict[sym].mean()
                dev_frac = (price-cur_mean)/cur_mean
                if price < tol_dict[sym] or dev_frac > tol_frac or dev_frac < -tol_frac:
                    winsound.Beep(frequency, duration)
            except:
                price = 0
                dev_frac = 0
            
            sys.stdout.write("%s: $%.2f" % (sym,price))
            sys.stdout.write("(%.2f%%)" % (dev_frac*100))
            sys.stdout.write(", ")
        sys.stdout.write("\n");
        sys.stdout.flush()

        time.sleep(10)

if __name__ == "__main__":
    main()