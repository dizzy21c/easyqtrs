from easyquant import StrategyTemplate
from easyquant import UdfIndexRisk
from easyquant import UdfMarketStart
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


class calcStrategy(Thread):
    def __init__(self, code, log_handler, redis, idx):
    # def __init__(self, code, idx):
        Thread.__init__(self)
        # self.data = new_data
        # self.data_map = his_data
        self.code = code
        self.log = log_handler
        self.redis = redis
        self.idx = idx

        self.data_util = DataUtil()
        self.pt = UdfIndexRisk()
        self.qd = UdfMarketStart()

        self.__flag = Event()     # 用于暂停线程的标识
        self.__flag.set()       # 设置为True
        self.__running = Event()      # 用于停止线程的标识
        self.__running.set()      # 将running设置为True

        self.init_flg = True

        #{'name': '"', 'open': 11.19, 'close': 11.1, 'now': 11.47, 'high': 11.63, 'low': 11.19, 'buy': 11.46, 'sell': 11.47, 'turnover': 54845630, 'volume': 629822482.49, 'bid1_volume': 52700, 'bid1': 11.46, 'bid2_volume': 94600, 'bid2': 11.45, 'bid3_volume': 10900, 'bid3': 11.44, 'bid4_volume': 40700, 'bid4': 11.43, 'bid5_volume': 60500, 'bid5': 11.42, 'ask1_volume': 5200, 'ask1': 11.47, 'ask2_volume': 70600, 'ask2': 11.48, 'ask3_volume': 116300, 'ask3': 11.49, 'ask4_volume': 248000, 'ask4': 11.5, 'ask5_volume': 26200, 'ask5': 11.51, 'date': '2019-04-08', 'time': '14:12:33'}
        # self.redis = redis.Redis(host='localhost', port=6379, db=0)
        # self.redis.push_day_data(self.code, data, idx=1)

    # def set_init_resume(self, code, idx):
        # self.init_flg = True
        # self.resume()

    def set_data_resume(self, new_data):
        # self.log.info("set data. %s data... " % self.code)
        self.data = new_data[self.code]
        self.resume()

    def run(self):
        data_df = self.redis.get_day_df(self.code, idx=self.idx)
        # finally:
        #     self.log.info("data read error: code= %s" % self.code )
        # data_df = self.redis.get_day_df(self.code, idx=self.idx)
        # data_map = self.data_util.df2series(data_df)
        # C, H, L, O, V, D = self.data_util.append2series(self.data_map, self.data)
        # # C = H = L = []
        out = self.pt.check(data_df.close,data_df.high, data_df.low)
        if out['flg']:
            self.log.info(" data risk => code=%s , value= %s " %  (self.code, out))

        # self.log.info("begin calc %s" % self.code)
        if self.qd.check(data_df.close):
            self.log.info(" data market start=>code=%s" % self.code )

    # def run(self):
    #     data_df = self.redis.get_day_df(self.code, idx=self.idx)
    #     out = self.pt.check(data_df.close,data_df.high, data_df.low)
    #     if out['flg']:
    #         self.log.info(" index risk => code=%s , value= %s " %  (self.code, out))

    def run_old(self):
        while self.__running.isSet():
            self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回

            if self.init_flg:
                self.do_init_data()
            else:
                self.do_calc()

            self.pause()

    def do_init_data(self):
        # self.log.info("init %s data... " % self.code)
        data_df = self.redis.get_day_df(self.code, idx=self.idx)
        self.data_map = self.data_util.df2series(data_df)
        self.init_flg = False

    def do_calc(self):
        # self.log.info("do-calc. %s data... " % self.code)
        data_df = self.redis.get_day_df(self.code, idx=self.idx)
        # data_map = self.data_util.df2series(data_df)
        out = self.pt.check(data_df.close,data_df.high,data_df.low)
        # out = {'flg':0}
        if out['flg']:
            self.log.info(" data risk => code=%s , value= %s " %  (self.code, out))
        # # self.log.info(" code=%s , value= %s " %  (self.code, out))

        # self.log.info("begin calc %s" % self.code)
        if self.qd.check(data_df.close):
            self.log.info(" data market start=>code=%s" % self.code )

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()        # 设置为False

# redis=RedisIo()

# _logname="do-calc"
# _log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
# _log_filepath = 'logs/%s.txt' % _logname #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''
# log_handler = DefaultLogHandler(name=_logname, log_type=_log_type, filepath=_log_filepath)


redis=RedisIo()

_logname="do-calc"
_log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
_log_filepath = 'logs/%s.txt' % _logname #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''
log_handler = DefaultLogHandler(name=_logname, log_type=_log_type, filepath=_log_filepath)

def do_calc_slow(codes, idx, pt, qd):
    # log_handler.info("begin-do-calc %s" % codes)
    threads = []
    for code in codes:
	    threads.append(calcStrategy(code, log_handler, redis, idx))
	    # threads.append(calcStrategy(code, idx))

    for c in threads:
        c.start()
    for c in threads:
        c.join()

    # log_handler.info("end-do-calc %s" % codes)

def do_calc(code, idx, pt, qd):
    # log.info("do calc")
    # print("start do-calc")
    data_df = redis.get_day_df(code, idx=idx)
    out = pt.check(data_df.close,data_df.high, data_df.low)
    if out['flg']:
        # log.info(" data risk => code=%s , value= %s " %  (code, out))
        log_handler.info(" data risk => code=%s , value= %s " %  (code, out))

    # self.log.info("begin calc %s" % self.code)
    if qd.check(data_df.close):
        # log.info(" data market start=>code=%s" % code )
        log_handler.info(" data market start=>code=%s" % code )


class Strategy(StrategyTemplate):
    name = 'data-worker2'
    data_flg = "data-sina"
    EventType = 'worker'
    config_name = './config/stock_list.json'
    idx=0

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
        self.pt = UdfIndexRisk()
        self.qd = UdfMarketStart()
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
        self.log.info('\nStrategy =%s, event_type=%s' %(self.name, event.event_type))
        pool = Pool(cpu_count())
        self.is_working = True

        for stcode in self.code_list:
            pool.apply_async(do_calc, args=(stcode, self.idx, self.pt, self.qd))

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
        self.log.info("do-working-end")