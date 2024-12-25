import os.path
import sys
import time
from datetime import datetime, timedelta
import pandas as pd

from func.tdx_func import *
from func.func_sys import *
from easyquant  import MongoIo
from multiprocessing import Process, Pool, cpu_count, Manager

import baostock as bs
import pandas as pd
import time
import signal

# 自定义超时异常
class TimeoutError(Exception):
    def __init__(self, msg):
        super(TimeoutError, self).__init__()
        self.msg = msg
  
  
def time_out(interval, callback):
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutError("run func timeout")
  
        def wrapper(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(interval)       # interval秒后向进程发送SIGALRM信号
                result = func(*args, **kwargs)
                signal.alarm(0)              # 函数在规定时间执行完后关闭alarm闹钟
                return result
            except TimeoutError as e:
                callback(e)
        return wrapper
    return decorator

def timeout_callback(e):
    print("timeout_callback", e.msg)
    lg = bs.login()
    # 显示登陆返回信息
    if lg.error_code != '0':
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
    
# @time_out(2, timeout_callback)
# def task1():
#     print("task1 start")
#     time.sleep(3)
#     print("task1 end")

# @time_out(2, timeout_callback)
# def task2():
#     print("task2 start")
#     time.sleep(1)
#     print("task2 end")
    
minutes_field = "date,time,code,open,high,low,close,volume,amount,adjustflag"
day_field = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM"
w_m_field = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"
profile_field = 'code,pubDate,statDate,roeAvg,npMargin,gpMargin,netProfit,epsTTM,MBRevenue,totalShare,liqaShare'
WEEK = 'w'
MONTH = 'm'
QFQ = '2'
HFQ = '1'
BFQ = '3'

databuf_mongo = Manager().dict()

def dateStr2stamp(dateObj):
#     dateStr = dateObj[0:12]
    date = time.mktime(time.strptime(dateObj, '%Y-%m-%d %H:%M:%S'))
    return date

def save_from_tdx_file(strPathFileName, today):
    mongo_mpd = MongoIo()
    codeDf = pd.read_csv(strPathFileName, sep='\t')##, encoding='iso-8859-1')
    ins_data = []
#     today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
    # print(today)
    for idx in codeDf.index:
        monv = {}
        code = 'none'
        try:
            monv['date'] = today
            tdf = codeDf.iloc[idx]
    #         print(codeDf.iloc[idx])
            code = tdf['代码'][2:8]
            if code[:1] == '6':
                monv['_id'] = 'sh.%s-%s' % (code, today)
            else:
                monv['_id'] = 'sz.%s-%s' % (code, today)
            monv['code'] = code
            monv['open'] = float(tdf['今开'])
            monv['high'] = float(tdf['最高'])
            monv['low'] = float(tdf['最低'])
            monv['close'] = float(tdf['现价'])
            monv['volume'] = float(tdf['总量'])*100
            monv['amount'] = float(tdf['总金额'])*10000
            monv['adjustflag'] = 2
            monv['turn'] = float(tdf['换手%'])
            monv['pctChg'] = float(tdf['涨幅%'])
            try:
                monv['peTTM'] = float(tdf['市盈(动)'])
            except:
                monv['peTTM'] = -1.0
            monv['pbMRQ'] = 0
            monv['psTTM'] = 0
            monv['pcfNcfTTM'] = 0
            monv['pcfNcfTTM'] = 0
            monv['date_stamp'] = mongo_mpd.dateStr2stamp(today)
    #         print(monv)
            try:
                mongo_mpd.save('stock_day_qfq_60', monv)
            except:
    #             print("save mongo error", code)
                pass
        except:
            print("convert error", code)
    #         pass
    #         break
    #     if idx == 1:
    #     break

@time_out(10, timeout_callback)
def fetch_k_day(code="sh.600606", p_begin_day: str = '2024-09-01', p_end_day: str = None):
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg,
    # 换手率\涨跌幅（百分比）\滚动市盈率\市净率\滚动市销率\滚动市现率\
    # 日周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM

    # frequency：数据类型，默认为d，日k线；d = 日k线、w = 周、m = 月、5 = 5
    # 分钟、15 = 15
    # 分钟、30 = 30
    # 分钟、60 = 60
    # 分钟k线数据，不区分大小写；指数没有分钟线数据；周线每周最后一个交易日才可以获取，月线每月最后一个交易日才可以获取

    # adjustflag：复权类型，默认不复权：3；1：后复权；2：前复权。已支持分钟线、日线、周线、月线前后复权
    if p_end_day is None:
        p_end_day = time.strftime('%Y-%m-%d')
#     print(p_begin_day, p_end_day)
    rs = bs.query_history_k_data_plus(code,
                                      minutes_field,
                                      start_date=p_begin_day, end_date=p_end_day,
                                      frequency="60", adjustflag=QFQ)
    data_list = []
#     if rs is None:
#         return pd.DataFrame()
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    # 添加方式
    # result.to_csv(p_file, index=False, mode='a+', header=True)
#     print(result.head())
    return result

def update_data(codelist, start = 0):
    start_t = datetime.datetime.now()
    print("begin-update_data:", start_t)
    mongo_mpd = MongoIo()
    tblName = 'stock_day_qfq_60'
    pool_size = cpu_count()
    code_dict = codelist2dict(codelist, pool_size)
    j = 0
#     for i in range(4,5): #code_dict.keys():
    for i in code_dict.keys():
#         pool.apply_async(do_update_data_mp, args=(i, code_dict[i]))
        for xcode in code_dict[i][start:]:
            j += 1
            print("do update data for ", xcode, "... ...", j, len(codelist))
            do_update_data_mp(tblName, mongo_mpd, xcode, i)
    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'update_data spent:{}'.format((end_t - start_t)))

