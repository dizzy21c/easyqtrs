import os
import struct
import pandas as pd
import numpy as np
import time, datetime
import sys, getopt
# import multiprocessing
# import talib as tdx
from easyquant import MongoIo
import matplotlib.pyplot as plt
# from easyquant.indicator.base import *
# import QUANTAXIS as QA

import talib
import matplotlib.ticker as ticker
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import mplfinance as mpf
from matplotlib import gridspec

def getStockByDate(stockData, date,code):
    if date < stockData.index[0][0]:
        return None
    try:
        return stockData.loc[date,code]
    except:
        return getStockByDate(stockData, date - datetime.timedelta(1), code)

def getValidDate(year, month, day, nextday = True):
    try:
        return pd.Timestamp(year, month, day)
    except:
        # print('getValidDate', year, month, day)
        if nextday:
            return getValidDate(year, month + 1, 1)
        else:
            return getValidDate(year, month, day - 1)
          
def beforeDate(calcDate, year = 0, month = 0, days = 0):
    if days > 1:
        return calcDate - datetime.timedelta(days)
    year = year + int(month / 12)
    month = month - int(month / 12) * 12
    if calcDate.month > month:
        result = getValidDate(calcDate.year - year, calcDate.month - month, calcDate.day)
    else:
        result = getValidDate(calcDate.year - year - 1, calcDate.month + 12 - month, calcDate.day)
    return result
  
def afterDate(calcDate, year = 0, month = 0, days = 0):
    if days > 0:
        return calcDate + datetime.timedelta(days)
    year = year + int(month / 12)
    month = month - int(month / 12) * 12
    if calcDate.month + month > 12:
        result = getValidDate(calcDate.year + year + 1, calcDate.month + month - 12, calcDate.day)
    else:
        result = getValidDate(calcDate.year + year, calcDate.month + month, calcDate.day)
    return result

def calcBAYMDateLst(calcDate, dstDate, year, month, before = True):
    out = []
    if before:
        value = eval('beforeDate')(calcDate, year, month)
        out.append(value)
        while value > dstDate:
            calcDate = value
            value = eval('beforeDate')(calcDate, year, month)
            out.append(value)
    else:
        value = eval('afterDate')(calcDate, year, month)
        out.append(value)
        while value < dstDate:
            calcDate = value
            value = eval('afterDate')(calcDate, year, month)
            out.append(value)
    return out

def calcBAYMDate4bak(calcDate, year, month, before = True):
    if before:
        value = eval('beforeDate')(calcDate, year, month)
    else:
        value = eval('afterDate')(calcDate, year, month)
    return value

def calcLoopDateByFunc(calcDate, funcName, loopDate):
    year = loopDate['y']
    month = loopDate['m']
    weeks = loopDate['w']
    days = loopDate['d']
    if days > 0:
        return eval(funcName)(calcDate, 0, 0, days)
    elif weeks > 0:
        return eval(funcName)(calcDate, 0, 0, weeks * 7)
    else:
        return eval(funcName)(calcDate, year, month)

def calcLoopLable(loopDate):
    year = loopDate['y']
    month = loopDate['m']
    weeks = loopDate['w']
    days = loopDate['d']
    if days > 0:
        return "D%02d" % days
    elif weeks > 0:
        return "W%02d" % weeks
    else:
        if year > 0 and month > 0:
            return "Y%02dM%02d" % (year, month)
        elif year > 0 and month == 0:
            return "Y%02d" % year
        else: ## month >0, year == 0
            return "M%02d" % month
        
def date2strLabel(dateIn):
    return str(dateIn)[2:10].replace("-","")

def calcBAYMDate(calcDate, loopDate, before = True):
    if before:
        return calcLoopDateByFunc(calcDate, 'beforeDate', loopDate)
    else:
        return calcLoopDateByFunc(calcDate, 'afterDate', loopDate)

