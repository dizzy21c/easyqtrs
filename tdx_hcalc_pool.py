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

def tdx_func_mp_all(func_names, sort_types, codelist, calcType='', backTime=''):
#     构造backTimeList
    calcDate = backTime
    backDates = [calcDate]
    endDate = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
    calcDate = get_next_date(calcDate)
    while calcDate <= endDate:
        backDates.append(calcDate)
        calcDate = get_next_date(calcDate)
#         print(backDates)
#         return
    for backDate in backDates:
        tdx_func_mp(func_names, sort_types, codelist, calcType, backDate)

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
    
def do_get_data_mp(key, codelist, st_start, st_end, func_name, calcType=''):
    mongo_mp = MongoIo()
    # start_t = datetime.datetime.now()
    # print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
    if calcType == 'B':
        refFlg = True
    else:
        refFlg = False
    databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end='2035-12-31')
    result = pd.DataFrame()
    if len(databuf_mongo[key]) > 0:
        for code in codelist:
            try:
#                 print("code", code)
                tempData = databuf_mongo[key].query("code=='%s'" % code)
                if len(tempData) == 0:
                    continue
                tdx_func_result, tdx_func_sell_result, next_buy = eval(func_name)(tempData, refFlg)
#                 tempData['cond'] = tdx_func_result
                if len(result) == 0:
                    result = pd.DataFrame(tdx_func_result)
#                     result.columns = ['cond']
                else:
                    if len(tdx_func_result) > 0:
                        result1 = pd.DataFrame(tdx_func_result)
#                         result.columns = ['cond']
                        result = result.append(result1)
            # 斜率
            except Exception as e:
#                 tempData['cond'] = 0
                print("code-result", code, len(result), e)
#     databuf_mongo_cond[key] = result.fillna(0)
    result = result.fillna(0)
    result.columns = ['cond']
    databuf_mongo_cond[key] = result

    # end_t = datetime.datetime.now()
    # print(end_t, 'get_data do_get_data_mp spent:{}'.format((end_t - start_t)))
    for code in codelist:
        data_buf_stockinfo[code] = mongo_mp.get_stock_info(code)

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
        pool.apply_async(do_get_data_mp, args=(i, code_dict[i], st_start, st_end, func_nameA[0], calcType))

    pool.close()
    pool.join()

    # # todo begin
    # data_day = pd.DataFrame()
    # for i in range(pool_size):
    #     if len(data_day) == 0:
    #         data_day = databuf_mongo[i]
    #     else:
    #         data_day = data_day.append(databuf_mongo[i])
    #     # print(len(dataR))
    # data_day.sort_index()
    # # todo end
    # 获取股票中文名称，只是为了看得方便，交易策略并不需要股票中文名称
    # stock_names = QA.QA_fetch_stock_name(codelist)
    # codename = [stock_names.at[code] for code in codelist]

    # data_day = QA.QA_fetch_stock_day_adv(codelist,
    #                                     '2010-01-01',
    #                                     '{}'.format(datetime.date.today(),)).to_qfq()

    # st_start="2018-12-01"
    # data_day = mongo.get_stock_day(codelist, st_start=st_start)

    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))

    # return data_day

def tdx_func_mp(func_names, sort_types, codelist, calcType='', backTime=''):
    start_t = datetime.datetime.now()
    # if start_t.time() < datetime.time(9, 30, 00):
    #     print("read web data from tencent begin-time:", start_t)
    #     newdatas = fetch_quotation_data(source="tencent")
    # else:
    print("read web data-begin-time:", start_t)
    mongo = MongoIo()
    if calcType == 'B':
        newdatas = mongo.get_realtime(codelist, backTime)
    else:
        newdatas = fetch_quotation_data(codelist, source="sina")

    end_t = datetime.datetime.now()
    print(end_t, 'read web data-spent:{}'.format((end_t - start_t)))

    start_t = datetime.datetime.now()
    print("do-task1-begin-time:", start_t)
    # for stcode in datas:
    #     data = datas[stcode]

    start_t = datetime.datetime.now()
    print("begin-tdx_func_mp :", start_t)

    func_nameA = func_names.split(',')
    sort_typeA = sort_types.split(',')
    keysObj = {}
    ##
    if calcType == 'B':
        condd=datetime.datetime.strptime(backTime, '%Y-%m-%d')
    else:
        condd = datetime.datetime.strptime(back_time, '%Y-%m-%d') + datetime.timedelta(-1)
#         condd=datetime.datetime.strptime(backTime, '%Y-%m-%d')
    for key in range(pool_size):
