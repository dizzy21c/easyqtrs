# coding: utf-8
from threading import Thread, current_thread, Lock
import datetime
import time

class CalcWorker(Thread):
    dataType = 0
    workType = "calc" # data, calc
    log = None
    redisIo = None
    chkData = None
    last_time = None
    last_vol = 0
	
    def __init__(self, code, sina_data):
        Thread.__init__(self)
        self.code = code
        self.data = sina_data
        #self.dataType = 0 # 0 normal 1 index
        
    def run(self):
      self.save_data()
      self.calc()

    def init(self):
        pass

    def calc(self):
        pass

    def save_data(self): #, data, idx=0):
        if self.workType != "data":
            return

        ct=time.strftime("%H:%M:%S", time.localtime()) 
        if self.last_time == self.data['time']:
            return
        self.last_time = self.data['time']
        if self.last_vol == 0:
            curtime=datetime.datetime.now().strftime('%H:%M:%S') #'%Y-%m-%d %H:%M:%S'
            if (curtime > "09:31:00" or curtime > "13:00:00"):
                self.last_vol = 100

        self.redis.push_cur_data(self.code, self.data, self.dataType, self.last_vol)
        self.last_vol = self.data['volume']