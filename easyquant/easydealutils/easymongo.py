# coding: utf-8
import os
import sys
import pymongo as mongo
import json
import pandas as pd
import numpy as np
from datetime import date, datetime
import time
from time import strftime, localtime
from QUANTAXIS.QAFetch import QATdx as tdx
from easyquant.easydealutils.easytime import EasyTime
import re
class MongoIo(object):
    """Redis操作类"""
    
    def __init__(self, host='mgdb', port=27017, database='quantaxis'):
        # self.config = self.file2dict(conf)
        client = mongo.MongoClient(host, port)
        self.db = client[database]
        self.st_start = '2018-01-01'
        # self.st_end = '2030-12-31'
        self.st_start_1min = '2020-01-01'
        self.st_start_5min = '2020-01-01'
        self.st_start_15min = '2020-01-01'
        self.st_start_30min = '2020-01-01'
        self.st_start_60min = '2020-01-01'
        # self.st_end_day = '2030-12-31'
        # if self.config['passwd'] is None:
        #     self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'])
        # else:
        #     self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'], password = self.config['passwd'])

    def dateStr2stamp(self, dateObj):
        dateStr = str(dateObj)[0:10]
        date = time.mktime(time.strptime(dateStr, '%Y-%m-%d'))
        return date

    def datetimeStr2stamp(self, dateObj):
        dataTimeStr = str(dateObj)[0:19]
        date = time.mktime(time.strptime(dataTimeStr, '%Y-%m-%d %H:%M:%S'))
        return date

    def _get_data_day(self, code, table, st_start, st_end):
        cursor = self.db[table].find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": self.dateStr2stamp(st_end),
                        "$gte": self.dateStr2stamp(st_start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        # if format in ['P', 'p', 'pandas', 'pd']:
        return res
        # elif format in ['json', 'dict']:
        #     return QA_util_to_json_from_pandas(res)
        # # 多种数据格式
        # elif format in ['n', 'N', 'numpy']:
        #     return numpy.asarray(res)
        # elif format in ['list', 'l', 'L']:
        #     return numpy.asarray(res).tolist()
        # else:
        #     print(
        #         "QA Error QA_fetch_stock_day format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
        #         % format
        #     )
        #     return None


    def _get_data_min(self, code, table, st_start, st_end, type):
        cursor = self.db[table].find(
            {
                'code': {
                    '$in': code
                }
                , "time_stamp":
                    {
                        "$lte": self.dateStr2stamp(st_end),
                        "$gte": self.dateStr2stamp(st_start)
                    }
                , 'type': type
            },
            {"_id": 0},
            batch_size=10000
        )
        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['datetime',
                                'code'])).query('volume>1').set_index(
                'datetime',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'datetime'
                  ]]
        except:
            res = None
        # if format in ['P', 'p', 'pandas', 'pd']:
        return res
        # elif format in ['json', 'dict']:
        #     return QA_util_to_json_from_pandas(res)
        # # 多种数据格式
        # elif format in ['n', 'N', 'numpy']:
        #     return numpy.asarray(res)
        # elif format in ['list', 'l', 'L']:
        #     return numpy.asarray(res).tolist()
        # else:
        #     print(
        #         "QA Error QA_fetch_stock_day format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
        #         % format
        #     )
        #     return None

    def _get_data2(self, code, table, st_start, st_end, type='D'):
        if st_end is None:
            # st_end = "2030-12-31"
            st_end = "2030-12-31 23:59:59"
        # st_start = self.dateStr2stamp(st_start)
        if type == 'D':
            if isinstance(code, list):
                dtd = self.db[table].find({
                    'code':
                        {'$in': code}
                    , 'date_stamp':
                        {'$gte': self.dateStr2stamp(st_start), "$lte": self.dateStr2stamp(st_end)}
                }
                    , {"_id": 0})
            else:
                dtd = self.db[table].find({'code': code,
                                           'date_stamp':
                                               {'$gte': self.dateStr2stamp(st_start),
                                                "$lte": self.dateStr2stamp(st_end)}
                                           }
                                          , {"_id": 0})
        else:
            if isinstance(code, list):
                dtd = self.db[table].find({'code': {'$in': code}, 'date': {'$gte': self.dateStr2stamp(st_start),
                                                                           "$lte": self.dateStr2stamp(st_end)},
                                           'type': type}, {"_id": 0})
            else:
                dtd = self.db[table].find(
                    {'code': code, 'date': {'$gte': self.dateStr2stamp(st_start), "$lte": self.dateStr2stamp(st_end)},
                     'type': type}, {"_id": 0})
        ptd = pd.DataFrame(list(dtd))
        if len(ptd) > 0:
            # del ptd['_id']
            del ptd['date_stamp']
            if type == 'D':
                ptd.date = pd.to_datetime(ptd.date)
                ptd = ptd.set_index(["date", "code"])
            else:
                ptd.date = pd.to_datetime(ptd.date)
                ptd.datetime = pd.to_datetime(ptd.datetime)
                ptd = ptd.set_index(["datetime", "code"])
        # ptd.rename(columns={"vol":"volume"}, inplace=True)
        return ptd

    def _get_data(self, code, table, st_start, st_end, type='D'):
        if st_end is None:
            # st_end = "2030-12-31"
            st_end = "2030-12-31 23:59:59"
        # st_start = self.dateStr2stamp(st_start)
        if type == 'D':
            data = self._get_data_day(code, table, st_start, st_end)
        else:
            data = self._get_data_min(code, table, st_start, st_end, type)
            # if isinstance(code, list):
            #     dtd=self.db[table].find({'code':{'$in':code},'date':{'$gte':self.dateStr2stamp(st_start), "$lte":self.dateStr2stamp(st_end)}, 'type':type},{"_id": 0})
            # else:
            #     dtd=self.db[table].find({'code':code,'date':{'$gte':self.dateStr2stamp(st_start), "$lte":self.dateStr2stamp(st_end)}, 'type':type},{"_id": 0})
        # ptd=pd.DataFrame(list(dtd))
        if data is None:
            return pd.DataFrame()

        if len(data) > 0:
            # del ptd['_id']
            # del ptd['date_stamp']
            if type == 'D':
                data.date = pd.to_datetime(data.date)
                data = data.set_index(["date","code"])
            else:
                # data.date = pd.to_datetime(data.date)
                data.datetime= pd.to_datetime(data.datetime)
                data = data.set_index(["datetime","code"])
        # ptd.rename(columns={"vol":"volume"}, inplace=True)
        return data
    
    def get_stock_day(self, code, st_start=None, st_end=None):
        if st_start is None:
            st_start = self.st_start
        if isinstance(code, str):
            code = [code]
        return self._get_data(code, 'stock_day', st_start, st_end)
  
    def get_stock_min(self, code, st_start=None, st_end=None, freq=5):
        if st_start is None:
            st_start = self.st_start_15min
        if isinstance(code, str):
            code = [code]
        return self._get_data(code, 'stock_min', st_start, st_end, "%dmin"%freq)

    def get_stock_min_realtime(self, code, st_start=None, st_end=None, freq=5):
        if st_start is None:
            st_start = self.st_start_5min
        if st_end is None:
            st_end = "2030-12-31 23:59:59"

        data_min = self.get_stock_min(code=code, freq=freq)
        if len(data_min) > 0:
            if freq < (time.time() - data_min.index[-1][0].timestamp()) / 60:
                start = data_min.index[-1][0].strftime('%Y-%m-%d %H:%M:01')  ## %S=>01
                add_df = tdx.QA_fetch_get_stock_min(code, start=start, end=st_end, frequence='%dmin' % freq)
                if len(add_df) > 0:
                    add_df.drop(['date_stamp', 'datetime'], axis=1, inplace=True)
                    data_min = data_min.append(add_df, sort=True)
                    ## save to db
        else:
            data_min = tdx.QA_fetch_get_stock_min(code, start=st_start, end=st_end, frequence='%dmin' % freq)
            if len(data_min) > 0:
                data_min.drop(['date_stamp', 'datetime'], axis=1, inplace=True)

        return data_min

    def get_index_day(self, code, st_start=None, st_end=None):
        if st_start is None:
            st_start = self.st_start
        if isinstance(code, str):
            code = [code]
        return self._get_data(code, 'index_day', st_start, st_end)

    def get_index_min(self, code, st_start=None, st_end=None, freq=5):
        if st_start is None:
            st_start = self.st_start_15min
        if isinstance(code, str):
            code = [code]
            
        return self._get_data(code, 'index_min', st_start, st_end, "%dmin"%freq)

    def get_index_min_realtime(self, code, st_start=None, st_end=None, freq=5):
        if st_start is None:
            st_start = self.st_start_5min
        if st_end is None:
            st_end = "2030-12-31 23:59:59"
        
        data_min = self.get_index_min(code=code, freq=freq)
        if len(data_min) > 0:
            if freq < (time.time() - data_min.index[-1][0].timestamp()) / 60:
                start=data_min.index[-1][0].strftime('%Y-%m-%d %H:%M:01') ## %S=>01
                add_df=tdx.QA_fetch_get_index_min(code,start=start,end=st_end, frequence='%dmin' % freq)
                if len(add_df) > 0:
                    add_df.drop(['date_stamp','datetime'],axis=1,inplace=True)
                    data_min=data_min.append(add_df, sort=True)
        else:
            data_min=tdx.QA_fetch_get_index_min(code,start=st_start,end=st_end, frequence='%dmin' % freq)
            if len(data_min) > 0:
                data_min.drop(['date_stamp','datetime'],axis=1,inplace=True)
        
        return data_min

    def file2dict(self, path):
        #读取配置文件
        with open(path) as f:
            return json.load(f)

    def save(self, table, data):
        self.db[table].insert_many(
            [data]
        )

    def save_data_min(self, data, idx=0):
        if idx == 0:
            pass
        else:
            pass

    def save_realtime(self, data):
        table = 'realtime_{}'.format(date.today())
        # self.db[table].insert_many(
        #     [data]
        # )
        self.db[table].replace_one({'_id':data['_id']}, data, True)

    def save_realtime2(self, data):
        table = 'realtime2_{}'.format(date.today())
        # self.db[table].insert_many(
        #     [data]
        # )
        self.db[table].replace_one({'_id':data['_id']}, data, True)

    def upd_data_min(self, df_data_min, json_data, minute):
        # index_time =pd.to_datetime(easytime.get_minute_date(minute=5))
        et = EasyTime()
        index_time = pd.to_datetime(et.get_minute_date_str(minute=minute, str_date=json_data['datetime']))
        begin_time = pd.to_datetime(et.get_begin_trade_date(minute=minute, str_date=json_data['datetime']))
        if len(df_data_min) > 0:
            sum_df=df_data_min.loc[df_data_min.index > begin_time]
            old_vol = sum_df['vol'].sum()
            old_amount = sum_df['amount'].sum()
            now_price = json_data['now']
            if index_time in df_data_min.index:
                if now_price > df_data_min.loc[index_time, 'high']:
                    df_data_min.loc[index_time, 'high'] = now_price
                if now_price < df_data_min.loc[index_time, 'low']:
                    df_data_min.loc[index_time, 'low'] = now_price
                df_data_min.loc[index_time, 'close'] = now_price
                df_data_min.loc[index_time, 'vol'] = json_data['volume'] - old_vol
                df_data_min.loc[index_time, 'amount'] = json_data['amount'] - old_amount
            else:
                # if self.code == '600822':
                #     print("2 code=%s, data=%d" % (self.code, len(df_data_min)))
                df_data_min.loc[index_time] = [0 for x in range(len(df_data_min.columns))]
                df_data_min.loc[index_time, 'code'] = json_data['code']
                df_data_min.loc[index_time, 'open'] = now_price
                df_data_min.loc[index_time, 'high'] = now_price
                df_data_min.loc[index_time, 'low'] = now_price
                df_data_min.loc[index_time, 'close'] = now_price
                df_data_min.loc[index_time, 'vol'] = json_data['volume'] - old_vol
                df_data_min.loc[index_time, 'amount'] = json_data['amount'] - old_amount
        else: ##first day ???
            pass

        return df_data_min
    
    def get_positions(self, idx=0):
        table = 'positions'
        # self.db[table].insert_many(
        #     [data]
        # )
        dtd=self.db[table].find({'amount':{'$gte':0},"idx":idx,'status':'1'})
        ptd=pd.DataFrame(list(dtd))
        if len(ptd) > 0:
            del ptd['_id']
            ptd = ptd.set_index(["code"])
        return ptd

    def get_stock_info(self, code = None):
        table = 'stock_info'
        if code == None:
            dtd = self.db[table].find()
        elif isinstance(code, list):
            # dtd = None
            dtd = self.db[table].find({'code': {'$in':code}})
        else:
            dtd = self.db[table].find({'code': code})
        return pd.DataFrame(list(dtd))

    def get_stock_list(self, code=None, notST = True, market = None):
        table = 'stock_list'
        query = {}
        if market != None:
            query['sse'] = '%s' % market
        if notST:
            # data=m.db['stock_list'].find({"code":{"$in":codelist}, "name":{'$not': re.compile(r"ST")}})
            query['name'] = {'$not': re.compile(r"ST")}
        if code == None:
            # print("get-stock-list", query)
            dtd = self.db[table].find(query)
        elif isinstance(code, list):
            query['code'] = {'$in': code}
            # dtd = self.db[table].find({'code': {'$in':code}})
            dtd = self.db[table].find(query)
        else:
            dtd = self.db[table].find({'code': code})
        pdf = pd.DataFrame(list(dtd))
        pdf = pdf.set_index('code')
        if len(pdf) == 0:
            return pdf
        del pdf['_id']
        del pdf['volunit']
        del pdf['sec']
        del pdf['sse']
        del pdf['decimal_point']
        return pdf

    def get_realtime(self, code = None, dateStr = None, time='09:30:00', beg_time = None):
        if dateStr == None:
            # dateStr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
            dateStr = strftime('%Y-%m-%d',localtime())
        table = 'realtime_%s' % dateStr
        if code == None:
            if beg_time == None:
                dtd = self.db[table].find({'time':{'$lt':time}})
            else:
                dtd = self.db[table].find({'time':{'$lt':time, '$gt':beg_time}})
        elif isinstance(code, list):
            dtd = self.db[table].find({'code':{'$in':code}, 'time':{'$lt':time}})
        else:
            dtd = self.db[table].find({'code':code, 'time':{'$lt':time}})
        df = pd.DataFrame(list(dtd))
        if len(df) > 0:
            df = df.set_index(['_id'])
        return df

    def get_realtime_count(self, dateStr = None):
        if dateStr == None:
            # dateStr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
            dateStr = strftime('%Y-%m-%d',localtime())
        table = 'realtime_%s' % dateStr
        return self.db[table].estimated_document_count()

    def upd_positions(self, code, amount, price):
        table = 'positions'
        # self.db[table].insert_many(
        #     [data]
        # )
        # data = self.db[table].
        # data = list()
        # self.db[table].replace_one({'_id':code}, {'$set':{'trade_amount':amount,'trade_price':price}}, True)
        # data=list(self.db[table].find({'_id':code}))[0]
        data=self.db[table].find_one({'_id':code})
        if data is not None:
            old_trade_amount = data['trade_amount']
            old_trade_price = data['trade_price']
            if old_trade_price == 0:
                data['trade_amount'] = amount
                data['trade_price'] = price
            else:
                data['trade_amount'] = old_trade_amount + amount
                recal_price = ( old_trade_amount * old_trade_price + amount * price ) / (old_trade_amount + amount)
                data['trade_price'] = recal_price
            self.db[table].replace_one({'_id':data['_id']}, data, True)

    def upd_order(self, func_name, dateObj, code, price, bs_flg = 'buy', insFlg = True):
        table = 'st_orders-%s' % func_name
        tax_comm = 1.003
        # self.db[table].insert_many(
        #     [data]
        # )
        # data = self.db[table].
        # data = list()
        # self.db[table].replace_one({'_id':code}, {'$set':{'trade_amount':amount,'trade_price':price}}, True)
        # data=list(self.db[table].find({'_id':code}))[0]
        dataId = "%s-%s" %(str(dateObj)[0:10], code)
        data = self.db[table].find_one({'_id': dataId})
        profi = 0.0
        if data is not None:
            if bs_flg == 'buy':
                data['upd-date'] = datetime.now()
                data['cur-price'] = price
                data['diff-price'] = (price - data['buy-price'] * tax_comm) / data['buy-price'] * 100
                profi = data['diff-price']
            else:
                data['upd-date'] = datetime.now()
                data['sell-price'] = price
                data['sell-date'] = dateObj
                data['diff-price'] = (price - data['buy-price'] * tax_comm) / data['buy-price'] * 100
                profi = data['diff-price']
            self.db[table].replace_one({'_id': data['_id']}, data, True)
        else:
            if insFlg and bs_flg == 'buy':
                data = {}
                data['_id'] = dataId
                data['code'] = code
                data['ins-date'] = datetime.now()
                data['buy-date'] = dateObj
                data['buy-price'] = price
                data['cur-price'] = price
                data['sell-price'] = 0.0
                data['diff-price'] = (tax_comm - 1) * 100
                profi = data['diff-price']
                self.db[table].insert(data)

        return profi

    def upd_sell_order(self, func_name, code, price, upd_date):
        table = 'st_orders-%s' % func_name
        tax_comm = 1.003
        datas = self.db[table].find({'code': code})
        dc = datas.count()
        i = 0
        profi = 0.0
        for data in datas:
            i = i + 1
            if i == dc:
                data['upd-date'] = upd_date
                # data['buy-time'] = data['buy-date'][11:]
                data['cur-price'] = price
                data['pct-price'] = (price - data['buy-price'] * tax_comm) / data['buy-price'] * 100
                profi = data['pct-price']
                self.db[table].replace_one({'_id': data['_id']}, data, True)
        return profi

    def upd_order_hist(self, func_name, code, price, openPrice, upd_date):
        table = 'st_orders-%s' % func_name
        tax_comm = 1.003
        datas = self.db[table].find({'code': code})
        for data in datas:
            data['upd-date'] = upd_date
            data['buy-time'] = data['buy-date'][11:]
            data['cur-price'] = price
            data['diff-price'] = (price - data['buy-price'] * tax_comm) / data['buy-price'] * 100
            data['diff-oprice'] = (openPrice - data['buy-price'] * tax_comm) / data['buy-price'] * 100
            self.db[table].replace_one({'_id': data['_id']}, data, True)

def main():
    md = MongoIo()
    md.get_stock_day('000001')
    # d.head

if __name__ == '__main__':
    main()
