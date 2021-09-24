from easyquant import StrategyTemplate
from easyquant import RedisIo
from threading import Thread, current_thread, Lock
import json
import redis
import time
#import pymongo
#import pandas as pd
import numpy as np
import talib

class calcStrategy(Thread):
    def __init__(self, code, ndata, log, redisIo, hdata):
        Thread.__init__(self)
        self.data = ndata
        self.code = code
        self.log = log
        self.rio = redisIo
        self.hdata = hdata
        # self._chkv = hdata[1]
        # log.info("code=%s, code=%s"%(code, code[2:]))
        # data=mdb['index_day'].find({'code':code[2:]})
        # self._df = pd.DataFrame(list(data))
        # self.rdata = hdata[2]

        #{'name': '"', 'open': 11.19, 'close': 11.1, 'now': 11.47, 'high': 11.63, 'low': 11.19, 'buy': 11.46, 'sell': 11.47, 'turnover': 54845630, 'volume': 629822482.49, 'bid1_volume': 52700, 'bid1': 11.46, 'bid2_volume': 94600, 'bid2': 11.45, 'bid3_volume': 10900, 'bid3': 11.44, 'bid4_volume': 40700, 'bid4': 11.43, 'bid5_volume': 60500, 'bid5': 11.42, 'ask1_volume': 5200, 'ask1': 11.47, 'ask2_volume': 70600, 'ask2': 11.48, 'ask3_volume': 116300, 'ask3': 11.49, 'ask4_volume': 248000, 'ask4': 11.5, 'ask5_volume': 26200, 'ask5': 11.51, 'date': '2019-04-08', 'time': '14:12:33'}


        # self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def run(self):
        # pass
        # time.sleep(1)
        # print (type(self._data))
        # self.redis.hmset(self._code, self._data)
        cc=self.data['now']
        chgValue = (self.data['now'] - self.data['close'])
        # downPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # chkVPct =  ( self._data['now'] - self._chkv  ) * 100 / self._chkv
        pct = chgValue * 100 / self.data['close']
        hp = self.data['high'] - self.data['close']
        lp = self.data['low'] - self.data['close']
        cp= self.data['now'] - self.data['close']
        #cs = pd.Series({'close':self._data['close']})
        # ma20 = talib.MA(np.array(self.rdata),20)
        # self.rdata.append(cc) 
        #save_csv= self.rdata.append(cs, ignore_index=True)
        #idx = self.ddata.index.values.size - 1
        # ma202 = talib.MA(np.array(self.rdata),20)
        #ma202 = talib.MA(np.array(df2),20)
        # self.rdata.pop()
        #path='/home/zhangjx/backup/bk/easyquant/datas/%s-%d.txt'
        #df2.to_csv(path % (self._code, 1),index=False,sep=',')
        #save_csv.to_csv(path % (self._code, 2),index=False,sep=',')
        # print ("code=%s now=%6.2f pct=%6.2f hl=%6.2f" % ( self._code, self._data['now'], pct, downPct))
        # self._log.info("code=%s now=%6.2f pct=%6.2f pctv2=%6.2f" % ( self._code, self._data['now'], pct, chkVPct))
        #if pct > 0.2 or pct < -0.2 :
        # self.log.info(self.code)
        # self.log.info(self.hdata.keys())
        
        # if self.code in self.hdata.keys():
        #     hd = self.hdata[self.code]
            # ma20 = talib.MA(np.array(hd),20)
            # self.log.info(hd)
            # ma20 = 0
            # self.log.info("code=%s now=%6.2f pct=%6.2f cp=%6.2f hp=%6.2f  lp=%6.2f " % (self.code, self.data['now'], pct, cp, hp, ma20))
            # self._log.info("code=%s now=%6.2f pct=%6.2f cp=%6.2f hp=%6.2f  lp=%6.2f " % (self._code, self._data['now'], pct, ma20[-1], ma202[-1], 0))

class Strategy(StrategyTemplate):
    name = 'watch-index-save'

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        self.hdata={}
        # self.hdata= {}
        # start_date = '2018-01-01'
        config_name = './config/worker_list.json'
        self.rio=RedisIo('redis.conf')
        with open(config_name, 'r') as f:
            data = json.load(f)
            # print data
            for d in data['chk-index']:
                #rdata=db.lrange("%s:idx:day:close"%d['c'][2:],0,-1)
                #rlist=[json.loads(v.decode()) for v in rdata]
                rlist=self.rio.get_day_c(d['c'])
                self.hdata[d['c']] = rlist
                # self.chks.append((d['c'], d['p'],rlist))
                #dtd=mdb['index_day'].find({'code':d['c'][2:],'date':{'$gt':start_date}})
                #dfd=pd.DataFrame(list(dtd))
                #dfd=[]
                #rda=pd.DataFrame(columns=('time','price','vol'))
                #self.hdata[d['c']] = [dfd,rda]
                # print d['c']

        #self.log.info('\n\nStrategy index event')
    def strategy(self, event):
        if event.event_type != 'index-sina':
            return

        # self.log.info('\nStrategy =%s, event_type=%s' %(self.name, event.event_type))
        # chklist = ['002617','600549','300275','000615']
        # print  (type(event.data))
        threads = []
        # [calcStrategy(l) for i in range(5)]
        #for td in event.data:
        #    self.log.info(td)
        for stcode in event.data:
            # self.log.info(event.data)
            stdata= event.data[stcode]
            # self.log.info(stdata)
            # rtn=self.summary(data=stdata,org=rtn)
            threads.append(calcStrategy(stcode, stdata, self.log, self.rio, self.hdata))

        # for td in self.chks:
            # if td[0] in event.data:
                # threads.append(calcStrategy(td[0], event.data[td[0]], self.log, td))
            # else:
            #     self.log.info("\n\nnot in data:" + td[0])

        # for d in event.data:
        #     threads.append(calcStrategy(d, event.data[d], self.log))

        for c in threads:
            c.start()

            # chgValue = (event.data[d]['now'] - event.data[d]['close'])
            # self.log.info( "code=%s pct=%6.2f now=%6.2f" % (d, ( chgValue * 100/ event.data[d]['now']), event.data[d]['now']))

        # self.log.info('data: stock-code-name %s' % event.data['162411'])
        # self.log.info('check balance')
        # self.log.info(self.user.balance)
        # self.log.info('\n')