def h_l_line(p_df, t=21,period=10000,fn=None):
    """
    根据给定的周期找出最高最低点的日期和数据，然后计算对应的斐波纳契数据
    :param fn: 高低线输出到文件,如果文件参数为None则不输出到文件
    :param p_df:股票交易数据
    :param t:数据周期
    :param period:数据长度
    :return:有效数据点，包括股票代码，日期，高低点周期交易天数、高低点周期自然天数
    """
    if p_df is None or len(p_df)<t:
        return None
    # 获取最新的period条数据
    # df1 = p_df.tail(period).reset_index(drop=True)
    df1 = p_df[['close','high','low','trade_date','ts_code']].copy()
    df1['cv'] = 0 #添加一列为后续保留值准备
    high = df1['high']
    low = df1['low']

    # 保留数据的df
    data = pd.DataFrame([])
    #获取首行为有效的数据点,加入到保留数据框中
    df1.loc[0,'cv'] = df1.iloc[0].high #最高价作为当前价
    first = df1.iloc[0:1]
    data = data.append(first)

    #取第一个日期的最高值作为当前值,开始为0，默认为上涨周期
    ci=0
    cv=df1.iloc[ci].high
    cup=True

    #循环处理每一个周期
    n=0
    lt = t
    while ci<df1.index.max():
        n=n+1
        # 取含当前日期的一个周期的最高和最低价以及索引值,如果出现下一个周期中当前点成为了这个周期的最高和最低点即当前点未变化则
        # 在前周期长度上扩展1个周期,一旦出现拐点则恢复周期。
        # 周期超高了数据长度则结束，当前点加入到数据有效点中。
        # 为什么不是从下一个点找周期，因为下一个点开始的周期则一定存在一个高低点，而这个高低点和当前点的高点或低点比较后一定会
        # 出现一个拐点，有时候不一定有拐点存在,所以要包含当前点
        ih = high[ci:ci+lt].idxmax()
        il = low[ci:ci+lt].idxmin()
        ihv = df1.iloc[ih].high
        ilv = df1.iloc[il].low
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
                # 如果上升周期中最高价有更新则仍然上涨持续，上涨价格有效，下跌的价格为噪声
                ci = ih
                cv = ihv
                cup = True
            else:
                # 未持续上涨，则下跌价格有效，出现了转折，此时上一个价格成为转折点价格,恢复计算周期
                df1.loc[ci,'cv'] = cv
                data = data.append(df1.iloc[ci:ci + 1])
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
                # 未持续下跌，此时转为上涨，上涨价格有效，此时上一个价格成为转折点价格,恢复计算周期
                df1.loc[ci, 'cv'] = cv
                data = data.append(df1.iloc[ci:ci + 1])
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
    df1.loc[ci, 'cv'] = cv
    data = data.append(df1.iloc[ci:ci + 1])
    if ci != df1.index.max():
        # 当前点不是最后一个点，则把最后一个点加入到数据点中
        df1.loc[df1.index.max(), 'cv'] = df1.iloc[df1.index.max()].close
        data = data.append(df1.tail(1))

    data = data.reset_index(drop=False)
    # 计算高低点转换的交易日数量即时间周期
    data['period'] = (data['index'] - data['index'].shift(1)).fillna(0)
    # 计算日期的差值,将字符串更改为日期
    trade_date = pd.to_datetime(data['trade_date'],format='%Y-%m-%d')
    days = trade_date - trade_date.shift(1)
    # 填充后转换为实际的天数数字
    days = (days.fillna(pd.Timedelta(0))).apply(lambda x:x.days)
    data['days'] = days
    # 对日期进行转换
    data['trade_date']=trade_date.apply(lambda x:x.strftime('%Y-%m-%d'))
    return data

def GannCheck(data, code, lastDay, posB0Day, preDate = None, delta = 0.1, gannBase = {'y':30,'m':0, 'w': 0, 'd':0}, gannList = []):
  #     data=data.reset_index()
