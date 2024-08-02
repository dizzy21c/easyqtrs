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
databuf_mongo_cond = Manager().dict()
# databuf_mongo_r = Manager().dict()
# databuf_mongo_rn = Manager().dict()
# data_buf_5min = Manager().dict()
# data_buf_5min_0 = Manager().dict()

pool_size = cpu_count()
# executor = ThreadPoolExecutor(max_workers=pool_size)
codeDatas = []
codeNameDf = None
# class DataSinaEngine(SinaEngine):
#     EventType = 'data-sina'
#     PushInterval = 10
#     config = "stock_list"

# dataSrc = DataSinaEngine()
def codeName(df, code):
    try:
        return df.loc[code]['name']
    except:
        return code

def do_get_data_mp(key, codelist, st_start, st_end, pre_check_func):
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
    if idxCalcFlg:
        databuf_mongo[key] = mongo_mp.get_index_day(codelist, st_start=st_start, st_end = st_end)
    else:
        databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end, qfq=1)
#     print("do_get_data_mp", key, len(databuf_mongo[key]))
    result = pd.DataFrame()
    if len(databuf_mongo[key]) > 0:
        for code in codelist:
            try:
                tempData = databuf_mongo[key].query("code=='%s'" % code)
                if len(tempData) == 0:
                    continue
                tdx_func_result, tdx_func_sell_result, next_buy = eval(pre_check_func)(tempData)
#                 tdx_func_result, tdx_func_sell_result, next_buy = tdx_DQSZQ(tempData, True)
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
    
def get_data(codelist, st_start, st_end, pre_check_func):
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
        pool.apply_async(do_get_data_mp, args=(i, code_dict[i], st_start, st_end, pre_check_func))

    pool.close()
    pool.join()


    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))
    # return data_day

def day_select(codelist, back_time, func_names, calcType):
    start_t = datetime.datetime.now()
#     print("begin-day_select:", back_time)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    # codelist = ['600380','600822']

    if back_time == 'all':
        backDates = []
    else: ## back_time = '2020-12-31'; back_time = '2020-12-31,2022-12-31'
        calcDate = back_time[:10]
        endDate = back_time[11:]
        if len(endDate) == 0:
            endDate = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
        backDates = [calcDate]
        calcDate = get_next_date(calcDate)
        while calcDate <= endDate:
            backDates.append(calcDate)
            calcDate = get_next_date(calcDate)
    if calcType == 'N':
        backDates = backDates[-1:]
    print('calc-date = %s' % backDates)

    func_nameA = func_names #func_names.split(',')
    pool_size = cpu_count()
    limit_len = 0
    code_dict = codelist2dict(codelist, pool_size)
    # print("get-data", code_dict)
    pool = Pool(cpu_count())
#     for i in [0,1,2,3,5,6,7]:
    for i in code_dict.keys():
#         print("do %d" % i, code_dict[i], backDates, func_nameA, calcType)
        pool.apply_async(do_day_select, args=(i, code_dict[i], backDates, func_nameA, calcType))
    pool.close()
    pool.join()


    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'day_select spent:{}'.format((end_t - start_t)))
    # return data_day

def do_day_select(key, codelist, backDates, func_nameA, calcType):
    today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
    mongo_mp = MongoIo()
    for code in codelist:
        all_calc_data = {}
        tempData = databuf_mongo[key].query("code=='%s'" % code)
        if len(tempData) <= 0:
            print("data size is 0", code, key)
            continue
        if calcType == 'N':
            if databuf_mongo_cond[key].query("code=='%s'" % code).iloc[-1].cond == 0:
#                 print(code, "cond is 0")
                continue
            tempData = pytdx_last_data(tempData)
#         print(tempData.tail(3))
#         break
        if not func_check_data(tempData):
            print("check data size is 0", code, key)
            continue
        if calcType == 'N':
            pass
        else:
            print("begin-calc-data: code = ", code, key)
        for func_calc in func_nameA:
            result1 = pd.DataFrame()
            try:
                result1 = eval(func_calc)(tempData)[0]
                result1 = result1[result1==1]
            except Exception as e:
                print("calc-error, key=%s, code=%s, func=%s" % ( key, code, func_calc) ,e)
                continue
#             print("result1=", result1)
            for x in result1.index:
                out_t = datetime.datetime.strftime(x[0],'%Y-%m-%d')
#                 if code == '159001':
#                     print('step1', out_t, valid_calc_date, backDates)
                if out_t < valid_calc_date:
                    print("out-t:", out_t, len(backDates))
                    continue
                if len(backDates) > 0 and out_t not in backDates:
                    continue
