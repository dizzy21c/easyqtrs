import os
import sys
import pymongo as mongo
import json
import polars as pl
import numpy as np
from datetime import date, datetime
import time
from time import strftime, localtime
# from QUANTAXIS.QAFetch import QATdx as tdx
from easyquant.easydealutils.easytime import EasyTime
from easyquant.indicator.base4pl import *
from easyquant  import MongoIo4Pl
import re
import talib
from easyquant  import MongoIo

mongoo = MongoIo()
# df = mongoo.get_stock_list()
codelist = list(mongoo.get_stock_list().index)

def codelist2dict(codelist, splitNum = 4):
    code_len = len(codelist)
    if splitNum <= 1 or code_len < splitNum :
        return {0: codelist}

    subcode_len = math.ceil(code_len / splitNum)
    code_dict = {}
    for i in range(subcode_len + 1):
        for j in range(splitNum):
            x = (i * splitNum) + j
            if x < code_len:
                if j in code_dict.keys():
                    # code_dict[j].append(codelist[x])
                    code_dict[j] = code_dict[j] + [codelist[x]]
                else:
                    code_dict[j] = [codelist[x]]
    return code_dict

from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor,as_completed
pool_size = cpu_count()
limit_len = 0

databuf_mongo = {}
data_buf_stockinfo = {}
code_list_dict = {}

def do_get_data_mp(key, codelist, st_start, st_end, type=''):
    mongo_mp = MongoIo4Pl()
    databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end=st_end)
    print("do_get_data_mp ... ", key, len(databuf_mongo[key]))
#     for code in codelist:
    data_buf_stockinfo[0] = mongo_mp.get_stock_info(code = None)


def get_data(codelist, st_start, st_end, type):
    start_t = datetime.datetime.now()
    print("begin-get_data:", start_t)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    # codelist = ['600380','600822']

#     pool_size = cpu_count()
    task_list = []
    limit_len = 0
    code_dict = codelist2dict(codelist, pool_size)
    executorGetData = ThreadPoolExecutor(max_workers=len(code_dict))
    # print("get-data", code_dict)
#     pool = Pool(cpu_count())
    for i in code_dict.keys():
        code_list_dict[i] = code_dict[i]
        task_list.append(executorGetData.submit(do_get_data_mp, i, code_dict[i], st_start, st_end, type))
#         task_list.executor(do_get_data_mp, args=(i, code_dict[i], st_start, st_end, type))

    for task in as_completed(task_list):
        # result = task.result()
        pass
    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))
    
codelist = list(mongoo.get_stock_list().index)
get_data(codelist, st_start = '2018-12-12', st_end = '2030-12-31', type = 'B')