#     data=data.set_index(['date'])
#     lstDay = data.index[-1]
    # code = data.index[-1][1] ##二维索引用
    # lastDay = data.index[-1][0] ##数据最大日期
    if preDate == None:
        preDate = posB0Day
    
    firstDay = data.index[0][0]
    ##基础点2
    posB1Day = calcBAYMDate(posB0Day, gannBase, False)
    posB2Day = calcBAYMDate(posB1Day, gannBase, False)
    # print("posB1Day", posB1Day)
    if firstDay > posB0Day or posB2Day < lastDay:
        # print('checkLoop1', firstDay, posB0Day, posB1Day)
        return GannCheck(data, code, lastDay, posB1Day, preDate, delta, gannBase, gannList)
    x0data = getStockByDate(data, posB0Day, code) #基础点1的数据
    xedata = getStockByDate(data, lastDay, code) #基础点1的数据 
    x1wight = 1 ##权重
    pxedata = 0
    pdelta = 0
    tj0=gannList[0] ##基础计算目标
    pos0Day = None
    pos1Day = None
    if posB1Day > lastDay:
        # print('checkLoop2', firstDay, posB0Day, posB1Day)
        result = GannSubCheck(data, code, lastDay, posB1Day, gannList, preDate, delta)
        if result != None:
            # print('checkLoop N', posB0Day, posB1Day, preDate, result['pos0'])
            result['posB0'] = posB0Day
            result['posB1'] = posB1Day
        return result
    else:
        # print('checkLoop2', posB0Day, posB1Day)
        result = GannSubCheck(data, code, lastDay, posB2Day, [gannBase] + gannList, preDate, delta)
        if result != None:
            # print('checkLoop N2', lastDay, posB0Day, posB1Day, preDate)
            result['posB0'] = posB0Day
            result['posB1'] = posB1Day
        return result

        # pos0Day = posB0Day
        # pos1Day = posB1Day
        # x0data = getStockByDate(data, pos0Day, code)
        # x1data=getStockByDate(data, pos1Day, code)
        # x1wight = x1data.close / x0data.close
        # pxedata = getStockByDate(data, calcBAYMDate(lastDay, gannBase['y'], gannBase['m'], True), code) * x1wight
        # pdelta = abs((pxedata.close - xedata.close ) / xedata.close )
        # return {'posB0':posB0Day, 'posB1':posB1Day, 'pos0':pos0Day, 'pos1':pos1Day, 'w':x1wight, 'pdata':pxedata, 'pd':pdelta}

def GannSubCheck(data, code, lastDay, posB1Day, gannList, preDate, delta = 0.1):
    # code = data.index[-1][1] ##二维索引用
    # lastDay = data.index[-1][0] ##数据最大日期
    xedata = getStockByDate(data, lastDay, code) #基础点1的数据
    firstDay = data.index[0][0]
    tj1=gannList[0]
    # print(tj1)
    # print('GannSubCheck0', lastDay, posB1Day, gannList)
    pos0Day = None
    pos1Day = None
    x1wight = 1 ##权重
    pxedata = 0
    pdelta = 0
    base2 = calcBAYMDate(posB1Day, tj1, True)
    base1 = calcBAYMDate(base2, tj1, True)
    if base1 < preDate:
        # print("calc date2:", base1)
        if len(gannList) == 1:
            return None
        return GannSubCheck(data, code, lastDay, posB1Day, gannList[1:], preDate, delta)
    
    if base2 < lastDay and base1 < lastDay and base1 > data.index[0][0]:
        pos0Day = base1
        pos1Day = base2
        x0data = getStockByDate(data, pos0Day, code)
        x1data = getStockByDate(data, pos1Day, code)
        
        # print(pos0Day, pos1Day, x0data, x1data)
        x1wight = x1data.close / x0data.close
        # x1:after 1-5
        # x11date = pos1Day + datetime.timedelta(1)
        # x11data = getStockByDate(data, x11date, code)
        # px11data = getStockByDate(data, calcBAYMDate(x11date, tj1, True), code) * x1wight
        # pdelta = abs((px11data.close - x11data.close ) / x11data.close )
        # print("calc delta", pos1Day, lastDay)
        delta1 = calcDelta(data, code, pos1Day, x1wight, tj1, 5, delta)
        delta2 = calcDelta(data, code, lastDay, x1wight, tj1, 5, delta)
        # last:        
        # pxedata = getStockByDate(data, calcBAYMDate(lastDay, tj1, True), code) * x1wight
        # pdelta = abs((pxedata.close - xedata.close ) / xedata.close )
        # last:after 1-5, before 1-5
        # if pdelta > delta:
        if delta1 == False or delta2 == False:
            if len(gannList) <= 1:
                # print('GannSubCheck None')
                return None
            else:
                # print('GannSubCheck1', gannList, pos0Day, pos1Day, pdelta)
                return GannSubCheck(data, code, lastDay, posB1Day, gannList[1:], preDate, delta)
        else:
            # print('GannSubCheck2', gannList, posB1Day, pdelta)
            # rule = "%s:%s:Y%02d:M%02d:%02d:%02d" % (str(pos0Day)[:10], str(pos1Day)[:10], tj1['y'], tj1['m'])
            # rule = "%s:%s:%s" % (str(pos0Day)[:10], str(pos1Day)[:10], calcLoopLable(tj1))
            rule = "%s:%s:%s" % (date2strLabel(pos0Day), date2strLabel(pos1Day), calcLoopLable(tj1))
            # calcLoopLable
            return {'pos0':pos0Day, 'pos1':pos1Day, 'w':x1wight, 'tj1':tj1, 'rule':rule}
    else:
        if base2 < firstDay:
            return None
        # print('GannSubCheck3', base2)
        return GannSubCheck(data, code, lastDay, base2, gannList, preDate, delta)