def ins_mongo_data(mongo_mpd, tdata, code):
    if len(tdata) > 0:
        akey = tdata.columns.values
        ins_data = []
        for index, row in tdata.iterrows():
            if row['volume'] == '':
                continue
            monv = {}
            for x in akey:
                if x == 'code':
                    monv[x] = row[x][3:]
                elif x == 'date':
                    monv[x] = row[x]
                elif x == 'time':
                    a = row[x]
                    monv[x] = '%s-%s-%s %s:%s:00'% (a[:4],a[4:6],a[6:8],a[8:10],a[10:12])
                else:
                    try:
                        monv[x] = float(row[x])
                    except:
                        monv[x] = 0.0
#             print("conv error", code, row['time'], type(row['time']))

            monv['_id'] = '%s-%s' % (monv['code'], monv['time'])
            monv['date_stamp'] = dateStr2stamp(monv['time'])
    # print(monv)
            ins_data.append(monv)
        #     print(row.tolist())
        if len(ins_data) > 0:
            try:
                mongo_mpd.save(tblName, ins_data)
            except:
                print("ins error", code)

    
def do_update_data_mp(tblName, mongo_mpd, xcode, key):
    tblName = 'stock_day_qfq_60'
    if '0' == xcode[:1] or '3' == xcode[:1]:
        code = "sz.%s" % xcode
#             print("sz.%s" % x)
    else:
        code = "sh.%s" % xcode
    if len(databuf_mongo[key]) == 0:
        codeData = []
    else:
        codeData = databuf_mongo[key].query(" code == '%s'" % xcode)
    ##debug
#     if xcode == '300088':
#         print(key, xcode, len(codeData), len(databuf_mongo[key]))
        
    if len(codeData) > 0:
        today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
        p_begin_day = codeData.index[-1][0].strftime("%Y-%m-%d") ##倒数2条
        fq1Close = codeData.iloc[-1].close
#         print("codeData", code, p_begin_day, codeData.tail())        
#         p_begin_day = get_next_date(p_begin_day)
        p_begin_year = int(p_begin_day[:4])
        p_end_day = '%s-12-31' % p_begin_year
