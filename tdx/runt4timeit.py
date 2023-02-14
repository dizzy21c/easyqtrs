import QUANTAXIS as qa
from pymongo import MongoClient
import pymongo
import pandas as pd
import datetime
import codecs
import copy
import csv
import datetime
import os
import struct
import sys
import time
import math
import timeit
from pymongo import MongoClient
import pymongo
import datetime

from QUANTAXIS.QAUtil import (
    QA_util_get_real_date,
    QA_util_to_json_from_pandas,
    trade_date_sse
)

# 根据二进制前两段拿到日期分时
def get_date_str(h1, h2) -> str:  # H1->0,1字节; H2->2,3字节;
    year = math.floor(h1 / 2048) + 2004  # 解析出年
    month = math.floor(h1 % 2048 / 100)  # 月
    day = h1 % 2048 % 100  # 日
    hour = math.floor(h2 / 60)  # 小时
    minute = h2 % 60  # 分钟
    if hour < 10:  # 如果小时小于两位, 补0
        hour = "0" + str(hour)
    if minute < 10:  # 如果分钟小于两位, 补0
        minute = "0" + str(minute)
    return str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(minute)

def read_min_file(file_name: str, stock_code: str):
    if not file_name:
        return []
    data_list = []
    with open(file_name, 'rb') as stock_file:
        buffer = stock_file.read()  # 读取数据到缓存
        total_size = len(buffer)
        row_size = 32  # 通信达day数据，每32个字节一组数据
        for seg in range(0, total_size, row_size):  # 步长为32遍历buffer
            row = list(struct.unpack('HHffffllf', buffer[seg: seg + row_size]))
            date_str = get_date_str(row[0], row[1])  # 解析日期和分时
            row[0] = stock_code
            row[1] = date_str
#             row[1] = row[1] / 100
#             row[2] = row[2] / 100
#             row[3] = row[3] / 100
#             row[4] = row[4] / 100
            row.pop()  # 移除最后无意义字段
#             row.insert(0, stock_code)
            data_list.append(row)
    return data_list

def read_day_file(file_name: str, stock_code: str, begin=19900101):
    if not file_name:
        return []
    if begin == None:
        begin = 19900101
    columns = ['code', 'tradeDate', 'open', 'high', 'low', 'close', 'amount', 'vol']
    data_list = []
    # data_list = []
    with open(file_name, 'rb') as stock_file:
        buffer = stock_file.read()  # 读取数据到缓存
        total_size = len(buffer)
        row_size = 32  # 通信达day数据，每32个字节一组数据
        for seg in range(0, total_size, row_size):  # 步长为32遍历buffer
            row = list(struct.unpack('IIIIIfII', buffer[seg: seg + row_size]))
            if row[0] <= begin:
                # print(row[0])
                continue
            row[1] = row[1] / 100 #open
            row[2] = row[2] / 100
            row[3] = row[3] / 100
            row[4] = row[4] / 100 #
            row[6] = row[6] / 100 #vol
            row.pop()  # 移除最后无意义字段
            row.insert(0, stock_code)
            data_list.append(row)
    return data_list

def readData(code: str, codePath :str, strDate: str):
    fileTmpl = "%s/vipdoc/%s/lday/%s%s.day"
    if code[:1] == '6':
        file_name = fileTmpl % (codePath, 'sh', 'sh', code)
    else:
        file_name = fileTmpl % (codePath, 'sz', 'sz', code)
#     print(int(strDate.replace("-","")))
    data_list = read_day_file(file_name, code, int(strDate.replace("-","")))
    if len(data_list) > 0:
        data=pd.DataFrame(data=data_list,columns=['code','date','open','high','low','close','amount','vol'])
        data['date'] = data['date'].apply(lambda x: datetime.datetime.strptime(str(x),'%Y%m%d').date())
        data['date_stamp'] = data['date'].apply(lambda x: time.mktime(time.strptime(str(x), '%Y-%m-%d')))
#         data=data.set_index(['date'], drop=False)
    else:
        data = pd.DataFrame()
    return data

def now_time():
    return str(QA_util_get_real_date(str(datetime.date.today() - datetime.timedelta(days=1)), trade_date_sse, -1)) + \
           ' 17:00:00' if datetime.datetime.now().hour < 15 else str(QA_util_get_real_date(
        str(datetime.date.today()), trade_date_sse, -1)) + ' 15:00:00'
#     return str(datetime.date.today())
def QA_SU_save_stock_day(client, tdxPath):
    stock_list = qa.QA_fetch_get_stock_list('tdx').code.unique().tolist()
    coll_stock_day = client.stock_day
    coll_stock_day.create_index(
        [("code",
          pymongo.ASCENDING),
         ("date_stamp",
          pymongo.ASCENDING)]
    )
    err = []

    def __saving_work(code, coll_stock_day):
        try:
            # 首选查找数据库 是否 有 这个代码的数据
            ref = coll_stock_day.find({'code': str(code)[0:6]})
            end_date = str(now_time())[0:10]

            # 当前数据库已经包含了这个代码的数据， 继续增量更新
            # 加入这个判断的原因是因为如果股票是刚上市的 数据库会没有数据 所以会有负索引问题出现
            if ref.count() > 0:
                # 接着上次获取的日期继续更新
                start_date = ref[ref.count() - 1]['date']
            else:
                start_date = '1990-01-01'
            df = readData(code,strDate=start_date, codePath=tdxPath)
            if len(df) > 0:
                print("insert data : %s" % code)
                coll_stock_day.insert_many(
                    QA_util_to_json_from_pandas(df)
                )
        except Exception as error0:
            print(error0)
            err.append(str(code))

    for item in range(len(stock_list)):
        __saving_work(stock_list[item], coll_stock_day)

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 2:
        print('python runt4timeit.py C:/soft/new_tdx')
        exit()
    package='tdx'
    client = MongoClient('localhost', 27017)
    db = client['quantaxis']
    QA_SU_save_stock_day(db,sys.argv[1])