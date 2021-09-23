import os
import struct
import pandas as pd
import numpy as np
import time, datetime
import sys, getopt
# import multiprocessing
# import talib as tdx
import QUANTAXIS as QA

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

def GannCheck(data, code, lastDay, posB0Day, delta = 0.1, gannBase = {'y':30,'m':0, 'w': 0, 'd':0}, gannList = []):
  #     data=data.reset_index()
#     data=data.set_index(['date'])
#     lstDay = data.index[-1]
    # code = data.index[-1][1] ##二维索引用
    # lastDay = data.index[-1][0] ##数据最大日期
    firstDay = data.index[0][0]
    x0data = getStockByDate(data, posB0Day, code) #基础点1的数据
    xedata = getStockByDate(data, lastDay, code) #基础点1的数据 
    x1wight = 1 ##权重
    pxedata = 0
    pdelta = 0
    tj0=gannList[0] ##基础计算目标
    ##基础点2
    posB1Day = calcBAYMDate(posB0Day, gannBase, False)
    # print("posB1Day", posB1Day)
    if firstDay > posB0Day:
        # print('checkLoop1', firstDay, posB0Day, posB1Day)
        return GannCheck(data, code, lastDay, posB1Day, delta, gannBase, gannList)
    pos0Day = None
    pos1Day = None
    if posB1Day > lastDay:
        # print('checkLoop2', firstDay, posB0Day, posB1Day)
        result = GannSubCheck(data, code, lastDay, posB1Day, gannList, delta)
        if result != None:
            result['posB0'] = posB0Day
            result['posB1'] = posB1Day
        return result
    else:
        # print('checkLoop2', posB1Day)
        result = GannSubCheck(data, code, lastDay, posB0Day, [gannBase])
        if result != None:
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

def GannSubCheck(data, code, lastDay, posB1Day, gannList, delta = 0.1):
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
        delta1 = calcDelta(data, pos1Day, x1wight, tj1, 5, delta)
        delta2 = calcDelta(data, lastDay, x1wight, tj1, 5, delta)
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
                return GannSubCheck(data, code, lastDay, posB1Day, gannList[1:], delta)
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
        return GannSubCheck(data, code, lastDay, base2, gannList, delta)

def calcDelta(data, calcDate, weight, gannBase, nums, delta):
    for i in range(1, nums+1):
        vdate = calcDate + datetime.timedelta(i)
        vdata = getStockByDate(data, vdate, code)
        pvdata = getStockByDate(data, calcBAYMDate(vdate, gannBase, True), code) * weight
        pdelta = abs((pvdata.close - vdata.close ) / vdata.close )
        if pdelta > delta:
            return False
    return True

