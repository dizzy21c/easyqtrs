# from easyquant import StrategyTemplate
# from easyquant import RedisIo
from easyquant import DataUtil, DefaultLogHandler

from threading import Thread, current_thread, Lock
import json
# import redis
import time
# import datetime
from datetime import datetime, date
import pandas as pd

# import pymongo
# import pandas as pd
import pika

from easyquant import EasyMq
from easyquant import MongoIo
from multiprocessing import Process, Pool, cpu_count, Manager

from QUANTAXIS.QAFetch import QATdx as tdx

# import tushare as ts

data_buf_day = Manager().dict()
data_buf_15min = Manager().dict()
data_buf_15min_0 = Manager().dict() ##0-today
# mongo = MongoIo()
end_date = '2030-12-31'
st_date = '2020-01-01'
def do_init_data_buf(code, idx):
    # print(code)
    mongo=MongoIo()
    if idx == 0:
        data_day = mongo.get_stock_day(code=code)
        data_15min = mongo.get_stock_min(code=code)
        if len(data_15min) == 0:
            data_15min = tdx.QA_fetch_get_stock_min(code, st_date,end_date, 15)
        else:
            last_dt = data_15min.datetime.iloc[-1]
            
    else:
        data_day = mongo.get_index_day(code=code)
        data_15min = mongo.get_index_min(code=code)
        if len(data_15min) == 0:
            data_15min = tdx.QA_fetch_get_index_min(code, st_date,end_date, 15)
    ## TODO fuquan 
    data_buf_day[code] = data_day
    data_buf_15min[code] = data_15min
    # print("do-init data end, code=%s, data-buf size=%d " % (code, len(data_buf_day)))


class calcStrategy(Thread):
    def __init__(self, code, data, log, idx):
        Thread.__init__(self)
        self._data = data
        self.code = code
        self.log = log
        # self.redis = redis
        self.idx = idx
        self.last_time = None
    
    def run(self):
        if self.last_time is None:
            self.last_time = pd.to_datetime(self._data['datetime'][0:10])
        else:
            last_time = pd.to_datetime(self._data['datetime'][0:10])
            if last_time == self.last_time:
                return
            self.last_time = last_time
        
        print("data-buf-len=%d" % len(data_buf_day))
        df_day = data_buf_day[self.code]
        df_day.loc[self.last_time]=[0 for x in range(len(df_day.columns))]
        df_day.loc[self.last_time].open = self._data['open']
        df_day.loc[self.last_time].high= self._data['high']
        df_day.loc[self.last_time].low = self._data['low']
        df_day.loc[self.last_time].close = self._data['close']
        df_day.loc[self.last_time].vol = self._data['volume']
        df_day.loc[self.last_time].amount = self._data['amount']
       
        # df=pd.concat([tdx.MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
        # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']
        print("calc ma...")
        df=pd.concat([tdx.MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        df_v=pd.concat([tdx.MA(df_day.vol, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df_v.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        df_a=pd.concat([tdx.MA(df_day.amount, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df_a.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']
        # print(data_df.head())
        # if back_test:
        # O,C,H,L,V,A = data_df.open, data_df.close, data_df.high, data_df.low, data_df.vol, data_df.amount
        # C =data_df.close
        
        # else:
        #     sina_data = redis.get_cur_data(code, idx = idx)
        #     O,C,H,L,V,A = redis.get_day_ps_ochlva(data_df, sina_data)

        print("%6.2f" % df.m5.iloc[-1])
        self.log.info("data=%s, m5=%6.2f" % (self.code, df.m5.iloc[-1]))
        
        # self.easymq.pub(text=self.code, routing_key = self.code)
        # self.log.info("data=%s" % self.code)
        # chgValue = (self._data['now'] - self._data['close'])
        # # downPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # # upPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # # chkVPct =  ( self._data['now'] - self._chkv  ) * 100 / self._chkv
        # pct = chgValue * 100 / self._data['close']
        # # print ("code=%s now=%6.2f pct=%6.2f hl=%6.2f" % ( self._code, self._data['now'], pct, downPct))
        # # if pct > 3 or (pct < 0 and pct > -12) :
        # self.log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self.code, self._data['now'], pct, self._data['high'], self._data['low']))
        #   self._log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self._code, self._data['now'], pct, self._data['high'], self._data['low']))
        
        # if self.code == "000004" or self.code == "000001":
        #     self.log.info("data=%s" % self.data['name'])
        # self.log.info("code=%s, time=%s" % (self.code, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        # self.redis.set_cur_data(self.code, self.data, idx = 0)
        # if self.data['open'] <= 0:
        #     return
        # self.redis.push_day_data(self.code, self.data, idx = 0)
        # # self.redis.push_cur_data(self.code, self.data, idx = 0)
        
class Strategy(object):
    name = 'save-data-calc-01'
    idx = 0
    EventType = 'data-sina'
    config_name = './config/stock2_list.json'

    def __init__(self):
        # StrategyTemplate.__init__(self, user, log_handler, main_engine)
        log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
        log_filepath = 'logs/mainlog2.txt' #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''
        self.log = DefaultLogHandler(name='real-data', log_type=log_type, filepath=log_filepath)
        
        self.log.info('init event:%s'% self.name)
        # self.redis = RedisIo()
        # self.data_util = DataUtil()
        # self.code_list = []
        self.idx=0
        
        # init data
        start_time = time.time()
        pool = Pool(cpu_count())
        res_l=[]
        with open(self.config_name, 'r') as f:
            data = json.load(f)
            for d in data['code']:
                if len(d) > 6:
                    d = d[len(d)-6:len(d)]
                # self.code_list.append(d)
                res=pool.apply_async(do_init_data_buf, args=(d, 0))
                res_l.append(res)
                # do_init_data_buf(d, 0)
                
        pool.close()
        pool.join()
        # pool.terminate()
        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))
        
        ## init message queue
        self.started=False
        self.easymq = EasyMq()
        self.easymq.init_receive(exchange="stockcn")
        self.easymq.callback = self.callback
        with open(self.config_name, 'r') as f:
            data = json.load(f)
            for d in data['code']:
                if len(d) > 6:
                    d = d[len(d)-6:len(d)]
                self.easymq.add_sub_key(routing_key=d)
                # self.code_list.append(d)
                # 
                # pool.apply_async(do_init_data_buf, args=(d, self.idx, self.data_type))
        # self.easymq.callback = mycallback
        # self.easymq.start()


    def start(self):
        if self.started:
            return
        
        self.started = True
        self.easymq.start()
        
    def callback(self, a, b, c, data):
        data = json.loads(data)
        # self.log.info("data111=%s" % data['code'])
        t = calcStrategy(data['code'], data, self.log, self.idx)
        t.start()


a = Strategy()
a.start()
