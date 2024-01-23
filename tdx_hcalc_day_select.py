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
from multiprocessing import Process, Pool, cpu_count, Manager
# from easyquant.indicator.base import *
# from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
#from pyalgotrade.strategy import position
# from custom.sinadataengine import SinaEngine
import easyquotation

# calc_thread_dict = Manager().dict()
data_codes = Manager().dict()
data_buf_day = Manager().dict()
data_buf_stockinfo = Manager().dict()
databuf_mongo = Manager().dict()
# databuf_mongo_r = Manager().dict()
# databuf_mongo_rn = Manager().dict()
# data_buf_5min = Manager().dict()
# data_buf_5min_0 = Manager().dict()

pool_size = cpu_count()
# executor = ThreadPoolExecutor(max_workers=pool_size)
codeDatas = []
# class DataSinaEngine(SinaEngine):
#     EventType = 'data-sina'
#     PushInterval = 10
#     config = "stock_list"

# dataSrc = DataSinaEngine()

def do_get_data_mp(key, codelist, st_start, st_end):
#     print("do_get_data_mp", key)
    mongo_mp = MongoIo()
#     slip  = 1
    # start_t = datetime.datetime.now()
    # print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
#     if len(func_nameA) < 1:
#         return
        # 取得当前数据
#     func_buy = func_nameA[0]
#     func_sell = func_nameA[1]
#     databuf_mongo = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end)
#     print("code-list", codelist[:100])
    databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end, qfq=1)

def get_data(codelist, st_start, st_end):
    start_t = datetime.datetime.now()
    print("begin-get_data:", start_t)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    # codelist = ['600380','600822']
#     func_nameA = func_names.split(',')
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
        pool.apply_async(do_get_data_mp, args=(i, code_dict[i], st_start, st_end))

    pool.close()
    pool.join()


    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))
    # return data_day

def day_select(codelist, back_time, func_names):
    start_t = datetime.datetime.now()
    print("begin-day_select:", back_time)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    # codelist = ['600380','600822']

    calcDate = back_time
    backDates = [calcDate]
    endDate = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
    calcDate = get_next_date(calcDate)
    while calcDate <= endDate:
        backDates.append(calcDate)
        calcDate = get_next_date(calcDate)
#     print('calc-date = %s' % backDates)

    func_nameA = func_names #func_names.split(',')
    pool_size = cpu_count()
    limit_len = 0
    code_dict = codelist2dict(codelist, pool_size)
    # print("get-data", code_dict)
    pool = Pool(cpu_count())
#     for i in [0,1,2,3,5,6,7]:
    for i in code_dict.keys():
        # if i < pool_size - 1:
            # code_dict[str(i)] = codelist[i* subcode_len : (i+1) * subcode_len]
        # else:
            # code_dict[str(i)] = codelist[i * subcode_len:]
        pool.apply_async(do_day_select, args=(i, code_dict[i], backDates, func_nameA))
#         for calcDate in backDates:
#             print(i, calcDate, func_nameA)
    pool.close()
    pool.join()


    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'day_select spent:{}'.format((end_t - start_t)))
    # return data_day

def do_day_select(key, codelist, backDates, func_nameA):
    today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
    mongo_mp = MongoIo()
    for code in codelist:
        all_calc_data = {}
        tempData = databuf_mongo[key].query("code=='%s'" % code)
        if len(tempData) <= 0:
            continue
        if not func_check_data(tempData):
            continue
        print("begin-calc-data: code = ", code, key)
        for func_calc in func_nameA:
            try:
                result1 = eval(func_calc)(tempData)[0]
                result1 = result1[result1==1]
                for x in result1.index:
                    out_t = datetime.datetime.strftime(x[0],'%Y-%m-%d')
                    outKey = '%s-%s' % (code, out_t)
                    if out_t in backDates:
                        if outKey in all_calc_data:
                            all_calc_data[outKey]['func'].append(func_calc)
                            all_calc_data[outKey]['score'] += 1
    #                         print("key1", outKey, all_calc_data[outKey])
                        else:
                            all_calc_data[outKey] = {'_id':outKey, 'code': code, 'date': out_t, 'price': tempData.loc[x].close, 'func': [func_calc], 'score': 1}
            except:
                print("calc-error, key=%s, code=%s, func=%s" % ( key, code, func_calc) )
                continue
#                         print("key2", key, all_calc_data[key])

#                     print("out", code, func_calc, out_t, tempData.loc[x].close)
#             if len(result1) > 0:
#                 print(func_calc, result1.head(1))
            
#     slip  = 1
        ins_datas = []
        if len(all_calc_data) > 0:
            for x in all_calc_data:
                if all_calc_data[x]['score'] > 1:
                    ins_datas.append(all_calc_data[x])
