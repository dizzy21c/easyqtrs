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
databuf_mongo_r = Manager().dict()
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
    
def do_main_work(code, data):
    # hold_price = positions['price']
    now_price = data['now']
    # print("code=%s, price=%.2f" % (code, now_price))
    # high_price = data['high']
    ##TODO 绝对条件１
    ## 止损卖出
    # if now_price < hold_price / 1.05:
    #     log.info("code=%s now=%6.2f solding..." % (code, now_price))
    ## 止赢回落 %5，卖出
    # if now_price > hold_price * 1.02 and now_price < high_price / 1.03:
    #     log.info("code=%s now=%6.2f solding..." % (code, now_price))
        # 卖出

    # now_vol = data['volume']
    # last_time = pd.to_datetime(data['datetime'][0:10])
    # print("code=%s, data=%s" % (self.code, self._data['datetime']))
    df_day = data_buf_day[code]
    # print(len(df_day))
    # print("code=%s, nums=%d" % (code, len(df_day)))
    # print("code=%s, data=%s" % (data['code'], data['datetime']))
    # print(data)
    df_day = new_df(df_day, data, now_price)
    # print(df_day.tail())
    #chk_flg, _ = tdx_a06_zsd(df_day)
    chk_flg, _ = tdx_yhzc(df_day)
    # chk_flg2, _ = tdx_hm(df_day)
    # chk_flg3, _ = tdx_tpcqpz(df_day)
    # df_day.loc[last_time]=[0 for x in range(len(df_day.columns))]
    # df_day.loc[(last_time,code),'open'] = data['open']
    # df_day.loc[(last_time,code),'high']= data['high']
    # df_day.loc[(last_time,code),'low'] = data['low']
    # df_day.loc[(last_time,code),'close'] = now_price
    # df_day.loc[(last_time,code),'vol'] = data['volume']
    # df_day.loc[(last_time,code),'amount'] = data['amount']
    # df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
    # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']
    # df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

    # df_v=pd.concat([MA(df_day.vol, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df_v.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

    # df_a=pd.concat([MA(df_day.amount, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df_a.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

    # self.log.info("data=%s, m5=%6.2f" % (self.code, df.m5.iloc[-1]))
    # self.upd_min(5)
    # self.log.info()
    # if now_vol > df_v.m5.iloc[-1]:
    # self.log.info("code=%s now=%6.2f pct=%6.2f m5=%6.2f, now_vol=%10f, m5v=%10f" % (self.code, now_price, self._data['chg_pct'], df.m5.iloc[-1], now_vol, df_v.m5.iloc[-1]))
    # if toptop_calc(df_day):
    # if now_price < df.m5.iloc[-1]:
    ## 低于５日线，卖出
    # print(chk_flg[-1])
    if chk_flg[-1]:
        print("calc code=%s now=%6.2f" % (code, now_price))
    # if chk_flg2[-1]:
    #     print("calc code=%s now=%6.2f HM" % (code, now_price))
    #
    # if chk_flg3[-1]:
    #     print("calc code=%s now=%6.2f TPCQPZ" % (code, now_price))


def do_get_data_mp(key, codelist, st_start, st_end, type=''):
    mongo_mp = MongoIo()
    # start_t = datetime.datetime.now()
    # print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
    databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end=st_end)
    if type == 'B':
        td = datetime.datetime.strptime(st_end, '%Y-%m-%d') + datetime.timedelta(1)
        st_backtime = td.strftime('%Y-%m-%d')
        databuf_mongo_r[key] = mongo_mp.get_stock_day(codelist, st_start=st_backtime, st_end=st_backtime)

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

def get_data(codelist, st_start, st_end, type):
    start_t = datetime.datetime.now()
    print("begin-get_data:", start_t)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    # codelist = ['600380','600822']

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
        pool.apply_async(do_get_data_mp, args=(i, code_dict[i], st_start, st_end, type))

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

def tdx_func_mp(func_name, codelist, type='', backTime=''):
    start_t = datetime.datetime.now()
    # if start_t.time() < datetime.time(9, 30, 00):
    #     print("read web data from tencent begin-time:", start_t)
    #     newdatas = fetch_quotation_data(source="tencent")
    # else:
    print("read web data-begin-time:", start_t)
    if type == 'B':
        mongo = MongoIo()
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

    task_list = []
    # pool = Pool(cpu_count())
    for key in range(pool_size):
        # tdx_func(databuf_mongo[key])
        # task_list.append(executor_func.submit(tdx_func, databuf_mongo[key], newdatas, func_name, type=type))
        task_list.append(executor_func.submit(tdx_func, key, newdatas, func_name, type=type))
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
    for task in as_completed(task_list):
        a = task.result()
        # pass
        if len(dataR) == 0:
            dataR = task.result()
        else:
            dataR = dataR.append(task.result())
    dataR = dataR.fillna(0)
    dataR = dataR.sort_values(by="dao")
    # todo end
    print(dataR)
    dataR.to_csv("step-%s-%s.csv" % (func_name, backTime))

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


