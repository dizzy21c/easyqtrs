from easyquant import StrategyTemplate
from easyquant.indicator.udf_formula import *
from easyquant import DataUtil
from easyquant import DefaultLogHandler
from easyquant import RedisIo
from threading import Thread, current_thread, Lock, Event
from multiprocessing import Process, Pool, cpu_count
import json
import redis
import time
#import pymongo
# from pandas import Series
# import pandas as pd
# import numpy as np
# import talib
redis=RedisIo()

_logname="do-index-worker"
_log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
_log_filepath = 'logs/%s.txt' % _logname #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''
log_handler = DefaultLogHandler(name=_logname, log_type=_log_type, filepath=_log_filepath)

def do_calc(code, idx):
    # log.info("do calc")
    # print("start do-calc")
    data_df = redis.get_day_df(code, idx=idx)
    Flg, out = udf_dapan_risk_df(data_df)
    if Flg: 
        log_handler.info(" data risk => code=%s , value= %s " %  (code, out))
    # log_handler.info(" data risk => code=%s , value= %s " %  (code, out))

    if udf_hangqing_start_df(data_df):
        log_handler.info(" data market start=>code=%s" % code )


class Strategy(StrategyTemplate):
    name = 'index-worker'
    EventType = 'worker'
    config_name = './config/index_list.json'
    idx=1

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        start_time = time.time()
        self.log.info('init event:%s' % (self.name))
        # self.hdata={}
        self.threads = []
        # start_date = '2018-01-01'
        self.rio=RedisIo('redis.conf')
        self.data_util = DataUtil()
        self.code_list = []
        # self.pool = Pool(10)
        self.is_working = False
        # self.pt = UdfIndexRisk()
        # self.qd = UdfMarketStart()
        with open(self.config_name, 'r') as f:
            data = json.load(f)
            for d in data['code']:
                self.code_list.append(d)
        #         # data_df = self.rio.get_day_df(d, idx=self.idx)
        #         # data_map = data_util.df2series(data_df)
                # self.hdata[d] = data_map

        #     for t in self.threads:
        #         # t.setDaemon(True)
        #         t.start()

            # for t in self.threads:
            #     t.join()

        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))

    def loading(self, code, idx):
        data_df = self.rio.get_day_df(code, idx=self.idx)
        data_map = self.data_util.df2series(data_df)
        # self.hdata[code] = data_map

    def strategy(self, event):
        # self.log.info('\nStrategy =%s, event_type=%s' %(self.name, event.event_type))
        if self.is_working:
            return
        if event.event_type != self.EventType:
            return
        self.log.info('Strategy =%s, event_type=%s' %(self.name, event.event_type))
        pool = Pool(cpu_count())
        self.is_working = True

        for stcode in self.code_list:
            pool.apply_async(do_calc, args=(stcode, self.idx))

        # i = 0
        # stcode = []
        # code_len = len(self.code_list)
        # while i < code_len:
        #     stcode.append(self.code_list[i])
        #     if i % 10 == 0 or i == code_len - 1:
        #         pool.apply_async(do_calc, args=(stcode, self.idx, self.pt, self.qd))
        #         stcode = []
        #     i += 1
        pool.close()
        pool.join()
        pool.terminate()
        self.is_working = False
        self.log.info("do-working-end name=%s" % self.name)