#             print(all_calc_data)
            if len(ins_datas) > 0:
                try:
                    mongo_mp.save('day-select-%s' % today, ins_datas)
                except:
                    print("ins mongo error, code:", code)
    print("do_day_select-end", key)
    # start_t = datetime.datetime.now()
    # print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
#     if len(func_nameA) < 1:
#         return
        # 取得当前数据
#     func_buy = func_nameA[0]
#     func_sell = func_nameA[1]
#     databuf_mongo = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end)
#     databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end)

    
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
    print('example: python tdx_hcalc_day_select.py -b 2020-01-01 -e 2024-01-20 -r 2024-01-02')
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)
    
    # st_start, st_end, func = main_param(sys.argv)
    # print("input", st_start, st_end, func)
    st_start, st_end, func, sort, calcType, back_time, all_data = main_param(sys.argv)
            
#     st_start = '1990-01-01'
    all_data = 'all'
    codelist = getCodeList(all_data)
    # func = "test"
    print("input st-start= %s, st-end= %s, back_time = %s" % (st_start, st_end, back_time))
    # 1, 读取数据（多进程，读入缓冲）
    # 开始日期
    data_day = get_data(codelist, st_start, st_end)
    # print(data_day)
    # indices_rsrsT = tdx_func(data_day)
    func1 = ['tdx_czhs', 'tdx_hm', 'tdx_dhmcl', 'tdx_sxp', 'tdx_hmdr', 'tdx_tpcqpz', 'tdx_jmmm', 'tdx_nmddl', 'tdx_swl', 'tdx_yaogu']
    func2 = ['tdx_niugu', 'tdx_buerfameng', 'tdx_yaoguqidong', 'tdx_ygqd_test', 'tdx_blftxg', 'tdx_cptlzt', 'tdx_yhzc', 'tdx_yhzc_macd', 'tdx_yhzc_kdj']
    func3 = ['tdx_bjmm', 'tdx_bjmm_jzmd', 'tdx_bjmm_yhzc', 'tdx_bjmm_new', 'tdx_sxjm', 'tdx_ltt', 'tdx_blft', 'tdx_cci_xg', 'tdx_WYZBUY', 'tdx_bdzh']
    func4 = ['tdx_skdj_lstd', 'tdx_lyqd', 'tdx_sl5560', 'tdx_lbqs', 'tdx_zttj', 'tdx_zttj1', 'tdx_cmfx', 'tdx_TLBXX', 'tdx_LDX', 'tdx_TLBXXF']
    func5 = ['tdx_WYZ17MA', 'tdx_qszn', 'tdx_cci', 'tdx_ngqd', 'tdx_bollxg_start', 'tdx_DQS', 'tdx_JZZCJSD', 'tdx_CDYTDXG', 'tdx_BOLL_EMA', 'tdx_hjy']
    func6 = ['tdx_LLXGSQ', 'tdx_WWDGWY', 'tdx_WWXGSQ', 'tdx_WWYHXG', 'tdx_WWMACDJC', 'tdx_SHYM', 'tdx_QIANFU', 'tdx_HW168QS']
#     func7 = ['tdx_sxzsl']

#     func = 'tdx_czhs, tdx_hm, tdx_dhmcl, tdx_sxp, tdx_hmdr, tdx_tpcqpz, tdx_jmmm, tdx_nmddl, tdx_swl, tdx_yaogu \
#     , tdx_niugu, tdx_buerfameng, tdx_yaoguqidong, tdx_ygqd_test, tdx_blftxg, tdx_cptlzt, tdx_yhzc, tdx_yhzc_macd, tdx_yhzc_kdj, tdx_sxp_yhzc \
#     , tdx_bjmm, tdx_bjmm_jzmd, tdx_bjmm_yhzc, tdx_bjmm_new, tdx_sxjm, tdx_ltt, tdx_blft, tdx_cci_xg, tdx_WYZBUY, tdx_bdzh \
#     , tdx_skdj_lstd, tdx_lyqd, tdx_sl5560, tdx_lbqs, tdx_zttj, tdx_zttj1, tdx_cmfx, tdx_TLBXX, tdx_LDX, tdx_TLBXXF \
#     , tdx_WYZ17MA, tdx_qszn, tdx_cci, tdx_ngqd, tdx_bollxg_start, tdx_DQS, tdx_JZZCJSD, tdx_CDYTDXG, tdx_BOLL_EMA, tdx_hjy \
#     , tdx_LLXGSQ, tdx_WWDGWY, tdx_WWXGSQ, tdx_WWYHXG, tdx_WWMACDJC, tdx_SHYM, tdx_QIANFU, tdx_HW168QS \
#     '
    func = func1 + func2 + func3 + func4 + func5 + func6 # + func7
#     get_data(codelist, st_start, st_end)
    day_select(codelist, back_time, func)
    end_t = datetime.datetime.now()
    print(end_t, '__name__ spent:{}'.format((end_t - start_t)))
#     print("__name__", len(dataR))
