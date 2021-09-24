from easyquant import StrategyTemplate
from easyquant import UdfIndexRisk
from easyquant import UdfMarketStart
from easyquant import DataUtil
from easyquant import RedisIo
from threading import Thread, current_thread, Lock
import json
import redis
import time
#import pymongo
from pandas import Series
import pandas as pd
import numpy as np
import talib

class calcStrategy(Thread):
    def __init__(self, code, new_data, log, redisIo, idx):
        Thread.__init__(self)
        # self.data = new_data
        self.code = code
        self.log = log
        self.redis = redisIo
        self.data_util = DataUtil()
        self.pt = UdfIndexRisk()
        self.qd = UdfMarketStart()
        self.idx = idx
        # self.data_map = his_data
        #{'name': '"', 'open': 11.19, 'close': 11.1, 'now': 11.47, 'high': 11.63, 'low': 11.19, 'buy': 11.46, 'sell': 11.47, 'turnover': 54845630, 'volume': 629822482.49, 'bid1_volume': 52700, 'bid1': 11.46, 'bid2_volume': 94600, 'bid2': 11.45, 'bid3_volume': 10900, 'bid3': 11.44, 'bid4_volume': 40700, 'bid4': 11.43, 'bid5_volume': 60500, 'bid5': 11.42, 'ask1_volume': 5200, 'ask1': 11.47, 'ask2_volume': 70600, 'ask2': 11.48, 'ask3_volume': 116300, 'ask3': 11.49, 'ask4_volume': 248000, 'ask4': 11.5, 'ask5_volume': 26200, 'ask5': 11.51, 'date': '2019-04-08', 'time': '14:12:33'}
        # self.redis = redis.Redis(host='localhost', port=6379, db=0)
        # self.redis.push_day_data(self.code, data, idx=1)

    def run(self):
        data_df = None
        try:
            data_df = self.redis.get_day_df(self.code, idx=self.idx)
        except Exception as e:
            time.sleep(1)
            try:
                data_df = self.redis.get_day_df(self.code, idx=self.idx)
            except Exception as e1:
                data_df = None
        if data_df is None:
            self.log.info("index-data read error:code=%s" % self.code)
            return

        # finally:
        #     self.log.info("data read error: code= %s" % self.code )
        # data_df = self.redis.get_day_df(self.code, idx=self.idx)
        # data_map = self.data_util.df2series(data_df)
        # C, H, L, O, V, D = self.data_util.append2series(self.data_map, self.data)
        # # C = H = L = []
        out = self.pt.check(data_df.close,data_df.high, data_df.low)
        if out['flg']:
            self.log.info(" index risk => code=%s , value= %s " %  (self.code, out))

        # self.log.info("begin calc %s" % self.code)
        if self.qd.check(data_df.close):
            self.log.info(" index market start=>code=%s" % self.code )

class Strategy(StrategyTemplate):
    name = 'index-risk'
    EventType = 'worker'
    config_name = './config/index_list.json'
    idx=1

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        start_time = time.time()
        self.log.info('init event:%s' % self.name)
        # self.hdata={}
        # start_date = '2018-01-01'
        self.rio=RedisIo('redis.conf')
        self.code_list = []
        # data_util = DataUtil()
        with open(self.config_name, 'r') as f:
            data = json.load(f)
            for d in data['code']:
                if d[0:2] == "sh":
                    d = d[2:]
        #         data_df = self.rio.get_day_df(d, idx=self.idx)
        #         data_map = data_util.df2series(data_df)
                self.code_list.append(d)

        # self.log.info('init event end:%s' % self.name)
        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))
    def strategy(self, event):
        if event.event_type != self.EventType:
            return

        # self.log.info('\nStrategy =%s, event_type=%s' %(self.name, event.event_type))
        threads = []
        #for td in event.data:
        #    self.log.info(td)
        for stcode in self.code_list:
        # for stcode in event.data:
            # stdata= event.data[stcode]
            # rtn=self.summary(data=stdata,org=rtn)
            threads.append(calcStrategy(stcode, None, self.log, self.rio, idx=1))

        # for d in event.data:
        #     threads.append(calcStrategy(d, event.data[d], self.log))

        for c in threads:
            c.start()

        # self.log.info('\n')

