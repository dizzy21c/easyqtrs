import os
import struct
import pandas as pd
import numpy as np
import time, datetime
import sys, getopt
# import multiprocessing
# import talib as tdx
import QUANTAXIS as QA
import math

from easyquant import MongoIo
import matplotlib.pyplot as plt
from multiprocessing import Process, Pool, cpu_count, Manager
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed

# from easyquant.indicator.base import *
# import QUANTAXIS as QA

import talib
import matplotlib.ticker as ticker
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import mplfinance as mpf
from matplotlib import gridspec
from gannCheck import *


def doForcastMP(idx, baseDate, delta, predict):
    start_t = datetime.datetime.now()
    print("begin-doForcastMP :", start_t)
    # TODO 
    codelist = code_dict[idx]
    mongoM = MongoIo()
    daraResult = pd.DataFrame()
    for code in codelist:
        # print("begin-doForcastMP code:", code)
        dataM=mongoM.get_stock_day(code, st_start = '1990-01-01')
        # print(type(dataM))
        if len(dataM) == 0:
            continue
        if len(predict) == 0:
            predict = calcPredict(dataM, t = 240)
            if len(predict) > 2:
                predict = predict[:-1]
        if predict == None or len(predict) < 1:
            print("predict data is NULL")
            # return None
            continue
        
        if baseDate == None:
            baseDate = dataM.index[-1][0] # - datetime.timedelta(baseDay)
        else:
            baseDate = pd.to_datetime(baseDate)

        dataLastDate = dataM.index[-1][0]
        
        lastDate = (baseDate, dataLastDate)
        calcData = (beforeStep, afterStep, delta)

        try:
            (firstDay, xlabel, dictData, predictValue) = doForcast4LoopYear(99, code, dataM, lastDate, calcData, startDates = predict, plot = None)
            # plt.title("%s == %s" % (code, predictValue))
            if dictData['code'] == []:
                continue
            else:
                df = pd.DataFrame.from_dict(dictData)
                df = df.set_index(["code", "loop"])
                # print("len df", len(df))
                if len(daraResult) == 0:
                    daraResult = df
                else:
                    daraResult = daraResult.append(df)
            print("calc result:", code, predictValue[:20], len(daraResult))
        except Exception as e:
            print("calc doForcast4LoopYear except", e)
    daraResult.to_csv("calc-out-%d.csv" % idx)
    end_t = datetime.datetime.now()
    print(end_t, 'doForcastMP spent:{}'.format((end_t - start_t)))

    return daraResult

def do_get_data_mp(key, codelist, st_start = '1990-01-01', st_end = '2031-12-31'):
    # print("do-get-data-mp ... ")
    mongo_mp = MongoIo()
    start_t = datetime.datetime.now()
    print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
    # databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end)
    end_t = datetime.datetime.now()
    print(end_t, 'get_data do_get_data_mp spent:{}, size = '.format((end_t - start_t)))

executor_func = ProcessPoolExecutor(max_workers=cpu_count() * 2)
code_dict = Manager().dict()
pool_size = cpu_count()
databuf_mongo = Manager().dict()

if __name__ == "__main__":
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)
    # print("code idx:0,1 predate col1 col2 co")
    # print(sys.argv[1:])
    argv = sys.argv[1:]
    code=argv[0]
    idx=argv[1]
    beforeStep = int(argv[2])
    afterStep = int(argv[3])
    delta = int(argv[4]) / 100.0
    loopYear = int(argv[5])
    # baseDay = int(argv[5])
    baseDay = None
    if len(argv) > 6:
        baseDay = argv[6]
    predict = []
    if len(argv) > 7:
        predict=argv[7:]
    # print(delta, baseDay, predict)
    print("params code=%s, idx=%s, beforeStep=%d, afterStep = %d, delta=%5.2f" % (code, idx, beforeStep, afterStep, delta))
    # print("params lastDay=%s, dataLastDate=%s, predict=%s" % (str(lastDay)[:10], str(dataLastDate)[:10], predict[-1]))
    # =MongoIo()
    databuf_mongo = Manager().dict()
    
    # pool_size = cpu_count()
    codelist=QA.QA_fetch_stock_block_adv().code[:100]
    subcode_len = math.ceil(len(codelist) / pool_size)
    # executor = ProcessPoolExecutor(max_workers=pool_size * 2)
    # code_dict = {}
    pool = Pool(cpu_count())
    for i in range(subcode_len + 1):
        for j in range(pool_size):
            x = (i * pool_size + 1) + j
            if x < len(codelist):
                if j in code_dict.keys():
                    # code_dict[j].append(codelist[x])
                    code_dict[j] = code_dict[j] + [codelist[x]]
                else:
                    code_dict[j] = [codelist[x]]

    for i in range(pool_size):
        # if i < pool_size - 1:
        #     code_dict[str(i)] = codelist[i* subcode_len : (i+1) * subcode_len]
        # else:
        #     code_dict[str(i)] = codelist[i * subcode_len:]
        # print(code_dict[str(i)][:10])
        print(code_dict[i])
        pool.apply_async(do_get_data_mp, args=(i, code_dict[i]))
    
    pool.close()
    pool.join()
    end_t = datetime.datetime.now()
    print(end_t, 'read db spent:{}'.format((end_t - start_t)))
    
    
    task_list = []
    # pool = Pool(cpu_count())
    # mongoM, code, baseDate, delta, predict
    for key in range(pool_size):
        # tdx_func(databuf_mongo[key])
        # print(key)
        # mongoM = MongoIo()
        task_list.append(executor_func.submit(doForcastMP, key, baseDay, delta, predict))

    dataR = pd.DataFrame()
    for task in as_completed(task_list):
        if len(dataR) == 0:
            dataR = task.result()
        else:
            dataR = dataR.append(task.result())
        print("dataR", len(dataR))
    if len(dataR) > 0:
        print(dataR.head(10))

    dataR.to_csv("calc-out.csv")
    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))