#                 if code == '000028':
#                     print('step2', out_t, valid_calc_date)
                date_stamp = time.mktime(time.strptime(out_t, '%Y-%m-%d'))
                ins_func = func_calc
                outKey = '%s-%s-%s' % (code, out_t, func_calc)
#                 if code == '159001':
#                     print('step3', out_t, valid_calc_date, outKey)
#                 try:
                close = 0
                pct = 0
                tOpen = 0 ## today
                high = 0
                low = 0
                try:
                    close = tempData.loc[x].close
                    pct = 999 #tempData.loc[x].pctChg
                    tOpen = tempData.loc[x].open
                    high = tempData.loc[x].high
                    low = tempData.loc[x].low
                except Exception as e:
                    print("calc2-error, key=%s, code=%s, func=%s" % ( key, code, func_calc) ,e)
                    ## stop stock
                    continue
                nClose = 0 ## next close
                nOpen = 0
                noPct = -99999
                n2oPct = -99999 ## next next open Pct
                n2cPct = -99999 ## next next close Pct
                try:
                    tmpNext = tempData.loc[x:].head(3)
                    if len(tmpNext) > 1:
                        nClose = tmpNext.iloc[1].close
                        nOpen = tmpNext.iloc[1].open
                        if nOpen > 0:
                            noPct = (nClose - nOpen) / nOpen * 100
                    if len(tmpNext) > 2:
                        tempC = tmpNext.iloc[2].close
                        tempO = tmpNext.iloc[2].open
                        if nOpen > 0:
                            n2oPct = (tempO - nOpen) / nOpen * 100
                            n2cPct = (tempC - nOpen) / nOpen * 100
                except Exception as e:
                    print("calc3-error, key=%s, code=%s, func=%s" % ( key, code, func_calc) ,e)
                    pass
                    ## stop stock
#                     continue
#                 if outKey in all_calc_data:
#                     all_calc_data[outKey]['func'].append(func_calc)
#                     all_calc_data[outKey]['score'] += 1
#                 else:
                all_calc_data[outKey] = {'_id':outKey, 'code': code, 'name':"%s-%s"%(code,codeName(codeNameDf, code)), 'date': out_t, 'close': close, 'pct': pct, 'open': tOpen, 'high':high, 'low': low, 'nClose': nClose, 'nOpen': nOpen, 'noPct': noPct, 'n2oPct': n2oPct, 'n2cPct': n2cPct, 'func': ins_func, 'score':1, 'date_stamp':date_stamp}
#                 print("all-calc-data", all_calc_data)
#                 break
#                 if code == '000028':
#                     print('step3', out_t, valid_calc_date, all_calc_data[outKey])

        ins_datas = []
        tblName = 'day-select-%s' % all_data
        if calcType == 'N':##NOW:
            tblName = 'day-select-idx-%s' % tblFlg
        if len(all_calc_data) > 0:
            for x in all_calc_data:
#                 if all_calc_data[x]['score'] > 1: ###### for test one
                ins_datas.append(all_calc_data[x])
#             print("today", today, len(ins_datas))
            if len(ins_datas) > 0:
                try:
                    mongo_mp.save(tblName, ins_datas)
                except Exception as e:
#                     print("ins mongo batch data error, code:", code)
                    for sing_data in ins_datas:
                        try:
                            mongo_mp.save(tblName, sing_data)
                        except Exception as e2:
#                             if code == '000002':
#                                 print("ins mongo sing data error, code:", code, sing_data['_id'])
                            mongo_mp.remove(tblName, sing_data['_id'])
                            mongo_mp.save(tblName, sing_data)
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


def get_avg_data(data):
    l_idx = []
    l_v = []
    max1 = 10
    max2 = 30
    delta = 3
    i = 0
    tempLv = 99999
    tempLi = None

    tempHv = 0

    loopL1 = -1
    loopL2 = -1

    lowB = False
    for idx, row in data.iterrows():
        if lowB:
            loopL1 += 1
            if row.low < tempLv and loopL2 <= delta:
    #             print('calc1', loopL1, loopL2, tempLi, tempLv, idx, row.low)
                tempLv = row.low
                tempLi = idx
    #             loopL1 = 0
                loopL2 = 0
            else:
    #             loopL1 += 1 
                loopL2 += 1

            if loopL1 >= max1 and loopL1 <= max2 and loopL2 > delta:
                print("calc2", loopL1, loopL2, tempLi, tempLv)
                l_idx.append(tempLi) 
                l_v.append(tempLv) 
                loopL1 = -1
                loopL1 = -1
                lowB = False
                tempLv = 99999
                tempLi = None
        if row.low < tempLv:
            tempLv = row.low
            tempLi = idx
            lowB = True
            loopL1 = 0
            loopL2 = 0
    return pd.DataFrame(data = l_v, index = l_idx, columns = ['low'])