#         if p_begin_day > p_end_day:
#             p_end_day = '%s-12-31' % p_begin_year
        if p_begin_day > today:
            ##last data
            return
        year = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
        for ldate in range(p_begin_year,int(year)+1):
            if ldate > p_begin_year:
                p_begin_day = '%s-01-01' % ldate
                p_end_day = '%s-12-31' % ldate
#             for i in range(0,5):
#                 print("cond", code, p_begin_day, p_end_day)
            tdata = fetch_k_day(code, p_begin_day = p_begin_day, p_end_day = p_end_day)
#             print("tdata result", code, p_begin_day, p_end_day, tdata.tail())
#                 continue
            if len(tdata) <= 0:
                break
#             try:
            for x in tdata.index:
                if pd.to_datetime(tdata.iloc[x].date) == pd.to_datetime(p_begin_day):
                    continue
#             fq2Close = float(tdata.iloc[-1].close)
#             if fq1Close == fq2Close:
                ins_mongo_data(mongo_mpd, tdata[x:], xcode)
                break
#             else:
#                 mongo_mpd.removeStockDataByCode(xcode)
#                 year = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
#                 for ldate in range(2024,int(year)+1):
#                     p_begin_day = '%s-01-01' % ldate
#                     p_end_day = '%s-12-31' % ldate
#                     tdata = fetch_k_day(code, p_begin_day = p_begin_day, p_end_day = p_end_day)
#                     ins_mongo_data(mongo_mpd, tdata, xcode)
#             break
#             except Exception as e:
#                 time.sleep(3)
# #                     bs.login()
#                 lg = bs.login()
#                 # 显示登陆返回信息
#                 if lg.error_code != '0':
#                     print('login respond error_code:' + lg.error_code)
#                     print('login respond  error_msg:' + lg.error_msg)

#                 continue
#         if len(tdata) > 0:
#             akey = tdata.columns.values
#             ins_data = []
#             for index, row in tdata.iterrows():
#                 monv = {}
#                 for x in akey:
#                     if x == 'code':
#                         monv[x] = row[x][3:]
#                     elif x == 'date':
#                         monv[x] = row[x]
#                     else:
#                         try:
#                             monv[x] = float(row[x])
#                         except:
#                             monv[x] = 0.0
# #                                 print("conv error", code, row)

#                 monv['_id'] = '%s-%s' % (row['code'], row['date'])
#                 monv['date_stamp'] = mongo_mpd.dateStr2stamp(row['date'])
# #                     print(monv)
#                 ins_data.append(monv)
#             #     print(row.tolist())
#             if len(ins_data) > 0:
#                 mongo_mpd.save(tblName, ins_data)
    else:
        year = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
        for ldate in range(2024,int(year)+1):
            p_begin_day = '%s-01-01' % ldate
            p_end_day = '%s-12-31' % ldate
            tdata = fetch_k_day(code, p_begin_day = p_begin_day, p_end_day = p_end_day)
            ins_mongo_data(mongo_mpd, tdata, xcode)
#             if len(tdata) > 0:
#                 akey = tdata.columns.values
#                 ins_data = []
#                 for index, row in tdata.iterrows():
#                     monv = {}
#                     for x in akey:
#                         if x == 'code':
#                             monv[x] = row[x][3:]
#                         elif x == 'date':
#                             monv[x] = row[x]
#                         else:
#                             try:
#                                 monv[x] = float(row[x])
#                             except:
#                                 monv[x] = 0.0
# #                                 print("conv error", code, row)

#                     monv['_id'] = '%s-%s' % (row['code'], row['date'])
#                     monv['date_stamp'] = mongo_mpd.dateStr2stamp(row['date'])
# #                     print(monv)
#                     ins_data.append(monv)
#                 #     print(row.tolist())
#                 if len(ins_data) > 0:
#                     mongo_mpd.save(tblName, ins_data)
            

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
#     databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end, qfq=1)