def forcast(code, data, lastDay, beforeStep, afterStep, predate, dataLastDate, loopYear = '30', delta = 0.1, plot = None):
    if predate < str(data.index[0][0])[:10]:
        return None
    # print('forcast', predate, str(data.index[0][0])[:10])
    col_name = predate.replace('-','')
    year = int(predate[:4])
    month = int(predate[5:7])
    day = int(predate[8:10])
    # outs=GannCheck(data, pd.Timestamp(1992,5,26), gannBase = {'y':30,'m':0}, gannList = [{'y':7,'m':6},{'y':2,'m':6},{'y':0,'m':7},{'y':0,'m':1}])
    # gannList = [{'y':7,'m':6},{'y':2,'m':6},{'y':0,'m':7},{'y':0,'m':1}]
    gannBase = {'y':int(loopYear),'m':0, 'w': 0,'d': 0}
    # gannBase = {'y':28,'m':0, 'w': 0,'d': 0}
    # gannBase = {'y':60,'m':0, 'w': 0,'d': 0}
    #年：季-月-周-日
    # gannList = []
    gannList7  = [{'y': 1, 'm': 9, 'w': 0,'d': 0}, {'y': 0, 'm': 7, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w': 7,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d': 7}] ##7循环
    # gannList7  = [{'y': 1, 'm': 9, 'w': 0,'d': 0}, {'y': 0, 'm': 7, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w': 7,'d': 0}] ##7循环
    gannList15 = [{'y': 3, 'm': 9, 'w': 0,'d': 0}, {'y': 1, 'm': 3, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':15,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':15}] ##28循环
    gannList30 = [{'y': 7, 'm': 6, 'w': 0,'d': 0}, {'y': 2, 'm': 6, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':30,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':30}] ##30循环
    gannList28 = [{'y': 7, 'm': 0, 'w': 0,'d': 0}, {'y': 2, 'm': 4, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':28,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':28}] ##28循环
    gannList60 = [{'y':15, 'm': 0, 'w': 0,'d': 0}, {'y': 5, 'm': 0, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':60,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':60}] ##60循环
    gannList = {'7':gannList7, '30':gannList30, '28':gannList28, '60':gannList60, '15':gannList15}
    try:
        # print('forcast', predate, str(data.index[0][0])[:10], gannBase, gannList[str(loopYear)])
        outs=GannCheck(data, code, lastDay, pd.Timestamp(year,month,day), delta = delta, gannBase = gannBase, gannList = gannList[str(loopYear)])
        # outs=GannCheck(data, code, lastDay, pd.Timestamp(year,month,day), delta = delta, gannBase = gannBase, gannList = gannList30)
        if outs == None:
            return None
    except Exception as e:
        print('forcast error', e)
        return None
    # outs
    # print('计算规则', outs['rule'])
    data[col_name] = 0.0
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
        if ycday <= pos1Day or ycday < lastDay:
            continue
        if firstDay == None:
            firstDay = ycday
        # print(ycday)
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
        if ycday == dataLastDate:
            baseValue = preN.close
    maxValue = data.loc[(firstDay,code):][col_name].max()
    minValue = data.loc[(firstDay,code):][col_name].min()
    xlabel = []
    for x in data.loc[(firstDay,code):].index:
        xlabel.append(str(x[0])[5:10])
    # data.iloc[-24:].close.plot()
    # data.iloc[-24:][col_name].plot()
    # plt.show()
    # if plot != None:
        # plot.plot(xlabel, data.loc[(firstDay,code):][col_name], label="%s:%s" % (date2strLabel(predate), outs['rule']))
    # print("calc-out", maxValue, minValue)
    return (firstDay, xlabel, outs['rule'], maxValue, minValue, baseValue)

def scroll(event):
    axtemp=event.inaxes
    x_min, x_max = axtemp.get_xlim()
    fanwei_x = (x_max - x_min) / 10
    print('scroll', fanwei_x, x_min, x_max)
    if event.button == 'up':
        axtemp.set(xlim=(x_min + fanwei_x, x_max - fanwei_x))
    elif event.button == 'down':
        axtemp.set(xlim=(x_min - fanwei_x, x_max + fanwei_x))
    fig.canvas.draw_idle() 
#这个函数实时更新图片的显示内容
def motion(event):
    try:
        temp = y[int(np.round(event.xdata))]
        print('motion', temp)
        # for i in range(len_y):
        #     _y[i] = temp
        # line_x.set_ydata(_y)
        # line_y.set_xdata(event.xdata)
        # ######
        # text0.set_position((event.xdata, temp))
        # text0.set_text(str(temp))
            
        fig.canvas.draw_idle() # 绘图动作实时反映在图像上
    except:
        pass
def call_back(event):
    info = 'name:{}\n button:{}\n x,y:{},{}\n xdata,ydata:{}{}'.format(event.name, event.button,event.x, event.y,event.xdata, event.ydata)
    text.set_text(info)
    fig.canvas.draw_idle()

def calcPredict(data, t = 250):
    dataP=data.copy()
    dataP['trade_date'] = dataP.index.levels[0]
    dataP['ts_code'] = dataP.index.levels[1][0]
    dataP=dataP.reset_index()
    hldata=h_l_line(dataP, t)
    predict = []
    for x in hldata.index:
        predict.append(hldata.iloc[x].trade_date)

    return predict

