# from easyquant import StrategyTemplate
# from easyquant import RedisIo

###
### python tdx_hcalc_new2.py -f bjmm -b 2020-01-01 -e 2021-12-31 -t T -a tdx/data/USL5556020210609.txt -r 2021-06-09
###

### python tdx_hcalc_new2.py -f dqe_cfc_A11 -b 2020-01-01 -e 2021-12-31 -t B -a tdx/data/Usl5556020210615.txt -r 2021-06-11

from easyquant import DataUtil
from threading import Thread, current_thread, Lock
import QUANTAXIS as QA
import json
import datetime
import sys, getopt
from easyquant import DataUtil
import subprocess
import pexpect

# import redis
import time
# import datetime
# from datetime import datetime, date
import pandas as pd

# import pymongo
import pika
# from QUANTAXIS.QAFetch import QATdx as tdx
# from easyquant import DefaultLogHandler
# from custom import tdx_func
from tdx.func.tdx_func import *
from tdx.func.func_sys import *
# from easyquant import EasyMq
from easyquant import MongoIo
from easyquant import EasyTime
from multiprocessing import Process, Pool, cpu_count, Manager
# from easyquant.indicator.base import *
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
#from pyalgotrade.strategy import position
# from custom.sinadataengine import SinaEngine
import easyquotation

# calc_thread_dict = Manager().dict()
data_codes = Manager().dict()
data_buf_day = Manager().dict()
data_buf_stockinfo = Manager().dict()
databuf_mongo = Manager().dict()
databuf_mongo_cond = Manager().dict()
# databuf_mongo_r = Manager().dict()
# databuf_mongo_rn = Manager().dict()
databuf_mongo_1 = Manager().dict()
databuf_mongo_5 = Manager().dict()
databuf_mongo_15 = Manager().dict()
databuf_mongo_30 = Manager().dict()
databuf_mongo_60 = Manager().dict()
# data_buf_5min = Manager().dict()
# data_buf_5min_0 = Manager().dict()

easytime=EasyTime()
pool_size = cpu_count()
executor = ThreadPoolExecutor(max_workers=pool_size)
executor2 = ThreadPoolExecutor(max_workers=pool_size * 4)
executor_func = ProcessPoolExecutor(max_workers=cpu_count() * 2)
codeDatas = []
# class DataSinaEngine(SinaEngine):
#     EventType = 'data-sina'
#     PushInterval = 10
#     config = "stock_list"
def get_next_date(calcDate):
    cDate = datetime.datetime.strptime(calcDate, '%Y-%m-%d')
    cDate = cDate + datetime.timedelta(1)
    if cDate.weekday() < 5:
        return datetime.datetime.strftime(cDate,'%Y-%m-%d')
    else: # if calcDate.weekday() == 5:
        cDate = cDate + datetime.timedelta(2)
        return datetime.datetime.strftime(cDate,'%Y-%m-%d')
#     else: # calcDate.weekday() == 6:
#         cDate = cDate + datetime.timedelta(2)
#         return datetime.datetime.strftime(cDate,'%Y-%m-%d')

def get_stock_codes(config="stock_list"):
    if 1 in data_codes:
        return data_codes[1]

    config_name = './config/%s.json' % config
    with open(config_name, 'r') as f:
        data_codes[1] = json.load(f)
        return data_codes[1]

def fetch_quotation_data(codelist, source="sina"):
    # tencent,qq, sina
    # source = easyquotation.use(source)
    source = easyquotation.use("sina")
    # codelist = getCodeList(all_data)
    # data = get_stock_codes(config)
    try:
        out = source.stocks(codelist)
        # print (out)
        while len(out) == 0:
            out = source.stocks(codelist)
        # print (out)
    except:
        out = None
    return out
        
# dataSrc = DataSinaEngine()

def do_init_data_buf(code):
    # freq = 5
    # 进程必须在里面, 线程可以在外部
    # mc = MongoIo()
    # mongo = MongoIo()
    # if idx == 0:
    mongo = MongoIo()
    data_day = mongo.get_stock_day(code=code, st_start="2019-01-01")
        # data_min = mc.get_stock_min_realtime(code=code, freq=freq)
    # else:
    #     data_day = mongo.get_index_day(code=code)
        # data_min = mc.get_index_min_realtime(code=code)
    data_buf_day[code] = data_day
    data_buf_stockinfo[code] = mongo.get_stock_info(code)
    # data_buf_5min[code] = data_min
    # print("do-init data end, code=%s, data-buf size=%d " % (code, len(data_day)))
    
def do_get_data_mp(key, codelist, st_start, st_end, func_nameA, calcType=''):
    mongo_mp = MongoIo()
#     slip  = 1
    # start_t = datetime.datetime.now()
    # print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
    if len(func_nameA) < 1:
        return
        # 取得当前数据
    func_buy = func_nameA[0]
    func_sell = func_nameA[1]
    databuf_mongo = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end='2035-12-31')
    
    if len(databuf_mongo) > 0:
        for code in codelist:
            result1 = pd.DataFrame()
            result = pd.DataFrame()
            try:
                tempData = databuf_mongo.query("code=='%s'" % code)
                if len(tempData) == 0:
                    continue
                result1['buy'] = eval(func_buy)(tempData)
                result1['sell'] = eval(func_sell)(tempData)
