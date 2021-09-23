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
from gannCheck import *

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
        data=m.get_index_day(code, st_start = '1990-01-01')
    else:
        data=m.get_stock_day(code, st_start = '1990-01-01')
    
    if len(predict) == 0:
        predict = calcPredict(data, t = 240)
        if len(predict) > 2:
            predict = predict[:-1]
    # print(predict)
    if predict == None or len(predict) < 1:
        print("predict data is NULL")
        sys.exit()
        # return 0
    if baseDay == None:
        lastDay = data.index[-1][0] # - datetime.timedelta(baseDay)
    else:
        lastDay = pd.to_datetime(baseDay)
    dataLastDate = data.index[-1][0]
    # print("code=%s, idx=%s, beforeStep=%d, afterStep = %d, delta=%5.2f" % (code, idx, beforeStep, afterStep, delta))
    # print("loopYear = %d, lastDay=%s, dataLastDate=%s, predict=%s" % (loopYear, str(lastDay)[:10], str(dataLastDate)[:10], predict))

    # print(data.head())
    # data=m.get_index_day(code, st_start = '1990-01-01')
    fig = plt.figure(dpi=100,figsize=(16,9))
    # plt.xlabel('日期')
    # plt.ylabel('价格')

    # fig = plt.figure(figsize=(960/72,360/72))
    # fig, ax = plt.subplots()
    stockPlot = fig.add_subplot(1,1,1)
    text = stockPlot.text(0.5, 0.5, 'event', ha='center', va='center', fontdict={'size': 20})
    # text0 = plt.text(len_y-1,y[-1],str(y[-1]),fontsize = 10)
    lastDate = (lastDay, dataLastDate)
    calcData = (beforeStep, afterStep, delta)

    (firstDay, xlabel, dictData, predictValue) = doForcast4LoopYear(loopYear, code, data, lastDate, calcData, startDates = predict, plot = stockPlot)
    plt.title("%s == %s" % (code, predictValue))
    print(pd.DataFrame.from_dict(dictData))
    
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
    
    # data.loc[(firstDay,code):].to_csv('gann-ok1-%s-%s.csv' % (loopYear, code))
    # print(data.loc[(firstDay,code):])
    # print()
    plt.axvline(x=str(lastDay)[5:10])
    plt.axvline(x=str(dataLastDate)[5:10])
    plt.legend(loc=1)
    # plt.save
    plt.show()
    # plt.save("gann-%s.png" % code)
    #plt.close()
    # print("predict value:", predictValue)
    # print(xlabel[:10])
    