def main_param(argv):
    st_begin = ''
    st_end = ''
    func = ''
    pchk = ''
    calcType = ''
    back_time = ''
    all_data = ''
    sort = ''
    try:
        opts, args = getopt.getopt(argv[1:], "hb:e:f:t:r:a:s:p:", ["st-begin=", "st-end=", "func=", "calcType=", "realdata-date=", 'all-data=', 'sort-type=', 'pcheck='])
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
        elif opt in ("-p", "--pcheck"):
            pchk = arg
        elif opt in ("-t", "--type"):
            calcType = arg
        elif opt in ("-r", "--realdata-date"):
            back_time = arg
        elif opt in ("-a", "--all-date"):
            all_data = arg
    return st_begin, st_end, func, sort, calcType, back_time, all_data, pchk

if __name__ == '__main__':
    print('example: \ndefault\tpython tdx_hcalc_day_select.py')
    print('test\tpython tdx_hcalc_day_select.py -b 1990-01-01 -e 2010-12-31 -r all -t T/N -f tdx_swl')
    print('single\tpython tdx_hcalc_day_select.py -b 2019-01-01 -e 2024-12-31 -r 2020-12-12,2022-12-12')
    print('single\tpython tdx_hcalc_day_select.py -b 2019-01-01 -e 2024-12-31 -r all-B2020-12-13')
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)
    
    ## hist1
    ## tdx_hcalc_day_select.py -b 1990-01-01 -e 2012-12-31 -r all
    ## python tdx_hcalc_day_select.py -b 2010-01-01 -e 2020-12-31 -r all-B2012-12-20
    ## -f tdx_sl5560,tdx_ygqd_test
    # st_start, st_end, func = main_param(sys.argv)
    # print("input", st_start, st_end, func)
    st_start, st_end, funcInput, sort, calcType, back_time, all_data, pchk = main_param(sys.argv)
    today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
    if st_start == '':
        st_start = "%s-01-01" % (int(today[:4]) - 3)
    if st_end == '':
        st_end =get_next_date(today)
    else:
        st_end =get_next_date(st_end, 2)
    
    valid_calc_date = '1990-01-01'
    if back_time == '': ## all = all-date
        back_time = get_prev_date(today, 3) # "%s,%s" % (get_prev_date(today,2), today)
    elif back_time[:5] == 'all-B':
        valid_calc_date = back_time[5:]
        back_time = 'all'
#         back_time = get_prev_date(st_end,3) # "%s,%s" % (get_prev_date(today,2), today)
    print("calc paras: st-start= %s, st-end= %s, back_time = %s, func = %s, valid-date=%s" % (st_start, st_end, back_time, funcInput, valid_calc_date))
    
    if pchk == '':
        pchk = 'tdx_DQS'
#     print('date-stamp', time.mktime(time.strptime(back_time, '%Y-%m-%d')))
#     exit(0)
    
#     st_start = '1990-01-01'
    if all_data == '':
        all_data = 'stock'
#     all_data = 'etf-kj'
    idxCalcFlg = False
    if all_data == 'etf-jk' or all_data == 'index-tdx':
        idxCalcFlg = True

    codeNameDf = getCodeNameList(all_data)
    codelist = getCodeList(all_data)
#     codelist2 = getCodeList('index-idx')
#     codelist = codelist1 + codelist2
    if calcType == 'T':
        codelist = codelist[:32] ## for test
    # func = "test"
    # 1, 读取数据（多进程，读入缓冲）
    # 开始日期
    # data_day = 
