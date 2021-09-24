from easyquant import StrategyTemplate
from easyquant import UdfIndexRisk
from easyquant import UdfMarketStart
from easyquant import DataUtil
from easyquant import RedisIo
from threading import Thread, current_thread, Lock, Event
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
        # self.data_map = his_data
        self.code = code
        self.log = log
        self.redis = redisIo
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
            self.log.info("data-data read error:code=%s" % self.code)
            return

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
        # data_df = self.redis.get_day_df(self.code, idx=self.idx)
        # data_map = self.data_util.df2series(data_df)
        C, H, L, O, V, D = self.data_util.append2series(self.data_map, self.data)
        # # C = H = L = []
        out = self.pt.check(C,H,L)
        # out = {'flg':0}
        if out['flg']:
            self.log.info(" data risk => code=%s , value= %s " %  (self.code, out))
        # # self.log.info(" code=%s , value= %s " %  (self.code, out))

        # self.log.info("begin calc %s" % self.code)
        if self.qd.check(C):
            self.log.info(" data market start=>code=%s" % self.code )

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()        # 设置为False

class Strategy(StrategyTemplate):
    name = 'data-risk'
    data_flg = "data-sina"
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
        self.hdata[code] = data_map

    def strategy(self, event):
        if event.event_type != 'data-sina':
            return

        self.log.info('\nStrategy =%s, event_type=%s' %(self.name, event.event_type))
        # chklist = ['002617','600549','300275','000615']
        # print  (type(event.data))
        threads = []
        # [calcStrategy(l) for i in range(5)]
        #for td in event.data:
        #    self.log.info(td)
        # for stcode in event.data:
        #     stdata= event.data[stcode]
        #     # rtn=self.summary(data=stdata,org=rtn)
        #     threads.append(calcStrategy(stcode, stdata, self.log, self.hdata[stcode], self.rio, idx=1))

        # for td in self.chks:
            # if td[0] in event.data:
                # threads.append(calcStrategy(td[0], event.data[td[0]], self.log, td))
            # else:
            #     self.log.info("\n\nnot in data:" + td[0])

        for stcode in self.code_list:
            # stdata= event.data[stcode]
            threads.append(calcStrategy(stcode, None, self.log, self.rio, self.idx))

        for c in threads:
            c.start()
        #     c.set_data_resume(event.data)

            # chgValue = (event.data[d]['now'] - event.data[d]['close'])
            # self.log.info( "code=%s pct=%6.2f now=%6.2f" % (d, ( chgValue * 100/ event.data[d]['now']), event.data[d]['now']))

        # self.log.info('data: stock-code-name %s' % event.data['162411'])
        # self.log.info('check balance')
        # self.log.info(self.user.balance)
        # self.log.info('\n')