#         keysObj[key] = None
        df1 = databuf_mongo_cond[key].sort_index()
        try:
            df1 = df1.loc[condd,]
            keysObj[key] = list(df1[df1['cond'] == 1].index)
#         print("keyObj", backTime, key, keysObj[key])
        except Exception as e:
            keysObj[key] = []

    is_idx = 1
    for func_name in func_nameA[1:]:
        sort_type = int(sort_typeA[is_idx])
        is_idx = is_idx + 1
        task_list = []
        # pool = Pool(cpu_count())
        for key in keysObj:
            # tdx_func(databuf_mongo[key])
            # task_list.append(executor_func.submit(tdx_func, databuf_mongo[key], newdatas, func_name, calcType=calcType))
            task_list.append(executor_func.submit(tdx_func, key, backTime, newdatas, func_name, code_list = keysObj[key], calcType=calcType))
        # pool.close()
        # pool.join()

        # todo begin
        dataR = pd.DataFrame()
        # for i in range(pool_size):
        #     if len(dataR) == 0:
        #         dataR = databuf_tdxfunc[i]
        #     else:
        #         dataR = dataR.append(databuf_tdxfunc[i])
        #     # print(len(dataR))
        keysObj = {}
        for task in as_completed(task_list):
            dR, key, codeList = task.result()
            keysObj[key] = codeList
            # pass
            if len(dataR) == 0:
                dataR = dR
            else:
                dataR = dataR.append(dR)

        if len(dataR) > 0:
            dataR = dataR.fillna(0)
            dataR = dataR.sort_values(by="dao")
            if sort_type > 0:
                dataR = dataR.tail(sort_type)
                allc = dataR.code.to_list()
                for key in keysObj:
                    sc = []
                    for sk in keysObj[key]:
                        if sk in allc:
                            sc.append(sk)
                    keysObj[key] = sc
            elif sort_type < 0:
                dataR = dataR.tail(abs(sort_type))
                allc = dataR.code.to_list()
                for key in keysObj:
                    sc = []
                    for sk in keysObj[key]:
                        if sk in allc:
                            sc.append(sk)
                    keysObj[key] = sc
    # todo end
    print(dataR)
    #dataR.to_csv("step-%s-%s.csv" % (func_name, backTime))
    if calcType == 'B':
        mongo.upd_backtest("%s-back" % func_names, dataR, backTime, calcType)
        dataR.to_csv("step-%s-%s-pool.csv" % (func_names, backTime))
    else:
        mongo.upd_backtest("%s-real" % func_names, dataR, backTime, calcType)
    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func_mp spent:{}'.format((end_t - start_t)))

    return dataR

def tdx_func_upd_hist_order(func_name):
    start_t = datetime.datetime.now()
    print("read web data-begin-time:", start_t)
    newdatas = fetch_quotation_data(source="sina")

    end_t = datetime.datetime.now()
    print(end_t, 'read web data-spent:{}'.format((end_t - start_t)))

    start_t = datetime.datetime.now()
    print("do-task1-begin-time:", start_t)
    # for stcode in datas:
    #     data = datas[stcode]

    start_t = datetime.datetime.now()
    print("begin-tdx_func_mp :", start_t)

    task_list = []
    # pool = Pool(cpu_count())
    mongo_np = MongoIo()
    for code in newdatas:
        try:
            data = newdatas[code]
            nowPrice = data['now']
            openPrice = data['open']
            dateStr = data['datetime']
            dateObj = datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
            mongo_np.upd_order_hist(func_name, code, nowPrice, openPrice, dateObj)
        except:
            print("read code error:", code)

    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func_mp spent:{}'.format((end_t - start_t)))

    # return dataR


# def tdx_func(datam, newdatas, func_name, code_list = None, calcType=''):
def tdx_func(key, calcDate, newdatas, func_name, code_list = None, calcType=''):
    """
    准备数据
    """
    # highs = data.high
    datam = databuf_mongo[key].query(" date < '%s' " % (calcDate))
