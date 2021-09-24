from easyquant import StrategyTemplate
# from easyquant import RedisIo
from easyquant import DataUtil
from threading import Thread, current_thread, Lock
import json
# import redis
import time
# import datetime
from datetime import datetime, date
import pandas as pd

# import pymongo
from QUANTAXIS.QAFetch import QATdx as tdx

import pika

from easyquant import EasyMq
from easyquant import MongoIo
from easyquant import EasyTime
from multiprocessing import Process, Pool, cpu_count, Manager
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed


# calc_thread_dict = Manager().dict()
data_buf_day = Manager().dict()
data_buf_5min = Manager().dict()
data_buf_5min_0 = Manager().dict()
mongo = MongoIo()
easytime=EasyTime()

executor = ThreadPoolExecutor(max_workers=cpu_count() * 50)

def do_init_data_buf(code, idx):
    freq = 5
    # mongo = MongoIo()
    if idx == 0:
        data_day = mongo.get_stock_day(code=code)
        # data_min = mongo.get_stock_min_realtime(code=code, freq=freq)
        data_min = mongo.get_stock_min(code=code, freq=freq)
    else:
        data_day = mongo.get_index_day(code=code)
        # data_min = mongo.get_index_min_realtime(code=code)
        data_min = mongo.get_index_min(code=code)
    ## TODO fuquan
    data_buf_day[code] = data_day
    data_buf_5min[code] = data_min
    # print("do-init data end, code=%s, data-buf size=%d " % (code, len(data_buf_5min)))

def do_init_data_ext(code_list, idx):
    pass

# class UpdateDataThread(Thread):
#     def __init__(self, code, idx):
#         Thread.__init__(self)
#         self.code = code
#         self.idx = idx
#
#     def run(self):
#         do_init_data_buf(self.code, self.idx)