#     print(len(codelist))
#     exit(0)
    get_data(codelist, st_start, st_end, pchk)
    # print(data_day)
    # indices_rsrsT = tdx_func(data_day)
    func1 = ['tdx_czhs', 'tdx_hm', 'tdx_dhmcl', 'tdx_sxp', 'tdx_hmdr', 'tdx_tpcqpz', 'tdx_jmmm', 'tdx_nmddl', 'tdx_swl', 'tdx_yaogu']
    func2 = ['tdx_niugu', 'tdx_buerfameng', 'tdx_yaoguqidong', 'tdx_ygqd_test', 'tdx_blftxg', 'tdx_cptlzt', 'tdx_yhzc', 'tdx_yhzc_macd', 'tdx_yhzc_kdj']
    func3 = ['tdx_bjmm', 'tdx_bjmm_jzmd', 'tdx_bjmm_yhzc', 'tdx_bjmm_new', 'tdx_sxjm', 'tdx_ltt', 'tdx_blft', 'tdx_cci_xg', 'tdx_WYZBUY', 'tdx_bdzh']
    func4 = ['tdx_skdj_lstd', 'tdx_lyqd', 'tdx_sl5560', 'tdx_lbqs', 'tdx_zttj', 'tdx_zttj1', 'tdx_cmfx', 'tdx_TLBXX'] ##, 'tdx_LDX'
    func5 = ['tdx_WYZ17MA', 'tdx_qszn', 'tdx_cci', 'tdx_ngqd', 'tdx_bollxg_start', 'tdx_DQS', 'tdx_JZZCJSD', 'tdx_CDYTDXG', 'tdx_BOLL_EMA', 'tdx_HJYHK']
    func6 = ['tdx_LLXGSQ', 'tdx_WWDGWY', 'tdx_WWXGSQ', 'tdx_WWYHXG', 'tdx_WWMACDJC', 'tdx_WWKDJJC', 'tdx_SHYM', 'tdx_QIANFU', 'tdx_HW168QS']
    func7 = ['tdx_sxzsl', 'tdx_ZQNG', 'tdx_JGCM', 'tdx_21PPQTP'] ##
    if idxCalcFlg:
        func2 = ['tdx_niugu', 'tdx_buerfameng', 'tdx_yaoguqidong', 'tdx_blftxg', 'tdx_cptlzt', 'tdx_yhzc', 'tdx_yhzc_macd', 'tdx_yhzc_kdj']
        func4 = ['tdx_skdj_lstd', 'tdx_lyqd', 'tdx_zttj', 'tdx_zttj1', 'tdx_TLBXX'] ##, 'tdx_LDX'
        func7 = ['tdx_JGCM'] ##
#     func = 'tdx_czhs, tdx_hm, tdx_dhmcl, tdx_sxp, tdx_hmdr, tdx_tpcqpz, tdx_jmmm, tdx_nmddl, tdx_swl, tdx_yaogu \
#     , tdx_niugu, tdx_buerfameng, tdx_yaoguqidong, tdx_ygqd_test, tdx_blftxg, tdx_cptlzt, tdx_yhzc, tdx_yhzc_macd, tdx_yhzc_kdj, tdx_sxp_yhzc \
#     , tdx_bjmm, tdx_bjmm_jzmd, tdx_bjmm_yhzc, tdx_bjmm_new, tdx_sxjm, tdx_ltt, tdx_blft, tdx_cci_xg, tdx_WYZBUY, tdx_bdzh \
#     , tdx_skdj_lstd, tdx_lyqd, tdx_sl5560, tdx_lbqs, tdx_zttj, tdx_zttj1, tdx_cmfx, tdx_TLBXX, tdx_LDX, tdx_TLBXXF \
#     , tdx_WYZ17MA, tdx_qszn, tdx_cci, tdx_ngqd, tdx_bollxg_start, tdx_DQS, tdx_JZZCJSD, tdx_CDYTDXG, tdx_BOLL_EMA, tdx_hjy \
#     , tdx_LLXGSQ, tdx_WWDGWY, tdx_WWXGSQ, tdx_WWYHXG, tdx_WWMACDJC, tdx_SHYM, tdx_QIANFU, tdx_HW168QS \
#     '
    funcN = ['tdx_DQS', 'tdx_JZZCJSD', 'tdx_WWYHXG', 'tdx_WWMACDJC', 'tdx_WWKDJJC','tdx_sl5560', 'tdx_HJYHK', 'tdx_TLBXX', 'tdx_DSCJ']
#     funcN = ['tdx_sl5560', 'tdx_HJYHK']
    if funcInput == '':
        func = func1 + func2 + func3 + func4 + func5 + func6 + func7
    else:
        func = funcInput.split(',')

    if funcInput == '' and calcType == 'N':
        func = funcN
        
    
#     func = func[:2] ## for test
#     if calcType == 'N':
    while True:
        day_select(codelist, back_time, func, calcType)
        if calcType != 'N':
            break
        else:
            nowtime = datetime.datetime.now().time()
            if nowtime > datetime.time(15, 10, 0):
                print("end calcl")
                break
            if nowtime > datetime.time(11, 35, 0) and nowtime < datetime.time(13, 5, 0):
                time.sleep(10)
                print("log:sleep PM")
                continue
            tblFlg = datetime.datetime.strftime(datetime.datetime.now(),'%y-%m-%d-%H-%M')
            time.sleep(10)
    end_t = datetime.datetime.now()
    print(end_t, '__name__ spent:{}'.format((end_t - start_t)))
#     print("__name__", len(dataR))





# db.getCollection('day-select-ff').aggregate(
# [
#         {
#             $match:{
#                 'date_stamp':{$eq: 1706025600.0}
#             }
#         },
#         {
#             $group:{
#                 _id: "$code",
#                 date: {$first: '$date'},
#                 sum_score: {$sum: '$score'}
#             }
#         }
#         ,{
#             $sort:{sum_score:-1}
#         }
# ]
# )