def get_data(codelist, start = 0):
    start_t = datetime.datetime.now()
    year = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
    print("begin-get_data:", start_t)
    pool_size = cpu_count()
    code_dict = codelist2dict(codelist, pool_size)
    pool = Pool(cpu_count())
    for i in code_dict.keys():
#         print("get-data - key", i)
        pool.apply_async(do_get_data_mp, args=(i, code_dict[i][start:], '%s-01-01' % year, '%s-12-31' % year))

    pool.close()
    pool.join()

    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))
    # return data_day
def do_get_data_mp(key, codelist, st_start, st_end):
#     print("do_get_data_mp", key, codelist[:5])
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
    try:
        query= {'code': {'$in': codelist}
                ,"date_stamp":{"$lte": mongo_mp.dateStr2stamp(st_end),  "$gte": mongo_mp.dateStr2stamp(st_start)}
            }
#         print("query", query)
        ptd = mongo_mp.get_table_data('stock_day_qfq_60',query=query)#codelist, st_start=st_start, st_end = st_end, qfq=1)
        if len(ptd) > 0:
            ptd.date = pd.to_datetime(ptd.date)
            ptd.time = pd.to_datetime(ptd.time)
            ptd = ptd.set_index(["time", "code"])
            databuf_mongo[key] = ptd
#             print('data-get', key, len(databuf_mongo[key]), st_start, st_end, ptd.head())
        else:
            databuf_mongo[key] = pd.DataFrame()
    except Error:
        print("do_get_data_mp error", key, Error)
        
    
if __name__ == '__main__':
    print("python get_baostock_data.py tdx /root/ALLASTOCK20240125.xls")
    print("python get_baostock_data.py baosdk")
    # 登陆系统
    tblName = 'stock_day_qfq_60'
    print('argv', sys.argv)
#     exit(0)
    if sys.argv[1] == 'tdx':
#     '/root/全部Ａ股20240125.xls'
        fileName = sys.argv[2]
#         print("chk", today, sys.argv[2])
        today=fileName.split('/')[-1]
        try:
            today = datetime.datetime.strptime(fileName.split('/')[-1][4:12],'%Y%m%d')
            today = datetime.datetime.strftime(today,'%Y-%m-%d')
        except:
            today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
#         print('today', today)
#         exit(0)
        save_from_tdx_file(sys.argv[2], today) #'/root/全部Ａ股20240125.xls')##, encoding='iso-8859-1')
    elif sys.argv[1] == 'baosdk':
        lg = bs.login()
        # 显示登陆返回信息
        if lg.error_code != '0':
            print('login respond error_code:' + lg.error_code)
            print('login respond  error_msg:' + lg.error_msg)
            sys.exit()

        codelist = getCodeList('stock', notST = False)
        start = 0
        if len(sys.argv) >= 3: 
#             codelist = codelist[int(sys.argv[2]):]
            pool_size = cpu_count()
            start = int(int(sys.argv[2]) / pool_size)
            print("start", start, len(codelist), pool_size)
        if len(sys.argv) >= 4: 
#             codelist = codelist[int(sys.argv[2]):]
#             pool_size = cpu_count()
#             start = int(int(sys.argv[2]) / pool_size)
            freq = sys.argv[3]
            print("start", start, len(codelist), pool_size)
#         if len(sys.argv) >= 4: 
#             codelist = codelist[:int(sys.argv[3])]
#         codelist = codelist[:24]
        get_data(codelist, start)
        update_data(codelist, start)
    elif sys.argv[1] == 'test-sdk':
        lg = bs.login()
        # 显示登陆返回信息
        if lg.error_code != '0':
            print('login respond error_code:' + lg.error_code)
            print('login respond  error_msg:' + lg.error_msg)
            sys.exit()
        code = sys.argv[2]
#         update_data([sys.argv[2]])
        p_begin_day = '%s-01-01' % sys.argv[3]
        p_end_day = '%s-12-31' % sys.argv[3]
        tdata = fetch_k_day(code, p_begin_day = p_begin_day, p_end_day = p_end_day)
        print(tdata.tail())