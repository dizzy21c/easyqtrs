from easyquant import MongoIo
from multiprocessing import Pool
import time
import pymongo as mongo
import datetime

import numpy
import pandas as pd
import QUANTAXIS as QA

from pandas import DataFrame
#
# # mongo=MongoIo()
# PAGE_SUM=100
# def to_mongo_pool(pageNum):
#     # pass
#     mongo = MongoIo()
#     # print("teset")
#     data={"positionId":pageNum, "data":"data=%d" % pageNum}
#     save_to_mongo(mongo, data)
#
# def save_to_mongo(mongo, data):
#     db = mongo.db
#     if db["test-mp"].update_one({'positionId': data['positionId']}, {'$set': data}, True):
#         print('Saved to Mongo', data['positionId'])
#     else:
#         print('Saved to Mongo Failed', data['positionId'])
#
# start_time = time.time()
# pool = Pool()
#
# pool.map(to_mongo_pool,[i for i in range(PAGE_SUM)])
#
# pool.close()
#
# pool.join()
#
# end_time = time.time()
#
# print("总耗费时间%.2f秒" % (end_time - start_time))
host='127.0.0.1'
port=27017
database='quantaxis'
client = mongo.MongoClient(host, port)
db = client[database]
st_start = '2020-01-01'
st_end = '2030-12-31'


def QA_util_date_stamp(date):
    """
    explanation:
        转换日期时间字符串为浮点数的时间戳

    params:
        * date->
            含义: 日期时间
            类型: str
            参数支持: []

    return:
        time
    """
    datestr = str(date)[0:10]
    date = time.mktime(time.strptime(datestr, '%Y-%m-%d'))
    return date


def get_data1(code, table = 'stock_day', st_start = st_start, st_end = st_end, type='D'):
    if st_end is None:
        # st_end = "2030-12-31"
        st_end = "2030-12-31 23:59:59"
    if type == 'D':
        if isinstance(code, list):
            dtd = db[table].find({
                'code': {'$in': code}
                # , 'date': {'$gte': st_start, "$lte": st_end}
                ,"date_stamp":
                {
                    "$lte": QA_util_date_stamp(st_end),
                    "$gte": QA_util_date_stamp(st_start)
                }

                }
                , {"_id": 0})
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

def get_data2(code, table = 'stock_day', start = st_start, end = st_end):
    cursor = db[table].find(
        {
            'code': {
                '$in': code
            },
            "date_stamp":
                {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)
                }
        },
        {"_id": 0},
        batch_size=10000
    )
    # res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

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



codes_df = QA.QA_fetch_stock_list_adv()
code_list = list(codes_df['code'])

start_t = datetime.datetime.now()
print("get_data-begin-time1:", start_t)

data = get_data1(code_list)
data = data.sort_index()
print(len(data))
# print(data.tail(20))
end_t = datetime.datetime.now()
print(end_t, 'get_data-spent1:{}'.format((end_t - start_t)))

start_t = datetime.datetime.now()
print("get_data-begin-time2:", start_t)

data = get_data2(code_list)
data = data.sort_index()
print(len(data))
# print(data.tail(20))
end_t = datetime.datetime.now()
print(end_t, 'get_data-spent2:{}'.format((end_t - start_t)))