def doForcast(code, data, loopYear, lastDate, calcData, startDates, plot):
    (calcLastDate, dataLastDate) = lastDate
    (beforeStep, afterStep, delta) = calcData
    xlabel  = []
    maxValues = []
    minValues = []
    firstDate = None
    baseValue = 0.0
    for preDate in startDates:
        plotFlg = None
        # print('step', predata)
        temp = forcast(code, data, calcLastDate, beforeStep, afterStep, dataLastDate = dataLastDate, loopYear = loopYear, predate = preDate, delta = delta)
        # if firstDate == None and temp != None:
        #     (firstDate, xlabel, maxPct, minPct) = temp
        #     # print(predata, maxPct)
        # if temp != None:
        #     maxValues.append(maxPct)
        #     minValues.append(minPct)
        if firstDate == None and temp != None:
            (firstDate, _, _, _, _, _) = temp
        if temp != None:
            (plotFlg, xlabel, rule, maxValue, minValue, baseValue) = temp
            maxValues.append(maxValue)
            minValues.append(minValue)

        if plot != None and plotFlg != None:
            col_name = preDate.replace('-','')
            # print(data.tail())
            plot.plot(xlabel, data.loc[(firstDate,code):][col_name], label="%s:%s" % (date2strLabel(preDate), rule))
        
    if firstDate == None:
        return (None, [], 0, 0, 0, 0)

    # if plot != None and firstDate != None:
    #     plot.plot(xlabel, data.loc[(firstDate,code):]['close'], label="%s:REAL" % code, linewidth = '2', color = '#00FF00')
    rclose = data.loc[(firstDate,code)].close
    rmaxValue = data.loc[(firstDate,code):]['close'].max()
    rminValue = data.loc[(firstDate,code):]['close'].min()

    return (firstDate, xlabel, getPctValue(max(maxValues), baseValue), getPctValue(min(minValues), baseValue), getPctValue(rmaxValue, rclose), getPctValue(rminValue, rclose))

def getPctValue(dstValue, baseValue):
    if baseValue == None or baseValue == 0:
        return 0
    return (dstValue - baseValue) / baseValue * 100

def doForcastFunc(mongoM, code, idx, key, baseDate, predict, plot):
    # mongoM = MongoIo()
    if idx == '1':
        dataM=mongoM.get_index_day(code, st_start = '1990-01-01')
    else:
        data=datam.query("code=='%s'" % code)
        dataM=mongoM.get_stock_day(code, st_start = '1990-01-01')
    if len(predict) == 0:
        predict = calcPredict(dataM, t = 240)
        if len(predict) > 2:
            predict = predict[:-1]
    if predict == None or len(predict) < 1:
        print("predict data is NULL")
        return None
    
    if baseDate == None:
        lastDate = dataM.index[-1][0] # - datetime.timedelta(baseDay)
    else:
        lastDate = pd.to_datetime(baseDate)

    dataLastDate = dataM.index[-1][0]
    
    lastDateG = (lastDate, dataLastDate)
    calcData = (beforeStep, afterStep, delta)
    OK_KEY = 'OK'
    ERR_KEY = 'ERROR'
    betaPct = {OK_KEY: 0, ERR_KEY: 0}
    for loopYear in [7, 28, 30, 60]:
        data = dataM.copy()
        (firstDay, xlabel, maxValue, minValue, rmax, rmin) = doForcast(code, data, loopYear, lastDateG, calcData, startDates = predict, plot = plot)
        data.loc[(firstDay,code):].to_csv('gann-%s-%s.csv' % (loopYear, code))
        # print("loopYear=%02d, maxValue=%5.1f, minValue=%5.1f, rmax=%5.1f, rmin=%5.1f" %(loopYear, maxValue, minValue, rmax, rmin))
        if rmax > 0:
            # print(rmax, abs(getPctValue(maxValue, rmax)), delta*100)
            if abs(getPctValue(maxValue, rmax)) < delta * 100 or maxValue > rmax * 1.1:
                betaPct[OK_KEY] = betaPct[OK_KEY] + 1
            else:
                betaPct[ERR_KEY] = betaPct[ERR_KEY] + 1
    
    return (data, firstDay, lastDate, dataLastDate, xlabel, betaPct)
   
