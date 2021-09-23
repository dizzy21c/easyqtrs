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
from gannCheck import calcPredict, getStockByDate, calcBAYMDate, date2strLabel, calcLoopLable

from gannCheck import calcPredict, getStockByDate, calcBAYMDate, date2strLabel, calcLoopLable, GannCheck

def GannCheck_1d(data, code, lastDay, posB0Day, delta = 0.1, gannBase = {'y':30,'m':0, 'w': 0, 'd':0}, gannList = []):
  #     data=dataIn.reset_index()
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
        pxedata = getStockByDate(data, calcBAYMDate(lastDay, tj1, True), code) * x1wight
        pdelta = abs((pxedata.close - xedata.close ) / xedata.close )
        if pdelta > delta:
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
    gannList7 = [{'y': 1, 'm': 9, 'w': 0,'d': 0}, {'y': 0, 'm': 7, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w': 7,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d': 7}] ##7循环
    gannList30 = [{'y': 7, 'm': 6, 'w': 0,'d': 0}, {'y': 2, 'm': 6, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':30,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':30}] ##30循环
    gannList28 = [{'y': 7, 'm': 0, 'w': 0,'d': 0}, {'y': 2, 'm': 4, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':28,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':28}] ##28循环
    gannList60 = [{'y':15, 'm': 0, 'w': 0,'d': 0}, {'y': 5, 'm': 0, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':60,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':60}] ##60循环

    gannList7 = [{'y': 1, 'm': 9, 'w': 0,'d': 0}, {'y': 0, 'm': 7, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w': 7,'d': 0}] ##7循环
    gannList30 = [{'y': 7, 'm': 6, 'w': 0,'d': 0}, {'y': 2, 'm': 6, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':30,'d': 0}] ##30循环
    gannList28 = [{'y': 7, 'm': 0, 'w': 0,'d': 0}, {'y': 2, 'm': 4, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':28,'d': 0}] ##28循环
    gannList60 = [{'y':15, 'm': 0, 'w': 0,'d': 0}, {'y': 5, 'm': 0, 'w': 0,'d': 0}, {'y': 0, 'm': 0, 'w':60,'d': 0}, {'y': 0, 'm': 0, 'w': 0,'d':60}] ##60循环

    gannList = {'7':gannList7, '30':gannList30, '28':gannList28, '60':gannList60}
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
        if ycday == dataLastDate:
            baseValue = preN.close
            maxValue = baseValue
            minValue = baseValue
        if preN.close > maxValue:
            maxValue = preN.close
        if preN.close < minValue:
            minValue = preN.close
        # data.at[]
    # data.tail(30)
    xlabel = []
    for x in data.loc[(firstDay,code):].index:
        xlabel.append(str(x[0])[5:10])
    # data.iloc[-24:].close.plot()
    # data.iloc[-24:][col_name].plot()
    # plt.show()
    if plot != None:
        plot.plot(xlabel, data.loc[(firstDay,code):][col_name], label="%s:%s" % (date2strLabel(predate), outs['rule']))
    # print("calc-out", maxValue, minValue)
    return (firstDay, xlabel, (maxValue - baseValue) / baseValue * 100, -(baseValue - minValue) / baseValue * 100)

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

def doForcast(code, loopYear, lastDate, calcData, startDates, plot):
    (calcLastDate, dataLastDate) = lastDate
    (beforeStep, afterStep, delta) = calcData
    
    maxValues = [0]
    minValues = [0]
    firstDate = None
    for preDate in startDates:
        # print('step', predata)
        temp = forcast(code, calcLastDate, beforeStep, afterStep, dataLastDate = dataLastDate, loopYear = loopYear, predate = preDate, plot = plot, delta = delta)
        if firstDate == None and temp != None:
            (firstDate, xlabel, maxPct, minPct) = temp
            # print(predata, maxPct)
        if temp != None:
            maxValues.append(maxPct)
            minValues.append(minPct)
    if firstDate == None:
        return None
    return (firstDate, xlabel, max(maxValues), min(minValues))


if __name__ == "__main__":
    # print("code idx:0,1 predate col1 col2 co")
    print(sys.argv[1:])
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

    m=MongoIo()
    if idx == '1':
        dataIn=m.get_index_day(code, st_start = '1990-01-01')
    else:
        dataIn=m.get_stock_day(code, st_start = '1990-01-01')
    
    if len(predict) == 0:
        predict = calcPredict(dataIn, t = 240)
        if len(predict) > 2:
            predict = predict[:-1]
    print(predict)
    if predict == None or len(predict) < 1:
        print("predict data is NULL")
        sys.exit()
        # return 0
    if baseDay == None:
        lastDay = dataIn.index[-1][0] # - datetime.timedelta(baseDay)
    else:
        lastDay = pd.to_datetime(baseDay)
    dataLastDate = dataIn.index[-1][0]
    # print("code=%s, idx=%s, beforeStep=%d, afterStep = %d, delta=%5.2f" % (code, idx, beforeStep, afterStep, delta))
    print("loopYear = %d, lastDay=%s, dataLastDate=%s, predict=%s" % (loopYear, str(lastDay)[:10], str(dataLastDate)[:10], predict))

    # print(data.head())
    # data=m.get_index_day(code, st_start = '1990-01-01')
    fig = plt.figure(dpi=100,figsize=(16,9))
    plt.title("%s-%d" % (code, loopYear))
    # plt.xlabel('日期')
    # plt.ylabel('价格')

    # fig = plt.figure(figsize=(960/72,360/72))
    # fig, ax = plt.subplots()
    stockPlot = fig.add_subplot(1,1,1)
    text = stockPlot.text(0.5, 0.5, 'event', ha='center', va='center', fontdict={'size': 20})
    # text0 = plt.text(len_y-1,y[-1],str(y[-1]),fontsize = 10)
    lastDate = (lastDay, dataLastDate)
    calcData = (beforeStep, afterStep, delta)
    # doForcast(code, loopYear, lastDate, calcData, startDates = predict, plot = stockPlot)
    firstDay = None
    xlabel = None
    maxValues = []
    minValues = []
    for predata in predict:
        # print('step', predata)
        temp = forcast(code, dataIn, lastDay, beforeStep, afterStep, dataLastDate = dataLastDate, loopYear = loopYear, predate = predata, plot = stockPlot, delta = delta)
        if firstDay == None and temp != None:
            (firstDay, xlabel, maxPct, minPct) = temp
            # print(predata, maxPct)
        if temp != None:
            maxValues.append(maxPct)
            minValues.append(minPct)
        else:
            print('calc is null', predata)
    # forcast(code, col_name = '19970512', predate = '1997-05-12')
    
    if firstDay != None:
        stockPlot.plot(xlabel, dataIn.loc[(firstDay,code):]['close'], label="%s:REAL" % code, linewidth = '2', color = '#00FF00')

    # # 设置刻度显示的值,显示日期，第一个数组为位置，第二个数组为显示的标签
    # plt.xticks(p_df['index'], p_df['trade_date'], rotation=90)

    for label in stockPlot.xaxis.get_ticklabels():
        label.set_rotation(90)
    # print(data.tail(30))
    # fig.canvas.mpl_connect('scroll_event', scroll)
    # fig.canvas.mpl_connect('motion_notify_event', motion)
    fig.canvas.mpl_connect('button_press_event', call_back)
    
    dataIn.loc[(firstDay,code):].to_csv('gann-%s-%s.csv' % (loopYear, code))
    # print(data.loc[(firstDay,code):])
    # print()
    plt.axvline(x=str(lastDay)[5:10])
    plt.axvline(x=str(dataLastDate)[5:10])
    plt.legend(loc=1)
    # plt.save
    plt.show()
    # plt.save("gann-%s.png" % code)
    #plt.close()
    print("maxValues", max(maxValues), "minValues", min(minValues))
    print(xlabel[:10])