#     if calcType == 'B':
#         datam_r = databuf_mongo_r[key]
#         datam_rn = databuf_mongo_rn[key]
    mongo_np = MongoIo()
    start_t = datetime.datetime.now()
    print("begin-tdx_func:", start_t)
    # dataER = pd.DataFrame()
    if code_list is None:
        code_list = datam.index.levels[1]
    # func_nameA = func_names.split(',')
    # sort_typeA = sort_types.split(',')
    is_idx = 0
    # for func_name in func_nameA:
    dataR = pd.DataFrame()
    # sort_type = int(sort_typeA[is_idx])
    is_idx = is_idx + 1
    for code in code_list:
        data=datam.query("code=='%s'" % code)
        # pb_value = pba_calc(code)
        # if not pb_value:
        #     print("pb < 0 code=%s" % code)
        #     continue
        try:
            if calcType == 'B':
                newdata0 = newdatas.query("code=='%s'" % code)
                if len(newdata0) > 0:
                    newdata = newdata0.iloc[-1]
                else:
                    # print("data-len=0, code=", code)
                    continue
            else:
                newdata = newdatas[code]
            now_price = newdata['now']
            last_price = newdata['now']
            dataln = None
            if calcType == 'B':
                try:
                    datal = databuf_mongo[key].query(" code=='%s' and date == '%s' " % (code, calcDate))
#                     datal = datam_r.query("code=='%s'" % code)
                    last_price = datal['close'][-1]
                except:
                    dataln = None
                    print("last-date=0, code=", code)
                    last_price = 0
                    continue
                try:
                    nextCalcDate = get_next_date(calcDate)
                    dataln = databuf_mongo[key].query(" code=='%s' and date == '%s' " % (code, nextCalcDate))
                except:
                    dataln = None
            # if (code == '003001'):
            #     print(data)
            #     print(newdata)
            data = new_df(data.copy(), newdata, now_price)
            calcR = tdx_base_func(data.copy(), func_name, code, newdata, last_price, dataln, mongo_np)
            if calcR == {}:
                continue
            dataR = dataR.append(calcR, ignore_index=True)
        except Exception as e:
            print("error code=%s" % code)
            print("error code=", e)
            # return
    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func spent:{}'.format((end_t - start_t)))
    print("tdx-fun-result-len", len(dataR))

    if len(dataR) > 0:
        code_list = dataR.code.to_list()
    else:
        code_list = {}
        # return pd.DataFrame()
    return dataR, key, code_list


# print("pool size=%d" % pool_size)
def tdx_base_func(data, func_name, code, newData, lastPrice, lastNData, mongo_np, code_list = None):
    """
    准备数据
    """
    dateObj = newData['datetime']
    timeStr = newData['time']
    insFlg = True
    nowPrice = newData['now']
    nowOpen = newData['open']
    oldClose = newData['close']
    if nowPrice == 0:
        return {}
    if nowOpen == 0:
        nowOpen = nowPrice
    PCT1 = nowPrice / oldClose - 1
    # PCT2 = newData['open'] / newData['close'] - 1
    PCT3 = nowPrice / nowOpen - 1
