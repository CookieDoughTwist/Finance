import robin_stocks.robinhood as r

import os
import sys
import requests
import json
import time
from ftplib import FTP
from io import StringIO, BytesIO

#from Robinhood import Robinhood

HIST_URL = 'https://api.robinhood.com/quotes/historicals/%s/?interval=%s'
NASDAQ_TRADED_URL = 'ftp.nasdaqtrader.com'
#DATA_DIR = 'C:/Users/Lucy/Documents/Finance/Data/Daily5minute'
DATA_DIR = 'D:/Finance/Data/Daily5minute'

class DayPlayer():

    def __init__(self,start_date=None,end_date=None):
        self.start_date = start_date
        self.end_date = end_date
        self.syms = list()       
        self.data_bank = dict()
        self.loader = DayLoader()
        self.data = dict()
        
        self.idx = 0
        
    def add_syms(self,syms):
        self.syms += syms
        self.loader.load_syms(syms)
        self.add_syms(syms)
        
    def poll(self):        
        new_data = []
        # TODO: Try/Except is probably not the best way to handle end of data... 1/4/18 -AW
        try:
            for sym in self.syms:
                new_data.append(self.data[sym][self.idx])
        except:
            return None
        self.idx += 1
        return new_data
        
class DayLoader:
    def __init__(self):
        self.day_data = dict()
        
    def add_syms(self,syms):    
        historicals = get_day_data(syms)        
        for idx in range(len(syms)):
            sym = syms[idx]
            self.day_data[sym] = historicals[idx]
    
    def get_range(self,sym,start_date=None,end_date=None):        
        historical = self.day_data[sym]
        if historical is None:
            return None
        # TODO: Remove this naive linear search... 1/4/18 -AW 
        if start_date is None:
            start_idx = 0
        else:
            for idx in range(len(historical)):
                cur_date = historical[idx]['begins_at'][:10]            
                if cur_date >= start_date:
                    start_idx = idx
                    break
        if end_date is None:
            end_idx = len(historical)-1
        else:
            for idx in reversed(range(len(historical))):
                cur_date = historical[idx]['begins_at'][:10]            
                if cur_date <= end_date:
                    end_idx = idx
                    break
        return historical[start_idx:end_idx+1]
                
        
def read_nasdaq():
    tickers = list()
    data = ''
    url = NASDAQ_TRADED_URL
    try:        
        ftp = FTP(url,'anonymous')
        #r = StringIO()
        r = BytesIO()
        ftp.retrbinary('RETR SymbolDirectory/nasdaqtraded.txt', r.write)        
        data = r.getvalue()
    except Exception as e:
        print(e)
        sys.stdout.write("Failed to access data at %s!\n"%url)
        return None
    lines = data.splitlines()
    for line in lines:
        line = line.decode("utf-8")
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

def get_day_data(syms,dir=DATA_DIR):    
    historicals = list()
    for sym in syms:
        ticker_path = dir + '/' + sym
        if sym == 'PRN':
            ticker_path += '+'
        if not os.path.exists(ticker_path):
            historicals.append(None)
            sys.stdout.write(" Ticker %s not in the database...\n"%sym)
            continue
        data_file = ticker_path + '/daily_data'
        if not os.path.isfile(data_file):
            historicals.append(None)
            sys.stdout.write(" Data for ticker %s not in the database...\n"%(sym))
            continue
        with open(data_file,'r') as f:
            res = f.read() 
        try:
            response = json.loads(res)
        except:
            sys.stdout.write(" Data for ticker %s not in the database...\n"%(sym))
            response = None
        historicals.append(response)
    return historicals    

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
        try:
            historicals.append(json.loads(res))
        except:
            sys.stdout.write("Date %s for ticker %s not in the database...\n"%(date,sym))
            historicals.append(None)        
    return historicals
    

URL_DICT = {
    "login": "https://api.robinhood.com/api-token-auth/",
    "logout": "https://api.robinhood.com/api-token-logout/",
    "investment_profile": "https://api.robinhood.com/user/investment_profile/",
    "accounts": "https://api.robinhood.com/accounts/",
    "ach_iav_auth": "https://api.robinhood.com/ach/iav/auth/",
    "ach_relationships": "https://api.robinhood.com/ach/relationships/",
    "ach_transfers": "https://api.robinhood.com/ach/transfers/",
    "applications": "https://api.robinhood.com/applications/",
    "dividends": "https://api.robinhood.com/dividends/",
    "edocuments": "https://api.robinhood.com/documents/",
    "instruments": "https://api.robinhood.com/instruments/",
    "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
    "markets": "https://api.robinhood.com/markets/",
    "notifications": "https://api.robinhood.com/notifications/",
    "orders": "https://api.robinhood.com/orders/",
    "password_reset": "https://api.robinhood.com/password_reset/request/",
    "portfolios": "https://api.robinhood.com/portfolios/",
    "positions": "https://api.robinhood.com/positions/",
    "quotes": "https://api.robinhood.com/quotes/",
    "historicals": "https://api.robinhood.com/quotes/historicals/",
    "document_requests": "https://api.robinhood.com/upload/document_requests/",
    "user": "https://api.robinhood.com/user/",
    "watchlists": "https://api.robinhood.com/watchlists/",
    "news": "https://api.robinhood.com/midlands/news/",
    "fundamentals": "https://api.robinhood.com/fundamentals/",
}

