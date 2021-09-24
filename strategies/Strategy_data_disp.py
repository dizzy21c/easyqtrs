from easyquant import StrategyTemplate
# from easyquant import RedisIo
from easyquant import DataUtil
from threading import Thread, current_thread, Lock
import json
# import redis
import time
# import datetime
from datetime import datetime, date

# import pymongo
# import pandas as pd
# import talib
import pika

from easyquant import EasyMq
from easyquant import MongoIo
from multiprocessing import Pool, cpu_count
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
mongo = MongoIo()
executor = ThreadPoolExecutor(max_workers=cpu_count() * 50)
# class SaveData(Thread):
#     def __init__(self, code,data):
#         Thread.__init__(self)
#         self.data = data
#         self.code = code
#         # self.log = log
#         # # self.redis = redis
#         # self.idx = idx
#         # self.m = MongoIo()
#         # self.last_time = None
#         # self.working = False
#
#     # def set_data(self, code, data, idx):
#     #     Thread.__init__(self)
#     #     self._data = data
#     #     self.code = code
#     #     self.log = log
#     #     # self.redis = redis
#
#     def run(self):
#         self.data['_id'] = "%s-%s" %( self.code, self.data['datetime'])
#         self.data['price'] = self.data['now']
#         mongo.save_realtime(self.data)

def save_monto_realtime(code, data):
    data['_id'] = "{}-{}".format( code, data['datetime'])
    data['price'] = data['now']
    mongo.save_realtime(data)

class Strategy(StrategyTemplate):
    name = 'save-data-disp'
    idx = 0
    EventType = 'data-sina'
    # config_name = './config/worker_list.json'

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        # self.redis = RedisIo()
        self.data_util = DataUtil()
        
        self.easymq = EasyMq()
        self.easymq.init_pub(exchange="stockcn")

    def strategy(self, event):
        if event.event_type != self.EventType:
            return

        self.log.info('Strategy =%s, event_type=%s' %(self.name, event.event_type))
        task_list = []
        rtn = {}
        # print(datetime.datetime.now())
        for stcode in event.data:
            stdata= event.data[stcode]
            # self.log.info("data=%s, data=%s" % (stcode, stdata))
            # self.easymq.pub(json.dumps(stdata, cls=CJsonEncoder), stcode)
            # aa = json.dumps(stdata)
            # self.log.info("code=%s, data=%s" % (stcode, aa))
            self.easymq.pub(json.dumps(stdata), stcode)
            rtn=self.data_util.day_summary(data=stdata, rtn=rtn)
            chk_time = stdata['datetime'][11:]
            if chk_time < '09:35:00' or chk_time > '14:59:00':
                task_list.append(executor.submit(save_monto_realtime, stcode, stdata))
            # threads.append(SaveData(stcode, stdata))
        self.log.info(rtn)

        for task in as_completed(task_list):
            # result = task.result()
            pass
        self.log.info('Strategy =%s, event_type=%s done.' %(self.name, event.event_type))

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        # elif isinstance(obj, date):
        #     return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)