# coding: utf-8
import os
import sys
import redis
import json
import time
import pandas as pd
import numpy as np

class RedisIo(object):
    """Redis操作类"""
    
    def __init__(self, host="127.0.0.1", port=6379):
        # self.config = self.file2dict(conf)
        # if self.config['passwd'] is None:
        self.r = redis.Redis(host=host, port=port, db=0)
        # else:
        #     self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'], password = self.config['passwd'])
    
    def file2dict(self, path):
        #读取配置文件
        with open(path) as f:
            return json.load(f)
        
    def cleanup(self):
        #清理Redis当前数据库
        self.r.flushdb()

    def lookup_redis_info(self):
        #查询Redis配置
        info = self.r.info()

    def set_key_value(self, key, value):
        #设置键值对key<-->value
        self.r.set(key, value)

    def get_key_value(self, key):
        #查询键值对
        return self.r.get(key)

    def save(self):
        #强行保存数据到硬盘
        return self.r.save()

    def get_keys(self):
        #获取当前数据库里面所有键值
        return self.r.keys()

    def delete_key(self, key):
        #删除某个键
        return self.r.delete(key)

    def pop_list_value(self, listname):
        #推入到队列
        return self.r.lpop(listname)

    def pop_list_rvalue(self, list_name):
        # print("%s=%s" %(list_name, value))
        return self.r.rpop(list_name)

    def rpop(self, list_name):
        # test only
        # print("%s=%s" %(list_name, value))
        value = self.r.rpop(list_name)
        if value is None:
            return ""
        else:
            return value.decode()

    def rpop_min_df(self, code, idx=0, freq=15):
        dtype="m%d" % freq 
        self.rpop(self._get_key(code, dtype=dtype, idx=idx))

    # def rpop_day_df(self, code, dtype="day", idx=0):
    def rpop_day_df(self, code, idx=0):
        dtype="day"
        self.rpop(self._get_key(code, dtype=dtype, idx=idx))

    def get_last_close(self, code, dtype="day", idx=0):
        return self.get_last_data(code, vidx=1, dtype=dtype)

    def get_last_day(self, code, idx=0):
        dtype="day"
        return self.get_last_data(code, vidx=6, dtype=dtype)
    
    def get_last_time(self, code, freq=15, idx=0):
        dtype="m%d" % freq
        return self.get_last_data(code, vidx=7, dtype=dtype)
    
    def get_last_date(self, code, dtype="day", idx=0):
        return self.get_last_data(code, vidx=6, dtype=dtype)
    
    def get_last_data(self, code, vidx=6, dtype="day", idx=0):
        list = self.get_data_value(code, dtype=dtype, startpos=-1, endpos=-1, idx=idx)
        if list == []:
            return None
        else:
            return self.list2ochlvadt(list[0])[vidx]

    def push_list_value(self, listname, value):
        #推入到队列
        return self.r.lpush(listname, value)

    def push_list_rvalue(self, list_name, value):
        # print("%s=%s" %(list_name, value))
        return self.r.rpush(list_name, value)

    def pull_list_range(self, listname, starpos=0, endpos=-1):
        #获取队列某个连续片段
        return self.r.lrange(listname, starpos, endpos)

    def get_list_len(self, listname):
        #获取队列长度
        return self.r.llen(listname)

    def set_cur_data(self, code, data, idx=0):
        dtype = "now"
        listname=self._get_key(code,dtype,idx)
        if isinstance(data, dict):
            self.set_key_value(listname, str(data))
        else:
            self.set_key_value(listname, data)


    def get_cur_data(self, code, idx=0):
        dtype = "now"
        listname=self._get_key(code,dtype,idx)
        sina_data = self.get_key_value(listname)
        str = sina_data.decode('utf8').replace('"','').replace('\'','"')
        return json.loads(str)

    def push_buy(self, code, data):
        # dtype = "buy"
        lc = self.get_last_close(code)
        # if lc == data['now']:
        self.push_options_value(code, data) #, dtype=dtype, idx=0)

    def push_sell(self, code, data):
        dtype = "buy"
        self.push_data_value(code, data, dtype=dtype, idx=0)

    def push_min_data(self, code, data, idx=0, freq=15):
        last_date = self.get_last_time(code, freq=freq, idx=idx)
        # self.set_read_flg(code, value=0)
        if last_date == data['datetime']:
            self.rpop_min_df(code, idx=idx)

        self.push_data_value(code, data, idx=idx, dtype="m%d"%freq)
        # self.set_log_date(code, data, idx = idx)

    def push_day_data(self, code, data, idx=0):
        last_date = self.get_last_day(code, idx=idx)
        # self.set_read_flg(code, value=0)
        if last_date == data['date']:
            self.rpop_day_df(code, idx=idx)

        self.push_data_value(code, data, idx=idx)
        # self.set_log_date(code, data, idx = idx)

    def dict2ochlvadtl(self, data, last_vol = 0, last_amount = 0):
        ##      O  C  H  L  V  A D T
        rtn = "%s|%s|%s|%s|%s|%s" % (data['open'],data['now'],data['high'],data['low'],data['turnover'] / 100 - last_vol, data['volume'] - last_amount)
        rtn = "%s|%s|%s %s|%s" % (rtn, data['date'], data['date'],data['time'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        return rtn

    def dict2ochlvadt(self, data, last_vol = 0, last_amount = 0):
        ##      O  C  H  L  V  A #D#
        rtn = "%s|%s|%s|%s|%s|%s" % (data['open'],data['now'],data['high'],data['low'],data['turnover'] / 100 - last_vol, data['volume'] - last_amount)
        if 'time' in data.keys():
            rtn = "%s|%s|%s %s" % (rtn, data['date'], data['date'],data['time'])
        else:
        # elif 'datetime' in data.keys():
            rtn = "%s|%s|%s" % (rtn, data['date'], data['datetime'])
        # else:
            # rtn = "%s|%s" % (rtn, data['date'])
        return rtn

    def list2ochlvadt(self, data):
        rtn = []
        for ns in data.split('|'):
            if "-" in ns: # 2019-12-31 [12:59:59]
                rtn.append(ns)
            else:
                rtn.append(float(ns))
        return rtn

    def push_data_value(self, code, data, dtype='day', idx=0, last_vol = 0, last_amount = 0):
        listname=self._get_key(code,dtype,idx)
        value = self.dict2ochlvadt(data, last_vol, last_amount)
        self.push_list_rvalue(listname, value)

    def push_options_value(self, code, data, dtype='buy'):
        listname=self._get_key(code,dtype,0)
        value = self.dict2ochlvadtl(data, 0, 0)
        self.push_list_rvalue(listname, value)

    
    def _get_key(self, code, dtype='day', idx=0):
        if idx==0:
            return "%s:%s"%(code, dtype)
        else:
            return "%s:idx:%s"%(code, dtype)

    def _get_str_data(self, listname, startpos=0, endpos=-1):
        rl = self.pull_list_range(listname, startpos, endpos) 
        return [v.decode() for v in rl]

    def _get_num_data(self, listname, startpos=0, endpos=-1):
        rl = self.pull_list_range(listname, startpos, endpos) 
        return [json.loads(v.decode()) for v in rl]
    
    def calc_pct(self, C, O):
        ldf = len(C)
        if ldf < 1:
            return 0.0
        
        close = C.iloc[ldf - 1]
        if ldf == 1:
            pclose = O[0] 
        else:
            pclose = C.iloc[ldf - 2]
        chgValue = close - pclose
        pct = chgValue * 100 / pclose
        return pct
        
    def get_day_ps(self, data_df, sdata):
        def_ps = pd.Series()
        if sdata['open'] <= 0:
           return def_ps

        len_d = len(data_df)
        if len_d <= 0:
           return def_ps
        C = data_df.close.append(pd.Series([sdata['now']], index=[len_d]))
        return C
        

    def get_day_ps_chl(self, data_df, sdata):
        def_ps = pd.Series()
        if sdata['open'] <= 0:
           return def_ps, def_ps, def_ps

        len_d = len(data_df)
        if len_d <= 0:
           return def_ps, def_ps, def_ps

        C = data_df.close.append(pd.Series([sdata['now']], index=[len_d]))
        H = data_df.high.append(pd.Series([sdata['high']], index=[len_d]))
        L = data_df.low.append(pd.Series([sdata['low']], index=[len_d]))
        return C,H,L

    def get_day_ps_ochlva(self, data_df, sdata):
        C,H,L = self.get_day_ps_chl(data_df, sdata)
        len_d = len(C)
        if len_d <= 0:
           return C,C,C,C,C,C

        O = data_df.open.append(pd.Series([sdata['open']], index=[len_d]))
        V = data_df.vol.append(pd.Series([sdata['turnover']], index=[len_d]))
        A = data_df.amount.append(pd.Series([sdata['volume']], index=[len_d]))
        return O,C,H,L,V,A

    def get_min_df(self, code, startpos=0, endpos=-1,idx=0, freq=15):
        return self.get_data_df(code, dtype="m%d"%freq, startpos=startpos, endpos=endpos, idx=idx)

    def get_day_df(self, code, startpos=0, endpos=-1,idx=0):
        return self.get_data_df(code, dtype="day", startpos=startpos, endpos=endpos, idx=idx)

    def get_data_df(self, code, dtype="day", startpos=0, endpos=-1, idx=0):
        data = self.get_data_value(code, dtype=dtype, startpos=startpos, endpos=endpos, idx=idx)
        o = []
        c = []
        h = []
        l = []
        v = []
        a = []
        d = []
        t = []
        for nd in data:
            snd = self.list2ochlvadt(nd)
            o.append(snd[0])
            c.append(snd[1])
            h.append(snd[2])
            l.append(snd[3])
            v.append(snd[4])
            a.append(snd[5])
            d.append(snd[6])
            t.append(snd[7])
        # return pd.DataFrame(data={'close':c, 'open':o, 'vol':v, 'high':h, 'low':l,'amount':a, 'date':d})
        # return pd.DataFrame(data={'close':c, 'open':o, 'vol':v, 'high':h, 'low':l,'amount':a, 'date':d, 'datetime':t})
        return pd.DataFrame(data={'close':c, 'open':o, 'vol':v, 'high':h, 'low':l,'amount':a, 'date':t})

    def get_data_value(self, code, dtype='day', startpos=0, endpos=-1, idx=0):
        listname=self._get_key(code,dtype,idx)
        return self._get_str_data(listname, startpos, endpos)
   
def main():
    ri = RedisIo()
    ri.lookup_redis_info()
    ri.set_key_value('test1', 1)
    ri.push_list_value('test2', 1)
    ri.push_list_value('test2', 2)

if __name__ == '__main__':
    main()