#     PCT4 = lastPrice / nowOpen - 1
    PCT4 = lastPrice / nowPrice - 1
    if lastNData is None or len(lastNData) == 0:
        PCTNO = 0
        PCTNC = 0
        PCTNL = 0
        PCTNH = 0
    else:
        PCTNO = lastNData.iloc[-1].open / nowPrice - 1
        PCTNC = lastNData.iloc[-1].close / nowPrice - 1
        PCTNL = lastNData.iloc[-1].low / nowPrice - 1
        PCTNH = lastNData.iloc[-1].high / nowPrice - 1

    # PCT = max(PCT1, PCT2)
    ##
    # if (code[0:3] == "300" or code[0:3] == 688) and (PCT > 1.08 ):# or PCT < 0.92):
    #     if timeStr <= "09:30:00":
    #         return
    #     else:
    #         insFlg = False
    # elif (code[0:3] != "300" and code[0:3] != 688) and (PCT > 1.05 ):# or PCT < 0.96):
    #     if timeStr <= "09:30:00":
    #         return
    #     else:
    #         insFlg = False

    #if timeStr > "09:36:00":
    #    insFlg = False

    try:
        tdx_func_result, tdx_func_sell_result, next_buy = eval(func_name)(data)
        # tdx_func_result, next_buy = tdx_a06_zsd(data)
    # 斜率
    except:
        print("calc %s code=%s ERROR:FUNC-CALC-ERROR " % (func_name, code))
        tdx_func_result, tdx_func_sell_result, next_buy = [0], [0], False
        
    # print("calc %s code=%s to PCT-20 dao=%5.3f " % (func_name, code, tdx_func_result[-1]))
    # if tdx_func_result[-1] > 0:
    #     try:
    #         if (code[0:3] == "300" or code[0:3] == 688) \
    #                 and data.iloc[-1].close >= data.iloc[-2].close * 1.19:
    #             profi = mongo_np.upd_order(func_name, dateObj, code, nowPrice, insFlg=False)
    #             print("calc %s code=%s to PCT-20 profi=%5.3f " % (func_name, code, profi))
    #         elif (code[0:3] != "300" and code[0:3] != 688) \
    #                 and data.iloc[-1].close >= data.iloc[-2].close * 1.09:
    #             profi = mongo_np.upd_order(func_name, dateObj, code, nowPrice, insFlg=False)
    #             print("calc %s code=%s to PCT-10 profi=%5.3f " % (func_name, code, profi))
    #         else:
    #             profi = mongo_np.upd_order(func_name, dateObj, code, nowPrice, insFlg=insFlg)
    #             print("calc %s code=%s now=%6.2f  profi=%5.3f " % (func_name, code, data.iloc[-1].close, profi))
    #     except:
    #         print("calc %s code=%s ERROR:BS-CALC-ERROR " % (func_name, code))
    dao = tdx_func_result[-1]
    if dao <= 0:
        return {}
    pn = "%4.1f" % (PCT1 * 100)
    po = "%4.1f" % (PCT3 * 100)
    pc = PCT4 * 100 # "%4.1f" % (PCT4 * 100)
    p2o = PCTNO * 100 # "%4.1f" % (PCTNO * 100)
    p2c = PCTNC * 100 # "%4.1f" % (PCTNC * 100)
    p2h = "%4.1f" % (PCTNH * 100)
    p2l = "%4.1f" % (PCTNL * 100)
    return {'code': code, 'now':nowPrice, 'dao': tdx_func_result[-1], 'pn':pn, 'po': po, 'PC': pc, 'P2O': p2o, 'P2C': p2c, 'p2h': p2h, 'p2l': p2l}

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
    if calcType == 'B':
        m = MongoIo()
        rc = m.get_realtime_count(dateStr = back_time)
        if rc == 0:
            exit(0)
            
    if calcType == 'T':
        back_time = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')

    if all_data == '':
        all_data = 'position'
    codelist = getCodeList(all_data)
    if calcType == 'B':
        m = MongoIo()
        his_real = m.get_realtime(dateStr = back_time)
        all_top = {}
        data_util = DataUtil()
        hidx = 0
#         dataA = pd.DataFrame()
        for code in codelist:
            temp = his_real.query("code=='%s'" % code)
            if len(temp) > 0:
                all_top = data_util.day_summary(data=temp.iloc[-1], rtn=all_top)
#             hidx = hidx + 1
        print(all_top)
#         exit(0)
    # st_start = "2019-01-01"
    # func = "test"
    print("input st-start=%s, st-end=%s, func=%s, sort=%s, calcType=%s, back-time=%s, all_data = %s" % (st_start, st_end, func, sort, calcType, back_time, all_data))
    # 1, 读取数据（多进程，读入缓冲）
    # 开始日期
    # data_day = get_data(st_start)
    # print(data_day)
    # indices_rsrsT = tdx_func(data_day)
    if calcType == 'B':
        td = datetime.datetime.strptime(back_time, '%Y-%m-%d') + datetime.timedelta(-1)
        st_end = td.strftime('%Y-%m-%d')
        # data_buf_rlast-dateday[0] =

    if calcType != 'R':
        get_data(codelist, st_start, st_end, calcType, func)

    # 2, 计算公式（多进程，读取缓冲）
    while True:
        if calcType == 'R':
            tdx_func_upd_hist_order(func, codelist)
            input()
            break

        if calcType == 'T':
            nowtime = datetime.datetime.now().time()
            if nowtime < datetime.time(9, 25, 50):
                time.sleep(10)
                print("log:sleep PM")
                continue
#             if nowtime > datetime.time(9,30,0):
#                 print("Pool stoped!!")
#                 break

#             if datetime.time(11, 30, 10) < nowtime < datetime.time(12, 59, 50):
#                 time.sleep(10)
                # print("log:sleep AM")
                # continue

            if nowtime > datetime.time(15,0,30):
                print("end trade time.")
                # time.sleep(3600)
                # break

            time.sleep(10)
            print("*** loop calc begin ***")
            tdx_func_mp(func, sort, codelist, calcType=calcType, backTime=back_time)

        if calcType == 'B':
            print("all-top", all_top)
            tdx_func_mp_all(func, sort, codelist, calcType=calcType, backTime=back_time)
            break
        # if calcType == 'T':
        #     input()

    end_t = datetime.datetime.now()
    print(end_t, '__name__ spent:{}'.format((end_t - start_t)))
#     print("__name__", len(dataR))