def do_get_data_mp(key, codelist, st_start, st_end):
    mongo_mp = MongoIo()
    # start_t = datetime.datetime.now()
    # print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
    databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end)
    # end_t = datetime.datetime.now()
    # print(end_t, 'get_data do_get_data_mp spent:{}'.format((end_t - start_t)))

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
    # loopYear = int(argv[5])
    # baseDay = int(argv[5])
    baseDay = None
    if len(argv) > 5:
        baseDay = argv[5]
    predict = []
    if len(argv) > 6:
        predict=argv[6:]
    # print(delta, baseDay, predict)

    # m=MongoIo()
    # if idx == '1':
    #     dataM=m.get_index_day(code, st_start = '1990-01-01')
    # else:
    #     dataM=m.get_stock_day(code, st_start = '1990-01-01')
    
    # if len(predict) == 0:
    #     predict = calcPredict(dataM, t = 240)
    #     if len(predict) > 2:
    #         predict = predict[:-1]
    # print(predict)
    # if predict == None or len(predict) < 1:
    #     print("predict data is NULL")
    #     sys.exit()
    #     # return 0

    # if baseDay == None:
    #     lastDay = dataM.index[-1][0] # - datetime.timedelta(baseDay)
    # else:
    #     lastDay = pd.to_datetime(baseDay)
    # dataLastDate = dataM.index[-1][0]
    print("params code=%s, idx=%s, beforeStep=%d, afterStep = %d, delta=%5.2f" % (code, idx, beforeStep, afterStep, delta))
    # print("params lastDay=%s, dataLastDate=%s, predict=%s" % (str(lastDay)[:10], str(dataLastDate)[:10], predict[-1]))

    # print(data.head())
    # data=m.get_index_day(code, st_start = '1990-01-01')
    fig = plt.figure(dpi=100,figsize=(16,9))
    plt.title("%s-%d" % (code, 999))
    # plt.xlabel('日期')
    # plt.ylabel('价格')

    # fig = plt.figure(figsize=(960/72,360/72))
    # fig, ax = plt.subplots()
    stockPlot = fig.add_subplot(1,1,1)
    text = stockPlot.text(0.5, 0.5, 'event', ha='center', va='center', fontdict={'size': 20})
    # text0 = plt.text(len_y-1,y[-1],str(y[-1]),fontsize = 10)
    # lastDate = (lastDay, dataLastDate)
    # calcData = (beforeStep, afterStep, delta)
    # OK_KEY = 'OK'
    # ERR_KEY = 'ERROR'
    # betaPct = {OK_KEY: 0, ERR_KEY: 0}
    # for loopYear in [7, 28, 30, 60]:
    #     data = dataM.copy()
    #     (firstDay, xlabel, maxValue, minValue, rmax, rmin) = doForcast(code, data,  loopYear, lastDate, calcData, startDates = predict, plot = stockPlot)
    #     data.loc[(firstDay,code):].to_csv('gann-%s-%s.csv' % (loopYear, code))
    #     # print("loopYear=%02d, maxValue=%5.1f, minValue=%5.1f, rmax=%5.1f, rmin=%5.1f" %(loopYear, maxValue, minValue, rmax, rmin))
    #     if rmax > 0:
    #         # print(rmax, abs(getPctValue(maxValue, rmax)), delta*100)
    #         if abs(getPctValue(maxValue, rmax)) < delta * 100 or maxValue > rmax * 1.1:
    #             betaPct[OK_KEY] = betaPct[OK_KEY] + 1
    #         else:
    #             betaPct[ERR_KEY] = betaPct[ERR_KEY] + 1
        # betaPct[str(loopYear)] = 
        # input()
    # =MongoIo()
    databuf_mongo = Manager().dict()
    
    pool_size = cpu_count()
    codelist=QA.QA_fetch_stock_block_adv().code
    subcode_len = int(len(codelist) / pool_size)
    # executor = ProcessPoolExecutor(max_workers=pool_size * 2)
    code_dict = {}
    pool = Pool(cpu_count())
    for i in range(pool_size):
        if i < pool_size - 1:
            code_dict[str(i)] = codelist[i* subcode_len : (i+1) * subcode_len]
        else:
            code_dict[str(i)] = codelist[i * subcode_len:]
        pool.apply_async(do_get_data_mp, args=(i, code_dict[str(i)]))
    
    pool.close()
    pool.join()
    end_t = datetime.datetime.now()
    print(end_t, 'read db spent:{}'.format((end_t - start_t)))
    
    executor_func = ProcessPoolExecutor(max_workers=cpu_count() * 2)
    task_list = []
    # pool = Pool(cpu_count())
    for key in range(pool_size):
        # tdx_func(databuf_mongo[key])
        task_list.append(executor_func.submit(tdx_func, databuf_mongo[key], func_name, st_start))

    for task in as_completed(task_list):
        if len(dataR) == 0:
            dataR = task.result()
        else:
            dataR = dataR.append(task.result())


    result = doForcastFunc(code, idx, baseDay, predict, stockPlot)
    if result == None:
        sys.exit()

    (data, firstDay, lastDay, dataLastDate, xlabel, betaPct) = result
    print(betaPct)
    # firstDay = None
    # xlabel = None
    # maxValues = []
    # minValues = []
    # baseValue = 0.0
    # for predata in predict:
    #     # print('step', predata)
    #     temp = forcast(code, lastDay, beforeStep, afterStep, dataLastDate = dataLastDate, loopYear = loopYear, predate = predata, plot = stockPlot, delta = delta)
    #     if firstDay == None and temp != None:
    #         (firstDay, _, _, _, _) = temp
    #     if temp != None:
    #         (_, xlabel, maxValue, minValue, baseValue) = temp
    #         maxValues.append(maxValue)
    #         minValues.append(minValue)
            # print(predata, maxPct)
    # forcast(code, col_name = '19970512', predate = '1997-05-12')
    # print(firstDay, xlabel)
    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))
    
    if firstDay != None:
        stockPlot.plot(xlabel, data.loc[(firstDay,code):]['close'], label="%s:REAL" % code, linewidth = '2', color = '#00FF00')

    # # 设置刻度显示的值,显示日期，第一个数组为位置，第二个数组为显示的标签
    # plt.xticks(p_df['index'], p_df['trade_date'], rotation=90)

    for label in stockPlot.xaxis.get_ticklabels():
        label.set_rotation(90)
    # print(data.tail(30))
    # fig.canvas.mpl_connect('scroll_event', scroll)
    # fig.canvas.mpl_connect('motion_notify_event', motion)
    fig.canvas.mpl_connect('button_press_event', call_back)
    # data.loc[(firstDay,code):].to_csv('gann-%s-%s.csv' % (loopYear, code))
    # print(data.loc[(firstDay,code):])
    # print()
    plt.axvline(x=str(lastDay)[5:10])
    plt.axvline(x=str(dataLastDate)[5:10])
    plt.legend(loc=1)
    # plt.save
    # plt.show()
    # plt.save("gann-%s.png" % code)
    #plt.close()
    # print("maxValues", (max(maxValues) - baseValue) / baseValue * 100, "minValues", (min(minValues) - baseValue) / baseValue * 100)
    # print("maxValues", maxValue, "minValues", minValue)