# def tdx_func(datam, newdatas, func_name, code_list = None, type=''):
def tdx_func(key, newdatas, func_name, code_list = None, type=''):
    """
    准备数据
    """
    # highs = data.high
    datam = databuf_mongo[key]
    if type == 'B':
        datam_r = databuf_mongo_r[key]
    mongo_np = MongoIo()
    start_t = datetime.datetime.now()
    print("begin-tdx_func:", start_t)
    dataR = pd.DataFrame()
    if code_list is None:
        code_list = datam.index.levels[1]
    for code in code_list:
        data=datam.query("code=='%s'" % code)
        # pb_value = pba_calc(code)
        # if not pb_value:
        #     print("pb < 0 code=%s" % code)
        #     continue
        try:
            if type == 'B':
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
            if type == 'B':
                try:
                    datal=datam_r.query("code=='%s'" % code) 
                    last_price = datal['close'][-1]
                except:
                    print("last-date=0, code=", code)
                    last_price = 0
                    continue
            # if (code == '003001'):
            #     print(data)
            #     print(newdata)
            data = new_df(data.copy(), newdata, now_price)
            # chk_flg, _ = tdx_dhmcl(df_day)
            # tdx_base_func(data, "tdx_dhmcl", code)
            # tdx_base_func(data.copy(), "tdx_dhmcl", code)
            # tdx_base_func(data, "tdx_sxp", code)
            # tdx_base_func(data.copy(), "tdx_hmdr", code)
            calcR = tdx_base_func(data.copy(), func_name, code, newdata, last_price, mongo_np)
            if calcR == {}:
                continue
            dataR = dataR.append(calcR, ignore_index=True)
            # if len(dataR):
            #     dataR = pd.DataFrame(calcR)
            # else:
            #     dataR.append(pd.DataFrame(calcR))
        except Exception as e:
            print("error code=%s" % code)
            print("error code=", e)
            # return
    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func spent:{}'.format((end_t - start_t)))
    print("tdx-fun-result-len", len(dataR))
    return dataR


# print("pool size=%d" % pool_size)
def tdx_base_func(data, func_names, code, newData, lastPrice, mongo_np, code_list = None):
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
    PCT4 = lastPrice / nowOpen - 1
    PCT4 = lastPrice / nowPrice - 1
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
    for func_name in func_names.split(","):
#         print("func-name", func_name)
        try:
            tdx_func_result, tdx_func_sell_result, next_buy = eval(func_name)(data)
            if tdx_func_result[-1] == 0 or tdx_func_result[-2] == 0:
#             if dao <= 0:
                return {}
            # tdx_func_result, next_buy = tdx_a06_zsd(data)
        # 斜率
        except:
            return {}
#             print("calc %s code=%s ERROR:FUNC-CALC-ERROR " % (func_name, code))
#             tdx_func_result, tdx_func_sell_result, next_buy = [0], [0], False
        
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
    p1 = "%4.1f" % (PCT1 * 100)
    p3 = "%4.1f" % (PCT3 * 100)
    p4 = "%4.1f" % (PCT4 * 100)
    return {'code': code, 'now':nowPrice, 'dao': tdx_func_result[-1], 'p1':p1, 'p3': p3, 'p4': p4}

def main_param(argv):
    st_begin = ''
    st_end = ''
    func = ''
    type = ''
    back_time = ''
    all_data = ''
    try:
        opts, args = getopt.getopt(argv[1:], "hb:e:f:t:r:a:", ["st-begin=", "st-end=", "func=", "type=", "realdata-date=", 'all-data='])
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
            func = '%s' % arg
        elif opt in ("-t", "--type"):
            type = arg
        elif opt in ("-r", "--realdata-date"):
            back_time = arg
        elif opt in ("-a", "--all-date"):
            all_data = arg
    return st_begin, st_end, func, type, back_time, all_data

if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)

    # st_start, st_end, func = main_param(sys.argv)
    # print("input", st_start, st_end, func)
    st_start, st_end, func, type, back_time, all_data = main_param(sys.argv)
    if all_data == '':
        all_data = 'position'
    codelist = getCodeList(all_data)
    # st_start = "2019-01-01"
    # func = "test"
    print("input st-start=%s, st-end=%s, func=%s, type=%s, back-time=%s, all_data = %s" % (st_start, st_end, func, type, back_time, all_data))
    # 1, 读取数据（多进程，读入缓冲）
    # 开始日期
    # data_day = get_data(st_start)
    # print(data_day)
    # indices_rsrsT = tdx_func(data_day)
    if type == 'B':
        td = datetime.datetime.strptime(back_time, '%Y-%m-%d') + datetime.timedelta(-1)
        st_end = td.strftime('%Y-%m-%d')
        # data_buf_rlast-dateday[0] = 
    
    if type != 'R':
        get_data(codelist, st_start, st_end, type)

    # 2, 计算公式（多进程，读取缓冲）
    while True:
        if type == 'R':
            tdx_func_upd_hist_order(func, codelist)
            input()
            break

        if type == 'T':
            nowtime = datetime.datetime.now().time()
            if nowtime < datetime.time(9, 24, 50):
                time.sleep(10)
                print("log:sleep PM")
                continue
            if datetime.time(11, 30, 10) < nowtime < datetime.time(12, 59, 50):
                time.sleep(10)
                # print("log:sleep AM")
                # continue

            if nowtime > datetime.time(15,0,30):
                print("end trade time.")
                # time.sleep(3600)
                # break
            
            time.sleep(10)
        print("*** loop calc begin ***")
        tdx_func_mp(func, codelist, type=type, backTime=back_time)

        if type == 'B' or type == 'T':
            input()