#                 tempData['buy'] = buy
#                 tempData['sell'] = sell
                result1 = result1[(result1.sell ==1) | (result1.buy == 1)]
                ## TODO
                buy_sell_cond = {}
                bought = False
                sold = True
                for idx in result1.index:
                    if result1.loc[idx].buy == 1:
                        if len(buy_sell_cond) == 0:
                            bought = True
                            sold = False
                            buy_sell_cond['code'] = code
                            buy_sell_cond['buy-date'] = idx[0]
                            buy_sell_cond['buy-price'] = tempData.loc[idx].close
                        else:
                            continue
                    if result1.loc[idx].sell == 1:
                        if len(buy_sell_cond) == 0:
                            continue
                        else:
                            bought = False
                            sold = True
                            buy_sell_cond['sell-price'] = tempData.loc[idx].close
                            buy_sell_cond['sell-date'] = idx[0]
                            buy_sell_cond['pct'] = (buy_sell_cond['sell-price'] - buy_sell_cond['buy-price']) / buy_sell_cond['buy-price'] * 100 - 0.5
                            
                            result = result.append(buy_sell_cond, ignore_index=True)
                            buy_sell_cond = {}
#                         pass
                if bought and not sold:
                    buy_sell_cond['sell-price'] = tempData.iloc[-1].close
                    buy_sell_cond['sell-date'] = tempData.index[-1][0]
                    buy_sell_cond['pct'] = (buy_sell_cond['sell-price'] - buy_sell_cond['buy-price']) / buy_sell_cond['buy-price'] * 100 - 0.5

                    result = result.append(buy_sell_cond, ignore_index=True)
                    print("code = %s, last = %s" % (code, buy_sell_cond))
#                 result = result.append(result1)
            # 斜率
            except Exception as e:
#                 tempData['cond'] = 0
                print("code-result", code, len(result), e)
#             if len(result) > 0:
#                 result.to_csv('/root/result1-%s.csv' % code)
#                 break
            if len(result) > 0:
                print("the %d calc code %s ... ended." % (key, code))
                mongo_mp.upd_backtest_bs("%s-%s" % (func_buy, func_sell), result)

def pba_calc(code):
    try:
        stockinfo = data_buf_stockinfo[code]
        return stockinfo.jinglirun[0] > 0
    except:
        return False

def do_get_data_mp_min(key, codelist, st_start, freq):
    mongo_mp = MongoIo()
    # start_t = datetime.datetime.now()
    # print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))

    get_data_list = mongo_mp.get_stock_min(codelist, st_start=st_start, freq=freq)
    if freq == 1:
        databuf_mongo_1[key] = get_data_list
    elif freq == 5:
        databuf_mongo_1[key] = get_data_list
    elif freq == 15:
        databuf_mongo_1[key] = get_data_list
    elif freq == 30:
        databuf_mongo_1[key] = get_data_list
    elif freq == 60:
        databuf_mongo_1[key] = get_data_list

        # end_t = datetime.datetime.now()
    # print(end_t, 'get_data do_get_data_mp spent:{}'.format((end_t - start_t)))

def get_data(codelist, st_start, st_end, calcType, func_names):
    start_t = datetime.datetime.now()
    print("begin-get_data:", start_t)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    # codelist = ['600380','600822']
    func_nameA = func_names.split(',')
    pool_size = cpu_count()
    limit_len = 0
    code_dict = codelist2dict(codelist, pool_size)
    # print("get-data", code_dict)
    pool = Pool(cpu_count())
    for i in code_dict.keys():
        # if i < pool_size - 1:
            # code_dict[str(i)] = codelist[i* subcode_len : (i+1) * subcode_len]
        # else:
            # code_dict[str(i)] = codelist[i * subcode_len:]
        pool.apply_async(do_get_data_mp, args=(i, code_dict[i], st_start, st_end, func_nameA, calcType))

    pool.close()
    pool.join()


    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))
    # return data_day

def main_param(argv):
    st_begin = ''
    st_end = ''
    func = ''
    calcType = ''
    back_time = ''
    all_data = ''
    sort = ''
    try:
        opts, args = getopt.getopt(argv[1:], "hb:e:f:t:r:a:s:", ["st-begin=", "st-end=", "func=", "calcType=", "realdata-date=", 'all-data=', 'sort-type='])
    except getopt.GetoptError:
        print(argv[0], ' -b <st-begin> [-e <st-end>] [-f <func-name:dhm> -t T -c <back-test-date>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(argv[0], ' -b2 <st-begin> [-e <st-end>] [-f <func-name:dhm> -t T -c B]')
            sys.exit()
        elif opt in ("-b", "--st-begin"):
            st_begin = arg
        elif opt in ("-e", "--st-end"):
            st_end = arg
        elif opt in ("-f", "--func"):
            func = arg
        elif opt in ("-s", "--sort"):
            sort = arg
        elif opt in ("-t", "--type"):
            calcType = arg
        elif opt in ("-r", "--realdata-date"):
            back_time = arg
        elif opt in ("-a", "--all-date"):
            all_data = arg
    return st_begin, st_end, func, sort, calcType, back_time, all_data

if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)

    # st_start, st_end, func = main_param(sys.argv)
    # print("input", st_start, st_end, func)
    st_start, st_end, func, sort, calcType, back_time, all_data = main_param(sys.argv)
            

    if all_data == '':
        all_data = 'position'
    codelist = getCodeList(all_data)
    # func = "test"
    print("input st-start=%s, st-end=%s, func=%s, all_data = %s" % (st_start, st_end, func, all_data))
    # 1, 读取数据（多进程，读入缓冲）
    # 开始日期
    # data_day = get_data(st_start)
    # print(data_day)
    # indices_rsrsT = tdx_func(data_day)

    get_data(codelist, st_start, st_end, calcType, func)
    end_t = datetime.datetime.now()
    print(end_t, '__name__ spent:{}'.format((end_t - start_t)))
#     print("__name__", len(dataR))
