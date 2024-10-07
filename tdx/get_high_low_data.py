import os.path
import sys
import time
from datetime import datetime, timedelta
import pandas as pd

from func.tdx_func import *
from func.func_sys import *
from easyquant  import MongoIo
from multiprocessing import Process, Pool, cpu_count, Manager

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
    print(e.msg)
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
    
databuf_mongo = Manager().dict()

def h_l_line(p_df, t=21,period=1000,fn=None,cur_idx=0, cup = True, firstCalc = True):
    """
    根据给定的周期找出最高最低点的日期和数据，然后计算对应的斐波纳契数据
    :param fn: 高低线输出到文件,如果文件参数为None则不输出到文件
    :param p_df:股票交易数据
    :param t:数据周期
    :param period:数据长度
    :return:有效数据点，包括股票代码，日期，高低点周期交易天数、高低点周期自然天数
    """
    data = pd.DataFrame([])
    if p_df is None:
        return data
    if firstCalc and len(p_df)<t:
        return data
    # 获取最新的period条数据
    # df1 = p_df.tail(period).reset_index(drop=True)
    df1 = p_df[['close','high','low','date','code']].copy()
    df1['top']=''
    df1['cv'] = 0 #添加一列为后续保留值准备
    high = df1['high']
    low = df1['low']

    # 保留数据的df
#     data = pd.DataFrame([])
    #获取首行为有效的数据点,加入到保留数据框中
    ci=cur_idx
    if ci == 0:
        df1.loc[ci,'cv'] = df1.iloc[ci].high #最高价作为当前价
        df1.loc[ci,'top'] = 'b'
        first = df1.iloc[ci:ci+1]
        # data = data.append(first)
        data = pd.concat([data,first])

        #取第一个日期的最高值作为当前值,开始为0，默认为上涨周期
    cv=df1.iloc[ci].high
    cup=True
    ptd = pd.to_datetime(df1.iloc[ci].date, format='%Y-%m-%d')
    ntd = pd.to_datetime(df1.iloc[ci].date, format='%Y-%m-%d')
    # print("ptd", ptd)
    #循环处理每一个周期
    n=cur_idx
    lt = t
    # while ci<df1.index.max():
    while n<df1.index.max():
        if n < ci:
            n = ci
        n=n+1
        
        # 取含当前日期的一个周期的最高和最低价以及索引值,如果出现下一个周期中当前点成为了这个周期的最高和最低点即当前点未变化则
        # 在前周期长度上扩展1个周期,一旦出现拐点则恢复周期。
        # 周期超高了数据长度则结束，当前点加入到数据有效点中。
        # 为什么不是从下一个点找周期，因为下一个点开始的周期则一定存在一个高低点，而这个高低点和当前点的高点或低点比较后一定会
        # 出现一个拐点，有时候不一定有拐点存在,所以要包含当前点
        # print("ci", ci, ci + lt,ptd,cup)
        ih = high[ci:ci+lt].idxmax()
        il = low[ci:ci+lt].idxmin()
        ihv = df1.iloc[ih].high
        ilv = df1.iloc[il].low
        # print("n1", n, ci,lt,ih,il, ihv, ilv)
        if (ih==ci) & (il==ci):
            #数据结束了吗?如果结束了则直接添加当前数据到数据点和最后一个数据到数据点
            if (ci+lt)>df1.index.max():
                # 数据结束了,最后一个数据是否要添加到数据点中，由循环结束时处理
                break
            else:
                # 三点重叠但数据为结束 , 周期延长重新计算
                lt = lt + t
                continue
        if cup:
            # 上涨阶段
            if (ihv >= cv) & (ci != ih):
                # print("n1", n, ci, cv, lt, ih, il, ihv, ilv)
                # 如果上升周期中最高价有更新则仍然上涨持续，上涨价格有效，下跌的价格为噪声
                ci = ih
                cv = ihv
                cup = True
            else:
                # 未持续上涨，则下跌价格有效，出现了转折，此时上一个价格成为转折点价格,恢复计算周期
                df1.loc[ci,'cv'] = cv
                p_ntd = ntd
                ntd = pd.to_datetime(df1.iloc[il].date, format='%Y-%m-%d')
#                 print("ntd-up", ptd, p_ntd, ntd, lt, t, (ntd - ptd).days, il, ih, ilv, ihv)
                if (ntd - p_ntd).days > 0 and (ntd - ptd).days > 0 and (ntd - ptd).days < (t / 2 + 1):
                    lt = lt + int(t / 2)
                else:
                    # print("cup date", ptd,ntd)
                    ptd = ntd
                    # data = data.append(df1.iloc[ci:ci + 1])
                    df1.loc[ci,'top'] = 'u'
                    if ci > 0:
                        data = pd.concat([data,df1.iloc[ci:ci + 1]])
                    ci = il
                    cv = ilv
                    cup = False
                    lt = t
        else:
            # 下跌阶段
            if (ilv<=cv) & (ci != il):
                # 下跌阶段持续创新低，则下跌价格有效，上涨价格为噪声
                ci = il
                cv = ilv
                cup = False
            else:
                p_ntd = ntd
                ntd = pd.to_datetime(df1.iloc[il].date, format='%Y-%m-%d')
                # print("ntd-d", ptd, ntd,lt,ntd - ptd < t / 2 + 1)