def save_day_5minute_data(syms,overwrite=False,dir=DATA_DIR):
    t_start = time.time()
    sys.stdout.write("Pulling and saving 5 minute resolution data:\n\n")
    failures = list()
    
    #ses = Robinhood()
    #ses.login(username="lucybgao@gmail.com", password="kiqrx8y91hx")
    
    login = r.login("lucybgao@gmail.com", "kiqrx8y91hx")
    
    # TODO: Ghetto way to get date string once. 12/27/17 -AW
    #url = HIST_URL%('AAPL','5minute')
    
    try:
        #content = requests.get(url).content
        #content = ses.get_historical_default('AAPL')
        content = r.get_stock_historicals('AAPL','5minute','day',raw=True)
        #print(type(contet))
    except:
        content = ''
        print(sys.exc_info()[0])
        sys.stdout.write("Date fetch failed!\n")    
    time_idx = content.find(b'open_time')
    if time_idx < 0:
        #failures.append(sym)
        return
    date = content[time_idx+12:time_idx+22].decode("utf-8")
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
        #    content = requests.get(url).content
        #    content = ses.get_historical_default(sym)
            content = r.get_stock_historicals(sym,'5minute','day',raw=True)
        except:
            sys.stdout.write("  Cloud data access failed for %s!\n"%sym)
            failures.append(sym)
            continue
        time_idx = content.find(b'open_time')            
        with open(date_file,'w') as f:
            f.write(content.decode("utf-8") )    
    if len(failures) > 0:
        sys.stdout.write("\nThe following tickers failed to pull:\n ")
        for sym in failures:
            sys.stdout.write("'%s',"%sym)
        sys.stdout.write("\b \n")
    else:    
        sys.stdout.write("\nData pull and storage successful!\n")
    sys.stdout.write(" Total execution time: %s\n"%(str(time.time()-t_start)))
    sys.stdout.write(" Timestamp: %s\n"%(time.asctime( time.localtime(time.time()) )))
    
def save_day_5minute_data_parallel(syms,overwrite=False,dir=DATA_DIR):
    t_start = time.time()
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
        
    if len(failures) > 0:
        sys.stdout.write("\nThe following tickers failed to pull:\n ")
        for sym in failures:
            sys.stdout.write("'%s',"%sym)
        sys.stdout.write("\b \n")
    else:    
        sys.stdout.write("\nData pull and storage successful!\n")
    sys.stdout.write(" Total execution time: %s\n"%(str(time.time()-t_start)))
    sys.stdout.write(" Timestamp: %s\n"%(time.asctime( time.localtime(time.time()) )))

def save_day_5minute_data_single():
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
            return
    url = HIST_URL%(sym,'5minute')            
    try:
        content = requests.get(url).content
    except:
        sys.stdout.write("  Cloud data access failed for %s!\n"%sym)
        failures.append(sym)
        return
    time_idx = content.find('open_time')            

    with open(date_file,'w') as f:
        f.write(content)    
    
def save_day_data(syms,dir=DATA_DIR):
    t_start = time.time()
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
        if start_idx < 0:
            # Invalid pull
            failures.append(sym)
            continue
        arr_content = content[start_idx:-1]        
        
        if not os.path.isfile(data_file):
            sys.stdout.write("  File %s does not exist. Generating now...\n"%data_file)
            with open(data_file,'w') as f:
                f.write(arr_content)
            continue
        # Process today's data        
        today_arr = json.loads(arr_content)  
        today_date = today_arr[-1]['begins_at'][:10]
        # Access stored data
        with open(data_file,'r') as f:        
            file_content = f.read()            
        try:
            file_arr = json.loads(file_content)
        except:
            sys.stdout.write("  JSON failed to read... Dumping file content and continuing.\n")
            with open(data_file,'w') as f:
                f.write(arr_content)
            failures.append(sym)
            continue
        last_date = file_arr[-1]['begins_at'][:10]
        # Loop checks back in time to see if there are missing days
        # Iterates until we find the entry matching the last day in the database
        cur_date = today_date
        data_adds = list()
        data_idx = 1
        while not cur_date == last_date:
            data_idx += 1
            cur_date = today_arr[-data_idx]['begins_at'][:10]
        if data_idx > 1:
            cur_bracket = len(arr_content)-1
            for r in range(data_idx-1):
                cur_bracket = arr_content.rfind('{',0,cur_bracket)                
            new_content = arr_content[cur_bracket:-1]
            tr_content = file_content[:-1]
            formed_content = tr_content+','+new_content+']'
            with open(data_file,'w') as f:
                f.write(formed_content)
        else:    
            sys.stdout.write("   %s is already up to date. Skipping...\n"%sym)        
            #failures.append(sym)    
    if len(failures) > 0:
        sys.stdout.write("\nThe following tickers failed to pull:\n ")
        for sym in failures:
            sys.stdout.write("'%s',"%sym)
        sys.stdout.write("\b \n")
    else:    
        sys.stdout.write("\nData pull and storage successful!\n")
    sys.stdout.write(" Total execution time: %s\n"%(str(time.time()-t_start)))

    
def daily_routine():
    tickers = read_nasdaq()    
    save_day_5minute_data(tickers)
    #save_day_5minute_data_parallel(tickers)
    #save_day_data(tickers)
    
def main():    
    daily_routine()
    #test_DataLoader()
    #get_day_data(['AAPL','GE','ASDFG','VLY.W'])
    #get_5minute_data(['AAPL','TSLA','GE','MCHI'],'2017-12-27')
    
if __name__ == "__main__":
    main()