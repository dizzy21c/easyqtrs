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
executor = ThreadPoolExecutor(max_workers=cpu_count() * 50)
def save_monto_realtime(code, data):
    data['_id'] = "{}-{}".format( code, data['datetime'])
    data['price'] = data['now']
    mongo.save_realtime2(data)

class Strategy:
    name = 'data-stock'  ### day

    def __init__(self, log_handler):
        self.log = log_handler
        self.log.info('init event:%s'% self.name)
        
        self.easymq = EasyMq()
        self.easymq.init_receive(exchange="stockcn")
        self.easymq.callback = self.callback
        self.easymq.add_sub_key(routing_key='data')
        
        start_time = time.time()

        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))
        
    def start(self):
        self.log.info('Strategy =%s, easymq started' % self.name)
        self.started = True
        self.easymq.start()
        
    def callback(self, a, b, c, data):
        # self.log.info('Strategy =%s, start calc...' % self.name)
#         print(datetime.datetime.now())
        data = json.loads(data)
#         print("data-size", len(data))
        task_list = []
        for stdata in data:
            stcode = stdata['code']
            if stcode == 'SZ000859':
                print("data", stcode)
#                 chk_time = stdata['datetime'][11:]
#                 task_list.append(executor.submit(save_monto_realtime, stcode, stdata))
#                 save_monto_realtime(stcode, stdata)
#         for task in as_completed(task_list):
#             pass

        
if __name__ == "__main__":
    log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
    # log_name = Strategy.name
    log_filepath = 'logs/%s.txt' % Strategy.name
    log_handler = DefaultLogHandler(name='calc-data', log_type=log_type, filepath=log_filepath)
    
    s = Strategy(log_handler)
    s.start()