#                 print("ntd-dn", ptd, p_ntd, ntd, lt, t, (ntd - ptd).days, il, ih, ilv, ihv)
                if (ntd - p_ntd).days > 0 and (ntd - ptd).days > 0 and (ntd - ptd).days < (t / 2 + 1):
                    lt = lt + int(t / 2)
                else:
                    # print("down date", ptd,ntd)
                    ptd = ntd
                    # 未持续下跌，此时转为上涨，上涨价格有效，此时上一个价格成为转折点价格,恢复计算周期
                    df1.loc[ci, 'cv'] = cv
                    # data = data.append(df1.iloc[ci:ci + 1])
                    df1.loc[ci,'top'] = 'd'
                    data = pd.concat([data,df1.iloc[ci:ci + 1]])
                    ci = ih
                    cv = ihv
                    cup = True
                    lt = t

        # print(df1.iloc[ci:ci+1])
        # print(n,ci,cv,cup,ih,il)

        # if last+t>=df1.index.max():
        #     # 最后计算恰好为最后一个周期，则直接加入最后一个周期进入数据有效点，并且结束循环
        #     last = df1.index.max()
        #     df1.loc[last, 'cv'] = df1.iloc[last].close
        #     data = data.append(df1.iloc[last:last + 1])
        #     break
    #结束了，把当前点加入到数据有效点中
    print("n1", n, ci, cv, lt, ih, il, ihv, ilv, cup)
    df1.loc[ci, 'cv'] = cv
    df1.loc[ci,'top'] = 'e'
    # data = data.append(df1.iloc[ci:ci + 1])
    data = pd.concat([data,df1.iloc[ci:ci + 1]])
    if ci != df1.index.max():
        # 当前点不是最后一个点，则把最后一个点加入到数据点中
        df1.loc[df1.index.max(), 'cv'] = df1.iloc[df1.index.max()].close
        # data = data.append(df1.tail(1))
        data = pd.concat([data,df1.tail(1)])

    data = data.reset_index(drop=False)
    # 计算高低点转换的交易日数量即时间周期
    data['period'] = (data['index'] - data['index'].shift(1)).fillna(0)
    # 计算日期的差值,将字符串更改为日期
    dateS = pd.to_datetime(data['date'],format='%Y-%m-%d')
    days = dateS - dateS.shift(1)
    # 填充后转换为实际的天数数字
    days = (days.fillna(pd.Timedelta(0))).apply(lambda x:x.days)
    data['days'] = days
    # 对日期进行转换
    data['date']=dateS.apply(lambda x:x.strftime('%Y-%m-%d'))
    return data

def update_data(codelist,tblName, calcStep):
    start_t = datetime.datetime.now()
    print("begin-update_data:", start_t)
#     tblName = 'stock_day_qfq'
    pool_size = cpu_count()
    code_dict = codelist2dict(codelist, pool_size)
    pool = Pool(pool_size)
#     j = 0
#     for i in range(4,5): #code_dict.keys():
    for i in code_dict.keys():
        print("do_update_data_mp data for ", i)
        pool.apply_async(do_update_data_mp, args=(tblName, code_dict[i], i, calcStep))
#         for xcode in code_dict[i]:
#             pool.apply_async(do_update_data_mp, args=(tblName, mongo_mpd, code, i))
# #             do_update_data_mp(tblName, mongo_mpd, xcode, i)
    pool.close()
    pool.join()

    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'update_data spent:{}'.format((end_t - start_t)))

def ins_mongo_data(mongo_mpd, tdata, code):
    if len(tdata) > 0:
        akey = tdata.columns.values
        ins_data = []
        for index, row in tdata.iterrows():
#             if row['volume'] == '':
#                 continue
            monv = {}
            for x in akey:
                if x == 'code':
                    monv[x] = row[x]
                elif x == 'top':
                    monv[x] = row[x]
                elif x == 'date':
                    monv[x] = row[x]
                else:
                    try:
                        monv[x] = float(row[x])
                    except:
                        monv[x] = 0.0
    # print("conv error", code, row)

            monv['_id'] = '%s-%s' % (row['code'], row['date'])
#             monv['date_stamp'] = mongo_mpd.dateStr2stamp(row['date'])
    # print(monv)
            ins_data.append(monv)
        #     print(row.tolist())
        if len(ins_data) > 0:
            try:
                mongo_mpd.save(tblName, ins_data)
            except:
                print("ins error", code)
    
def do_update_data_mp(tblName, codeList, key, calcStep):
#     print("do update data for ", tblName, "... ...", codeList, key)   
    mongo_mpd = MongoIo()
#     for xcode in codeList:
#         print(key, xcode)
#     tblName = 'stock_day_qfq'
#     if '0' == xcode[:1] or '3' == xcode[:1]:
#         code = "sz.%s" % xcode
# #             print("sz.%s" % x)
#     else:
#         code = "sh.%s" % xcode
    for xcode in codeList:
