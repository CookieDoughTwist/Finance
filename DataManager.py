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

class DayPlayer():

    def __init__(self,date):
        self.date = date
        self.syms = list()        
        sefl.data_bank = dict()
        
    def add_syms(self,syms):
        self.syms += syms
        self.update_data_bank()
        
    def update_data_bank(self):
        historical_data = get_5minute_data(self.syms,self,date)
        print historical_data
        
    def poll(self):
        pass
        
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
                failures.append(sym)
                continue
        url = HIST_URL%(sym,'5minute')            
        try:
            content = requests.get(url).content
        except:
            sys.stdout.write("  Cloud data access failed for %s!\n"%sym)
            failures.append(sym)
            continue
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

def save_day_data(syms,dir=DATA_DIR):
    t_start = time.clock()
    sys.stdout.write("Pulling and saving 1 day resolution data:\n\n")
    failures = list()
    
    for idx in range(len(syms)):
        sym = syms[idx]
        sys.stdout.write(" Loading %s\n"%sym)
        ticker_path = dir + '/' + sym
        if sym == 'PRN':
            ticker_path += '+'
        if not os.path.exists(ticker_path):
            os.makedirs(ticker_path)   
        data_file = ticker_path + '/daily_data'
        url = HIST_URL%(sym,'day')
        try:
            content = requests.get(url).content
        except:
            sys.stdout.write("  Cloud data access failed for %s!\n"%sym)
            failures.append(sym)
            continue
        start_idx = content.find('[{')
        arr_content = content[start_idx:-1]        
        
        if not os.path.isfile(data_file):
            sys.stdout.write("  File %s does not exist. Generating now...\n"%data_file)
            with open(data_file,'w') as f:
                f.write(arr_content)
            continue
        # Process today's data
        op_idx = arr_content.rfind('{')
        cb_idx = arr_content.rfind('}',0,-1)                
        today_entry = arr_content[op_idx:cb_idx+1]
        date_idx = today_entry.find('begins_at')    
        today_date = today_entry[date_idx+12:date_idx+22]
        # Access stored data
        with open(data_file,'r') as f:        
            file_content = f.read()        
        op_idx = file_content.rfind('{')
        cb_idx = file_content.rfind('}',0,-1)        
        last_entry = file_content[op_idx:cb_idx+1]
        date_idx = last_entry.find('begins_at')
        last_date = last_entry[date_idx+12:date_idx+22]
        if not today_date == last_date:
            tr_content = file_content[:cb_idx+1]
            new_content = tr_content+','+today_entry+']'
            with open(date_file,'w') as f:
                f.write(new_content)
    
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



    
def daily_routine():
    tickers = read_nasdaq()    
    save_day_5minute_data(tickers)
    
    
def main():
    daily_routine()
    #tickers = read_nasdaq()    
    #save_day_data(tickers)

    #get_5minute_data(['AAPL','TSLA','GE','MCHI'],'2017-12-27')
    
if __name__ == "__main__":
    main()