def calcPredict(data, t = 250):
    dataP = data.copy()
    # code = dataP.index.levels[1][0]
    # code = dataP.index[1][1]
    # dataP['ts_code'] = code
    dataP = dataP.reset_index()
    dataP['ts_code'] = dataP['code']
    dataP['trade_date'] = dataP['date']
    predict = []
    try:
        # dataP['trade_date'] = dataP.index.levels[0]
        # dataP=dataP.reset_index()
        hldata=h_l_line(dataP, t)
        for x in hldata.index:
            predict.append(hldata.iloc[x].trade_date)
    except Exception as e:
        print("calc predict error", code, e)
    return predict

def calcDelta(data, code, calcDate, weight, gannBase, nums, delta):
    for i in range(1, nums+1):
        vdate = calcDate + datetime.timedelta(i)
        vdata = getStockByDate(data, vdate, code)
        pvdata = getStockByDate(data, calcBAYMDate(vdate, gannBase, True), code) * weight
        pdelta = abs((pvdata.close - vdata.close ) / vdata.close )
        if pdelta > delta:
            return False
    return True
  
def getPctValue(dstValue, baseValue):
    if baseValue == None or baseValue == 0:
        return 0
    return (dstValue - baseValue) / baseValue * 100

def getColName(loopYear, preDate):
    col_name = "%s:%s" % (loopYear, preDate.replace('-',''))
    return col_name