#         print(key, xcode)
        if len(databuf_mongo[key]) == 0:
            codeData = []
        else:
            codeData = databuf_mongo[key].query(" code == '%s'" % xcode)
#             print("pass2", len(codeData))
        ##debug
    #     if xcode == '300088':
    #         print(key, xcode, len(codeData), len(databuf_mongo[key]))

        if len(codeData) > 0:
#             print("pass")
            calcHLData = codeData.tail(3)
            if len(calcHLData) == 3:
#                 print('calcHLData1',calcHLData)
                st_start = calcHLData.iloc[0].date
#                 cup = calcHLData.iloc[0].top == 'u'
#                 iindex = calcHLData.iloc[0]['index']
#                 st_start2 = calcHLData.iloc[1].date
#                 iindex2 = calcHLData.iloc[1]['index']
#                 iperiod = calcHLData.iloc[1]['period']
                idKey = calcHLData.iloc[2]['_id']
#                 print('st_start', st_start, cup)
                srcData = mongo_mpd.get_stock_day(code=[xcode], st_start=st_start, st_end = '2030-12-31', qfq=1)
                srcData = srcData.reset_index()
                dstHLData=h_l_line(srcData, t=calcStep)
#                 print('calcHLData20',dstHLData)
                if len(dstHLData) >= 3:
#                     dstHLData.loc[1,'index']=iindex2 + dstHLData.iloc[1]['period'] - iperiod
                    print('calcHLData21',dstHLData.iloc[2:])
                    mongo_mpd.removeData(tblName, {'_id':idKey})
                    ins_mongo_data(mongo_mpd, dstHLData.iloc[2:], xcode)
    #         today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
    #         p_begin_day = codeData.index[-1][0].strftime("%Y-%m-%d") ##倒数2条
    #         fq1Close = codeData.iloc[-1].close
    # #         p_begin_day = get_next_date(p_begin_day)
    #         p_begin_year = int(p_begin_day[:4])
    #         p_end_day = '%s-12-31' % p_begin_year
    # #         if p_begin_day > p_end_day:
    # #             p_end_day = '%s-12-31' % p_begin_year
    #         if p_begin_day > today:
    #             ##last data
    #             return
    #         year = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
    #         for ldate in range(p_begin_year,int(year)+1):
    #             if ldate > p_begin_year:
    #                 p_begin_day = '%s-01-01' % ldate
    #                 p_end_day = '%s-12-31' % ldate
    #             tdata = fetch_k_day(code, p_begin_day = p_begin_day, p_end_day = p_end_day)
    #             fq2Close = float(tdata.iloc[0].close)
    #             if fq1Close == fq2Close:
    #                 ins_mongo_data(mongo_mpd, tdata[1:], xcode)
    #             else:
    #                 mongo_mpd.removeStockDataByCode(xcode)
    #                 year = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
    #                 for ldate in range(1990,int(year)+1):
    #                     p_begin_day = '%s-01-01' % ldate
    #                     p_end_day = '%s-12-31' % ldate
    #                     tdata = fetch_k_day(code, p_begin_day = p_begin_day, p_end_day = p_end_day)
    #                     ins_mongo_data(mongo_mpd, tdata, xcode)
        else:
            srcData = mongo_mpd.get_stock_day(code=[xcode], st_start='1990-01-01', st_end = '2030-12-31', qfq=1)
#             print(srcData.head())
            srcData = srcData.reset_index()
            dstHLData=h_l_line(srcData, t=calcStep)
            if len(dstHLData) > 0:
                ins_mongo_data(mongo_mpd, dstHLData, xcode)

def get_data(codelist):
    start_t = datetime.datetime.now()
    year = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
    print("begin-get_data:", start_t)
    pool_size = cpu_count()
    code_dict = codelist2dict(codelist, pool_size)
    # print("get-data", code_dict)
    pool = Pool(cpu_count())
    for i in code_dict.keys():
        pool.apply_async(do_get_data_mp, args=(i, code_dict[i], '%s-01-01' % str(int(year)-2), '%s-12-31' % year))

    pool.close()
    pool.join()

    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))
    # return data_day
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

#     try:
#         databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end, qfq=1)
#         print('data-get-1', key, len(databuf_mongo[key]), st_start, st_end)
#     except Error:
#         print("do_get_data_mp error", key, Error)

    try:
        databuf_mongo[key] = mongo_mp.get_table_data(tblName, query={"code":{"$in":codelist}})
        print('data-get-2', key, len(databuf_mongo[key]))
    except Error:
        print("do_get_data_mp error", key, Error)
        
    
if __name__ == '__main__':
    print("python get_high_low_data.py 21")
    print('argv', sys.argv)
    # 登陆系统
    calcStep = int(sys.argv[1])
    tblName = 'stock_high_low_data_%d' % calcStep
    print('tblName', tblName)
#     exit(0)
    codelist = getCodeList('stock', notST = False)
#     codelist = codelist[:8]
#     print(codelist)
    get_data(codelist)
    update_data(codelist, tblName, calcStep)
