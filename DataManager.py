import os
import sys
import requests
import json
import time
from ftplib import FTP
from StringIO import StringIO

HIST_URL = 'https://api.robinhood.com/quotes/historicals/%s/?interval=%s'
NASDAQ_TRADED_URL = 'ftp.nasdaqtrader.com'
DATA_DIR = 'C:/Users/Lucy/Documents/Finance/Data/Daily5minute'

def get_5minute_data(syms,date,dir=DATA_DIR):
    historicals = list()
    for sym in syms:
        ticker_path = dir + '/' + sym
        if sym == 'PRN':
            ticker_path += '+'
        if not os.path.exists(ticker_path):
            historicals.append(None)
            sys.stdout.write("Ticker %s not in the database...\n"%sym)
            continue
        date_file = ticker_path + '/' + date
        if not os.path.isfile(date_file):
            historicals.append(None)
            sys.stdout.write("Date %s for ticker %s not in the database...\n"%(date,sym))
            continue
        with open(date_file,'r') as f:
            res = f.read()        
        response = json.loads(res)
        historicals.append(response)        
    return historicals

def save_day_5minute_data(syms,overwrite=False,dir=DATA_DIR):
    t_start = time.clock()
    sys.stdout.write("Pulling and saving 5 minute resolution data:\n\n")
    failures = list()
    # TODO: Ghetto way to get date string once. 12/27/17 -AW
    url = HIST_URL%('AAPL','5minute')
    try:
        content = requests.get(url).content
    except:
        content = ''
        sys.stdout.write("Date fetch failed!\n")
    time_idx = content.find('open_time')
    if time_idx < 0:
            failures.append(sym)
            return
    date = content[time_idx+12:time_idx+22] 
    for idx in range(len(syms)):        
        sym = syms[idx]
        sys.stdout.write(" Loading %s\n"%sym)
        ticker_path = dir + '/' + sym
        if sym == 'PRN':
            ticker_path += '+'
        if not os.path.exists(ticker_path):
            os.makedirs(ticker_path)   
        date_file = ticker_path + '/' + date
        if os.path.isfile(date_file):
            sys.stdout.write("  File %s already exists!\n"%date_file)
            if overwrite:
                sys.stdout.write("  Overwriting %s...\n"%date_file)
            else:
                sys.stdout.write("  Overwrite is off. %s will be appended to failures.\n"%sym)
                #failures.append(sym)
                continue
        url = HIST_URL%(sym,'5minute')            
        try:
            content = requests.get(url).content
        except:
            content = ''
            sys.stdout.write("  Cloud data access failed for %s!\n"%sym)
        time_idx = content.find('open_time')            

        with open(date_file,'w') as f:
            f.write(content)    
    if len(failures) > 0:
        sys.stdout.write("\nThe following tickers failed to pull:\n ")
        for sym in failures:
            sys.stdout.write("'%s',"%sym)
        sys.stdout.write("\b \n")
    else:    
        sys.stdout.write("\nData pull and storage successful!\n")
    sys.stdout.write(" Total execution time: %s\n"%(str(time.clock()-t_start)))

def read_tickers_from_file(ticket_dir='C:/Users/Lucy/Documents/Finance/Data/tickers.txt'):
    tickers = None
    with open(ticker_dir,'r') as f:
        tickers = f.read().splitlines()  
    return tickers

def read_nasdaq():
    tickers = list()
    data = ''
    url = NASDAQ_TRADED_URL
    try:        
        ftp = FTP(url,'anonymous')
        r = StringIO()
        ftp.retrbinary('RETR SymbolDirectory/nasdaqtraded.txt', r.write)
        data = r.getvalue()
    except:
        sys.stdout.write("Failed to access data at %s!\n"%url)
        return None
    lines = data.splitlines()
    for line in lines:
        if line[0] is not 'Y':
            continue
        i1 = line.find('|')
        i2 = line.find('|',i1+1)
        if i1 < 0 or i2 < 0:
            continue
        ticker = line[i1+1:i2]
        ticker = ticker.replace('$','-') # Robihnood uses - instead of $
        tickers.append(ticker)    
    return tickers
    
def main():
    tickers = read_nasdaq()    
    save_day_5minute_data(tickers,True)
    #save_day_5minute_data(['TSLA','MU'],True)
    #get_5minute_data(['AAPL','TSLA','GE','MCHI'],'2017-12-27')
    
if __name__ == "__main__":
    main()