class calcStrategy(Thread):
    def __init__(self, code, data, log, idx):
        Thread.__init__(self)
        self._data = data
        self.code = code
        self.log = log
        # self.redis = redis
        self.idx = idx
        # self.last_time = None
        # self.working = False
    
    # def set_data(self, code, data, idx):
    #     Thread.__init__(self)
    #     self._data = data
    #     self.code = code
    #     self.log = log
    #     # self.redis = redis
    def upd_min(self, minute):
        # index_time =pd.to_datetime(easytime.get_minute_date(minute=5))
        index_time = pd.to_datetime(easytime.get_minute_date_str(minute=minute, str_date=self._data['datetime']))
        df_min = data_buf_5min[self.code]
        # if self.code == '600822':
        #     print("0 code=%s, data=%d" % (self.code, len(df_min)))
        if len(df_min) > 0:
            ## TODO 计算单日前的数据
            # old_vol = 0
            # old_amount = 0
            beg_time = pd.to_datetime(easytime.get_minute_date_str(minute=minute, str_date=self._data['datetime']))
            sum_df=df_min.loc[df_min.index > beg_time]
            old_vol = sum_df['vol'].sum()
            old_amount = sum_df['amount'].sum()
            # if self.code == '600822':
            #     print("1 code=%s, data=%d" % (self.code, len(df_min)))
            now_price = self._data['now']
            if index_time in df_min.index:
                # if self.code == '600822':
                #     print("10 code=%s, data=%s" % (self.code, index_time))
                # df_min.loc[index_time, 'open'] = now_price
                if now_price > df_min.loc[index_time, 'high']:
                    df_min.loc[index_time, 'high'] = now_price
                if now_price < df_min.loc[index_time, 'low']:
                    df_min.loc[index_time, 'low'] = now_price
                df_min.loc[index_time, 'close'] = now_price
                df_min.loc[index_time, 'vol'] = self._data['volume'] - old_vol
                df_min.loc[index_time, 'amount'] = self._data['amount'] - old_amount
            else:
                # if self.code == '600822':
                #     print("2 code=%s, data=%d" % (self.code, len(df_min)))
                df_min.loc[index_time] = [0 for x in range(len(df_min.columns))]
                df_min.loc[index_time, 'open'] = now_price
                df_min.loc[index_time, 'high'] = now_price
                df_min.loc[index_time, 'low'] = now_price
                df_min.loc[index_time, 'close'] = now_price
                df_min.loc[index_time, 'vol'] = self._data['volume'] - old_vol
                df_min.loc[index_time, 'amount'] = self._data['amount'] - old_amount
                ## vol 计算
        else: ##first day ???
            pass

        data_buf_5min[self.code] = df_min

    def run(self):
        # if self.working:
        #     return
        
        # self.working = True
        now_price = self._data['now']
        now_vol = self._data['volume']
        last_time = pd.to_datetime(self._data['datetime'][0:10])
        # print("code=%s, data=%s" % (self.code, self._data['datetime']))
        df_day = data_buf_day[self.code]
        df_day.loc[last_time]=[0 for x in range(len(df_day.columns))]
        df_day.loc[last_time,'open'] = self._data['open']
        df_day.loc[last_time,'high']= self._data['high']
        df_day.loc[last_time,'low'] = self._data['low']
        df_day.loc[last_time,'close'] = now_price
        df_day.loc[last_time,'vol'] = self._data['volume']
        df_day.loc[last_time,'amount'] = self._data['amount']
        # df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
        # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']
        df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        df_v=pd.concat([MA(df_day.vol, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df_v.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        df_a=pd.concat([MA(df_day.amount, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df_a.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        # self.log.info("data=%s, m5=%6.2f" % (self.code, df.m5.iloc[-1]))
        self.upd_min(5)
        # self.log.info()
        # if now_vol > df_v.m5.iloc[-1]:
        # if self._data['close'] > 0:
        chag_pct = (self._data['now'] - self._data['close']) / self._data['close'] * 100
        # else:
        #     chag_pct = 0.0
        # self.log.info("code=%s now=%6.2f pct=%6.2f m5=%6.2f, now_vol=%10f, m5v=%10f" % (self.code, now_price, self._data['chg_pct'], df.m5.iloc[-1], now_vol, df_v.m5.iloc[-1]))
        self.log.info("code=%s now=%6.2f pct=%6.2f m5=%6.2f, high=%6.2f, low=%6.2f" % (self.code, now_price, chag_pct, df.m5.iloc[-1], self._data['high'], self._data['low']))


        # self.working = False
class Strategy(StrategyTemplate):
    name = 'calc-min-data'  ### day
    idx = 0
    # EventType = 'data-sina'
    config_name = './config/stock2_list.json'

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        # self.redis = RedisIo()
        # self.data_util = DataUtil()
        # self.code_list = []
        self.idx=0
        self.calc_thread_dict = {}
        # init data
        start_time = time.time()
        task_list = []
        code_list = []
        with open(self.config_name, 'r') as f:
            data = json.load(f)
            for d in data['code']:
                if len(d) > 6:
                    d = d[len(d)-6:len(d)]
                    code_list.append(d)
                # self.code_list.append(d)
                # pool.apply_async(do_init_data_buf, args=(d, self.idx))
                # do_init_data_buf(d, self.idx)
                # poolThread.append(UpdateDataThread(d, self.idx))
                task_list.append(executor.submit(do_init_data_buf, d, self.idx))
                # self.calc_thread_dict[d] = calcStrategy(data['code'], self.log)
        # pool.close()
        # pool.join()
        # pool.terminate()
        # for c in poolThread:
        #     c.start()
        #
        # for c in poolThread:
        #     c.join()
        for task in as_completed(task_list):
            # result = task.result()
            pass

        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))
        
        ## init message queue
        self.started = False
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

    def strategy(self, event):
        if self.started:
            return
        self.log.info('Strategy =%s, easymq started' % self.name)
        self.started = True
        self.easymq.start()
        
    def callback(self, a, b, c, data):
        # self.log.info('Strategy =%s, start calc...' % self.name)
        # data = json.loads(data)
        # t = calcStrategy(data['code'], data, self.log, self.idx)
        # t.start()
        pass
