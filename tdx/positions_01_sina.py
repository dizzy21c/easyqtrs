# from easyquant import StrategyTemplate
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
import pika
# from QUANTAXIS.QAFetch import QATdx as tdx
from easyquant import DefaultLogHandler
# from util import new_df

from easyquant import EasyMq
from easyquant import MongoIo
from easyquant import EasyTime
from multiprocessing import Process, Pool, cpu_count, Manager
from easyquant.indicator.base import *
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
#from pyalgotrade.strategy import position

from func.tdx_func import *

# calc_thread_dict = Manager().dict()
data_buf_day = Manager().dict()
# data_buf_5min = Manager().dict()
# data_buf_5min_0 = Manager().dict()
mongo = MongoIo()
easytime=EasyTime()
executor = ThreadPoolExecutor(max_workers=cpu_count() * 10)
def do_init_data_buf(code):
    # freq = 5
    # 进程必须在里面, 线程可以在外部
    # mc = MongoIo()
    # mongo = MongoIo()
    # if idx == 0:
    data_day = mongo.get_stock_day(code=code) #, st_start="2020-05-15")
        # data_min = mc.get_stock_min_realtime(code=code, freq=freq)
    # else:
    #     data_day = mongo.get_index_day(code=code)
        # data_min = mc.get_index_min_realtime(code=code)
    data_buf_day[code] = data_day
    # data_buf_5min[code] = data_min
    # print("do-init data end, code=%s, data-buf size=%d " % (code, len(data_day)))

def do_main_work(code, data, log, positions):
    hold_price = positions['price']
    now_price = data['now']
    high_price = data['high']
    ##TODO 绝对条件１
    ## 止损卖出
    # if now_price < hold_price / 1.05:
    #     log.info("code=%s now=%6.2f solding..." % (code, now_price))
    # ## 止赢回落 %5，卖出
    # if now_price > hold_price * 1.02 and now_price < high_price / 1.03:
    #     log.info("code=%s now=%6.2f solding..." % (code, now_price))
        # 卖出
    now_vol = data['volume']
    # last_time = pd.to_datetime(data['datetime'][0:10])
    # print("code=%s, data=%s" % (self.code, self._data['datetime']))
    df_day = data_buf_day[code]
    df_day = new_df(df_day, data, now_price)

    ## add begin
    m5 = MA(df_day.close, 5)
    # xg, sell_flg, nbFlg = tdx_buerfameng(df_day)
    xg = tjS(df_day)
    midBS = tdx_MID_BS_Check(df_day)
#     print("mid", midBS)
    chag_pct = (data['now'] - data['close']) / data['close'] * 100
    log.info("code=%s bf=%d now=%6.2f pct=%6.2f m5=%6.2f, high=%6.2f, low=%6.2f, mid=%6.2f, low1=%6.2f, high1=%6.2f" % (code, xg.iloc[-1], now_price, chag_pct, m5.iloc[-1], data['high'], data['low'], midBS.midp, midBS.low1, midBS.high1))
#     log.info("code=%s bf=%d now=%6.2f pct=%6.2f m5=%6.2f, high=%6.2f, low=%6.2f" % (code, xg.iloc[-1], now_price, chag_pct, m5.iloc[-1], data['high'], data['low']))
    #
    # # df_day.loc[last_time]=[0 for x in range(len(df_day.columns))]
    # # df_day.loc[(last_time,code),'open'] = data['open']
    # # df_day.loc[(last_time,code),'high']= data['high']
    # # df_day.loc[(last_time,code),'low'] = data['low']
    # # df_day.loc[(last_time,code),'close'] = now_price
    # # df_day.loc[(last_time,code),'vol'] = data['volume']
    # # df_day.loc[(last_time,code),'amount'] = data['amount']
    # # df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
    # # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']
    # df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']
    #
    # df_v=pd.concat([MA(df_day.vol, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df_v.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']
    #
    # df_a=pd.concat([MA(df_day.amount, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df_a.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']
    #
    # # self.log.info("data=%s, m5=%6.2f" % (self.code, df.m5.iloc[-1]))
    # # self.upd_min(5)
    # # self.log.info()
    # # if now_vol > df_v.m5.iloc[-1]:
    # # self.log.info("code=%s now=%6.2f pct=%6.2f m5=%6.2f, now_vol=%10f, m5v=%10f" % (self.code, now_price, self._data['chg_pct'], df.m5.iloc[-1], now_vol, df_v.m5.iloc[-1]))
    # # if toptop_calc(df_day):
    # # if now_price < df.m5.iloc[-1]:
    # chag_pct = (data['now'] - data['close']) / data['close'] * 100
    # log.info("toptop code=%s now=%6.2f pct=%6.2f m5=%6.2f, high=%6.2f, low=%6.2f" % (code, now_price, chag_pct, df.m5.iloc[-1], data['high'], data['low']))
    # ## 低于５日线，卖出
    # # if now_price < df.m5.iloc[-1]:
    # #     log.info("code=%s now=%6.2f solding..." % (code, now_price))
    #     # 卖出

class Strategy:
    name = 'calc-stock'  ### day

    def __init__(self, log_handler):
        self.log = log_handler
        self.log.info('init event:%s'% self.name)
        
        self.df_positions = mongo.get_positions()
        
        self.easymq = EasyMq()
        self.easymq.init_receive(exchange="stockcn")
        self.easymq.callback = self.callback
        
        start_time = time.time()
        task_list = []
        for code in self.df_positions.index:
            task_list.append(executor.submit(do_init_data_buf, code))
            self.easymq.add_sub_key(routing_key=code)
            
        for task in as_completed(task_list):
            # result = task.result()
            pass

        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))
        
        ## init message queue
        # self.started=False
        # self.easymq = EasyMq()
        # self.easymq.init_receive(exchange="stockcn")
        # self.easymq.callback = self.callback
        # with open(self.config_name, 'r') as f:
        #     data = json.load(f)
        #     for d in data['code']:
        #         if len(d) > 6:
        #             d = d[len(d)-6:len(d)]
        #         self.easymq.add_sub_key(routing_key=d)
                # self.code_list.append(d)
                # 
                # pool.apply_async(do_init_data_buf, args=(d, self.idx, self.data_type))
        # self.easymq.callback = mycallback
        # self.easymq.start()


    def start(self):
        self.log.info('Strategy =%s, easymq started' % self.name)
        self.started = True
        self.easymq.start()
        
    def callback(self, a, b, c, data):
        # self.log.info('Strategy =%s, start calc...' % self.name)
        data = json.loads(data)
        #code =data['code']
        if data['code'][:1] == 'S':
            code =data['code'][2:]
        else:
            code = data['code']
        # t.start()
        executor.submit(do_main_work, code, data, self.log, self.df_positions.loc[code])

if __name__ == "__main__":
    log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
    # log_name = Strategy.name
    log_filepath = 'logs/%s.txt' % Strategy.name
    log_handler = DefaultLogHandler(name='calc-data', log_type=log_type, filepath=log_filepath)
    
    s = Strategy(log_handler)
    s.start()