def forcast(code, data, lastDay, beforeStep, afterStep, preDate, dataLastDate, loopYear = '30', delta = 0.1, plot = None):
    if preDate < str(data.index[0][0])[:10]:
        return None
    # print('forcast', preDate, str(data.index[0][0])[:10])
    col_name = getColName(loopYear, preDate) ## "%s:%s" % (loopYear, preDate.replace('-',''))
    year = int(preDate[:4])
    month = int(preDate[5:7])
    day = int(preDate[8:10])
    # outs=GannCheck(data, pd.Timestamp(1992,5,26), gannBase = {'y':30,'m':0}, gannList = [{'y':7,'m':6},{'y':2,'m':6},{'y':0,'m':7},{'y':0,'m':1}])
    # gannList = [{'y':7,'m':6},{'y':2,'m':6},{'y':0,'m':7},{'y':0,'m':1}]
    gannBase = {'y':int(loopYear),'m':0, 'w': 0,'d': 0}
    # gannBase = {'y':28,'m':0, 'w': 0,'d': 0}
    # gannBase = {'y':60,'m':0, 'w': 0,'d': 0}
    #年：季-月-周-日
    # gannList = []
    gannList7 = [{'y': 1, 'm': 9, 'w': 0,'d': 0}, {'y': 0, 'm': 7, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w': 7,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d': 7}] ##7循环
    # gannList7  = [{'y': 1, 'm': 9, 'w': 0,'d': 0}, {'y': 0, 'm': 7, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w': 7,'d': 0}] ##7循环
    gannList15 = [{'y': 3, 'm': 9, 'w': 0,'d': 0}, {'y': 1, 'm': 3, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':15,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':15}] ##28循环
    gannList30 = [{'y': 7, 'm': 6, 'w': 0,'d': 0}, {'y': 2, 'm': 6, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':30,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':30}] ##30循环
    gannList28 = [{'y': 7, 'm': 0, 'w': 0,'d': 0}, {'y': 2, 'm': 4, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':28,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':28}] ##28循环
    gannList60 = [{'y':15, 'm': 0, 'w': 0,'d': 0}, {'y': 5, 'm': 0, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':60,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':60}] ##60循环

    # gannList7 = [{'y': 1, 'm': 9, 'w': 0,'d': 0}, {'y': 0, 'm': 7, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w': 7,'d': 0}] ##7循环
    # gannList7  = [{'y': 1, 'm': 9, 'w': 0,'d': 0}, {'y': 0, 'm': 7, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w': 7,'d': 0}] ##7循环
    # gannList15 = [{'y': 3, 'm': 9, 'w': 0,'d': 0}, {'y': 1, 'm': 3, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':15,'d': 0}] ##28循环
    gannList30 = [{'y': 7, 'm': 6, 'w': 0,'d': 0}, {'y': 2, 'm': 6, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':30,'d': 0}] ##30循环
    gannList28 = [{'y': 7, 'm': 0, 'w': 0,'d': 0}, {'y': 2, 'm': 4, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':28,'d': 0}] ##28循环
    # gannList60 = [{'y':15, 'm': 0, 'w': 0,'d': 0}, {'y': 5, 'm': 0, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':60,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':60}] ##60循环

    gannList = {'7':gannList7, '30':gannList30, '28':gannList28, '60':gannList60, '15':gannList15}
    try:
        # print('forcast', preDate, str(data.index[0][0])[:10], gannBase, gannList[str(loopYear)])
        outs=GannCheck(data, code, lastDay, pd.Timestamp(year,month,day), delta = delta, gannBase = gannBase, gannList = gannList[str(loopYear)])
        # outs=GannCheck(data, code, lastDay, pd.Timestamp(year,month,day), delta = delta, gannBase = gannBase, gannList = gannList30)
        if outs == None:
            return None
    except Exception as e:
        print('forcast error', e)
        return None
    # outs
    # print('计算规则', outs['rule'])
    data.loc[:,col_name] = 0.0
    x1wight=outs['w']
    # print(x1wight)
    gannBase=outs['tj1']
    pos1Day = outs['pos1']  ##middle date
    # print(gannBase)
    # lastDay = data.index[-1][0]
    # lastDay
    # print(lastDay)
    # code='000001'
    firstDay = None
    baseValue = 0.0
    maxValue = 0.0
    minValue = 0.0
    for rday in range(-beforeStep, afterStep):
        ycday = lastDay + datetime.timedelta(rday)
        if firstDay == None:
            firstDay = ycday
        # print(ycday)
        if ycday <= pos1Day:    ##当前日期在可预测日期之前，取实际日期
            preN = getStockByDate(data, ycday, code)
        else:
            preN = getStockByDate(data, calcBAYMDate(ycday, gannBase, True), code) * x1wight
        # preD = afterDate(preN.name[0], year=0, month = 7)
        try:
            rclose = data.at[(ycday,code),'close']
            # print(ycday)
            rclose = getStockByDate(data, ycday, code).close
            diff = preN.close - rclose
        except Exception as e:
    #         print(preN.name[0])
            rclose = 0.0
            diff = 0
    #     print(str(preD)[:10], int(preN.close), rclose, int(diff))
        if rclose == 0 and ycday < dataLastDate:
    #         print(ycday)
            continue
        else:
            if ycday < dataLastDate and ycday.weekday() > 4:
                continue
            rclose = getStockByDate(data, ycday, code).close
    #     print(ycday.weekday())
        data.at[(ycday,code),col_name]  = preN.close
        data.at[(ycday,code),'close']  = rclose
        ## max Value        
        # if ycday == dataLastDate:
            # baseValue = preN.close
        #     maxValue = baseValue
        #     minValue = baseValue
        # if preN.close > maxValue:
        #     maxValue = preN.close
        # if preN.close < minValue:
        #     minValue = preN.close
        # data.at[]
    # data.tail(30)
    # maxValue = data.loc[(firstDay,code):][col_name].max()
    # minValue = data.loc[(firstDay,code):][col_name].min()
    # base1Value = data.loc[(firstDay,code)][col_name]
    base1Value = data.loc[(lastDay,code)][col_name]
    base2Value = data.loc[(dataLastDate,code)][col_name]
    xlabel = []
    for x in data.loc[(firstDay,code):].index:
        xlabel.append(str(x[0])[5:10])
    # data.iloc[-24:].close.plot()
    # data.iloc[-24:][col_name].plot()
    # plt.show()
    # if plot != None:
    #     plot.plot(xlabel, data.loc[(firstDay,code):][col_name], label="%s:%s" % (date2strLabel(preDate), outs['rule']))
    # print("calc-out", maxValue, minValue)
    # return (firstDay, xlabel,(maxValue - baseValue) / baseValue * 100, -(baseValue - minValue) / baseValue * 100)
    return (firstDay, xlabel, outs['rule'], base1Value, base2Value)

def doForcast(code, data, loopYear, lastDate, calcData, startDates, plot):
    (calcLastDate, dataLastDate) = lastDate
    (beforeStep, afterStep, delta) = calcData
    firstDate = None
    pre1MaxPct = {'max': -9999, 'min': 9999, 'col': ''}
    pre1MinPct = pre1MaxPct.copy() #{'max': -9999, 'min': 9999, 'col': ''}
    pre2MaxPct = pre1MaxPct.copy() #{'max': -9999, 'min': 9999, 'col': ''}
    pre2MinPct = pre1MaxPct.copy() #{'max': -9999, 'min': 9999, 'col': ''}
    for preDate in startDates:
        # print('step', preDate)
        col_name = getColName(loopYear, preDate)
        plotFlg = None
        temp = forcast(code, data, calcLastDate, beforeStep, afterStep, dataLastDate = dataLastDate, loopYear = loopYear, preDate = preDate, plot = plot, delta = delta)
        if firstDate == None and temp != None:
            (firstDate, xlabel, _, _, _) = temp
        if temp != None:
            (plotFlg, _, rule, base1Value, base2Value) = temp
            pre1MaxValue = data.loc[(calcLastDate,code):(dataLastDate, code)][col_name].max()
            pre1MinValue = data.loc[(calcLastDate,code):(dataLastDate, code)][col_name].min()
            pre2MaxValue = data.loc[(dataLastDate, code):][col_name].max()
            pre2MinValue = data.loc[(dataLastDate, code):][col_name].min()
            
            p1Max, p1Min = getPctValue(pre1MaxValue, base1Value), getPctValue(pre1MinValue, base1Value)
            if pre1MaxPct['max'] < p1Max:
               pre1MaxPct['max'] = p1Max
               pre1MaxPct['min'] = p1Min
               pre1MaxPct['col'] = col_name
            if pre1MinPct['min'] > p1Min:
               pre1MinPct['max'] = p1Max
               pre1MinPct['min'] = p1Min
               pre1MinPct['col'] = col_name
            p2Max, p2Min = getPctValue(pre2MaxValue, base2Value), getPctValue(pre2MinValue, base2Value)
            if pre2MaxPct['max'] < p2Max:
               pre2MaxPct['max'] = p2Max
               pre2MaxPct['min'] = p2Min
               pre2MaxPct['col'] = col_name
            if pre2MinPct['min'] > p2Min:
               pre2MinPct['max'] = p2Max
               pre2MinPct['min'] = p2Min
               pre2MinPct['col'] = col_name
        # else:
            # print("calc is null", preDate)
        if plot != None and plotFlg != None:
            # col_name = preDate.replace('-','')
            # print(data.tail())
            plot.plot(xlabel, data.loc[(firstDate,code):][col_name], label="%02d:%s:%s" % (loopYear, date2strLabel(preDate), rule))
        # if firstDate == None and temp != None:
        #     (firstDate, xlabel, maxPct, minPct) = temp
            # print(predata, maxPct)
        # if temp != None:
        #     maxValues.append(maxPct)
        #     minValues.append(minPct)
    if firstDate == None:
        xlabel = []
        firstDate1 = calcLastDate - datetime.timedelta(beforeStep)
        for x in data.loc[(firstDate1,code):].index:
            xlabel.append(str(x[0])[5:10])
        return (firstDate1, xlabel, pre1MaxPct, pre1MaxPct, pre1MaxPct, pre1MaxPct, 0, 0)
    # rclose = data.loc[(firstDate,code)].close
    # rmaxValue = data.loc[(firstDate,code):]['close'].max()
    # rminValue = data.loc[(firstDate,code):]['close'].min()
    
    # pre1MaxValue = data.loc[(firstDate,code):(dataLastDate, code)][col_name].max()
    # pre1MinValue = data.loc[(firstDate,code):(dataLastDate, code)][col_name].min()

    rclose = data.loc[(calcLastDate,code)].close
    rmaxValue = data.loc[(calcLastDate,code):]['close'].max()
    rminValue = data.loc[(calcLastDate,code):]['close'].min()
    
    return (firstDate, xlabel
            , pre1MaxPct, pre1MinPct
            , pre2MaxPct, pre2MinPct
            , getPctValue(rmaxValue, rclose), getPctValue(rminValue, rclose))
    # return (firstDate, xlabel, max(maxValues), min(minValues))

def doForcast4LoopYear(loopYear, code, data, lastDate, calcData, startDates, plot):
    firstDay = None
    xlabel = []
    predictValue = ""
    dictData = {'code':[], 'loop': [], 'yc1max': [], 'yc1min':[], 'rmax':[], 'rmin':[], 'yc2max': [], 'yc2min':[] }
    for loopYear1 in [7, 28, 30, 60]:
    # for loopYear1 in [28, 30]:
        if loopYear == 99 or loopYear == loopYear1 or (loopYear == 88 and (loopYear1 == 28 or loopYear1 == 30)):
            (firstDay, xlabel, yc1Max, yc1Min, yc2Max, yc2Min, rMax, rMin) = doForcast(code, data, loopYear1, lastDate, calcData, startDates = startDates, plot = plot)
            if yc1Max['max'] <= -9999:
                continue
            dictData['code'].append(code)
            dictData['loop'].append(loopYear1)
            dictData['yc1max'].append(yc1Max['max'])
            dictData['yc1min'].append(yc1Min['min'])
            dictData['yc2max'].append(yc2Max['max'])
            dictData['yc2min'].append(yc2Min['min'])
            dictData['rmax'].append(rMax)
            dictData['rmin'].append(rMin)
            predictValue1 = "loop:%02d:yc1Maxmin:%4.1f,%4.1f==rMaxmin:%4.1f,%4.1f==>yc2Maxmin:%4.1f,%4.1f" % (loopYear1, yc1Max['max'], yc1Min['min'], rMax, rMin, yc2Max['max'], yc2Min['min'])
            # dictData = {'code':code, }
            # print('dict data', dictData)
            # print("predict value:", predictValue1)
            if predictValue == "":
                predictValue = predictValue1
            else:
                predictValue = predictValue + "\n" + predictValue1
    return (firstDay, xlabel, dictData, predictValue)
