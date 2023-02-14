import os
import copy
import struct
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import time
import sys
import math
import matplotlib.pyplot as plt

BASEM = 30.42778
BASEM = 30.41667
BASEM = 30.4375

def getStockByDate(stockData, date,code):
    if date < stockData.index[0][0]:
        return None
    try:
        return stockData.loc[date,code]
    except:
        return getStockByDate(stockData, date - timedelta(1), code)

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
        return calcDate - timedelta(days)
    year = year + int(month / 12)
    month = month - int(month / 12) * 12
    if calcDate.month > month:
        result = getValidDate(calcDate.year - year, calcDate.month - month, calcDate.day)
    else:
        result = getValidDate(calcDate.year - year - 1, calcDate.month + 12 - month, calcDate.day)
    return result
  
def afterDate(calcDate, year = 0, month = 0, days = 0):
    if days > 0:
        return calcDate + timedelta(days)
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

def calcBAYMDate(calcDate, loopDate, before = True):
    if before:
        return calcLoopDateByFunc(calcDate, 'beforeDate', loopDate)
    else:
        return calcLoopDateByFunc(calcDate, 'afterDate', loopDate)

def readTdxLdayFile(fname="/home/zjx/qa/udf/readtdx/data/sh000001.day"):
  dataSet=[]
  with open(fname,'rb') as fl:
    buffer=fl.read() #读取数据到缓存
    size=len(buffer) 
    rowSize=32 #通信达day数据，每32个字节一组数据
    code=os.path.basename(fname).replace('.day','')
    for i in range(0,size,rowSize): #步长为32遍历buffer
      row=list( struct.unpack('IIIIIfII',buffer[i:i+rowSize]) )
      row[1]=row[1]/100
      row[2]=row[2]/100
      row[3]=row[3]/100
      row[4]=row[4]/100
      row.pop() #移除最后无意义字段
      row.insert(0,code)
      dataSet.append(row) 
  return dataSet

#补齐数据列表
def analysis(data: list):
    if len(data) == 0:
        return [], []
    data_with_empty = [] #[columns]
    data_with_complete = [] #[columns]
    pre_row = []
    stock_date = datetime.strptime(str(data[0][1]), '%Y%m%d').date()
    for row in data:
        if str(row[1]) == str(stock_date).replace('-', ''):
            pre_row = copy.deepcopy(row)
            data_with_empty.append(row)
            data_with_complete.append(row)
            stock_date = stock_date + timedelta(1)
        else:
            while int(str(stock_date).replace('-', '')) < row[1]:
                pre_row = copy.deepcopy(pre_row)
                pre_row[1] = int(str(stock_date).replace('-', ''))
                data_with_complete.append(pre_row)
                stock_date = stock_date + timedelta(1)
            pre_row = copy.deepcopy(row)
            data_with_empty.append(row)
            data_with_complete.append(row)
            stock_date = stock_date + timedelta(1)
    return data_with_empty, data_with_complete

#补齐数据
def getAllData(orgdata):
    (df1, dataSet) = analysis(orgdata)
    data=pd.DataFrame(data=dataSet,columns=['code','date','open','high','low','close','amount','vol'])
    data['date'] = data['date'].apply(lambda x: pd.to_datetime(datetime.strptime(str(x),'%Y%m%d')))
    data=data.set_index(['date'], drop=False)
    data.index.name='date'
    return data

#计算第一个基础高低点日期位置
def getBaseCalcDate(data):
    loop= math.ceil(data.iloc[-1].close)
    df2 = data.iloc[-1 *loop:]
    maxdate= df2[df2.high == df2.high.max()].index[0]
    mindate= df2[df2.low == df2.low.min()].index[0]
    return maxdate, mindate

# 根据 calcDate 向前推 loop 周期的高低点计算
def getCalcDate(data, calcDate, loop = 1):
    # loop = [0,1,3,12]
    if loop == 0:
        highDate=data.loc[calcDate].date - timedelta(math.ceil(data.loc[calcDate].high))
        lowDate=data.loc[calcDate].date - timedelta(math.ceil(data.loc[calcDate].low))
    elif loop == 2:
        highDate=data.loc[calcDate].date - timedelta(math.ceil(data.loc[calcDate].high * 7))
        lowDate=data.loc[calcDate].date - timedelta(math.ceil(data.loc[calcDate].low * 7))
    else:
        highDate=data.loc[calcDate].date - timedelta(math.ceil(data.loc[calcDate].high * loop * BASEM))
        lowDate=data.loc[calcDate].date - timedelta(math.ceil(data.loc[calcDate].low * loop *  BASEM))
    return highDate, lowDate

#预测值得计算 base2data预测值起始点
def calcPreData(realData, outData, base2Data):  
    idx1=realData.iloc[0].date
    last1=base2Data.date
    for x in range(1, len(realData)):
        idx2 = idx1 + timedelta(1)
        last2 = last1 + timedelta(1)
        lastRow = realData.loc[idx2].copy()
        lastRow.date = last2
        lastRow.name = last2
        lastRow.close = base2Data.close * realData.loc[idx2].close / realData.iloc[0].close
        lastRow.high = base2Data.high * realData.loc[idx2].high / realData.iloc[0].high
        lastRow.low = base2Data.low * realData.loc[idx2].low / realData.iloc[0].low
        lastRow.open = base2Data.open * realData.loc[idx2].open / realData.iloc[0].open
        outData=outData.append(lastRow)
        idx1=idx2
        last1=last2
    return outData

##取前一天的数据
def getPrevData(df, date):
    if date < df.index[0]:
        return None
    try:
        return df.loc[date]
    except:
        return getPrevData(df, date - timedelta(1))

#计算数据初始化
def getCalcLastData(data, pre1, calcDate, high = True):
    dfn1 = data.loc[pre1:calcDate]
#     print(pre1, calcDate)
    idx1=pre1
    last1=calcDate
    dfn3 = pd.DataFrame()
    bz1data = data.loc[calcDate]
    dfn3 = dfn3.append(data.loc[calcDate])
#     bz1data=dfn2.iloc[0]
    return dfn1, calcPreData(dfn1, dfn3, bz1data)

##计算数据，画图
def showdata(codePath, code, loop, minFlg=1, nextDate=None):
    # code = "sz000859.day"
    # data2 = readTdxLdayFile("C:/soft/new_tdx/vipdoc/sz/lday/" + code)
    fileCodePath = "%s/vipdoc/%s/lday/%s%s.day"
    if code[:1] == '6':
        codePath = fileCodePath % (codePath, 'sh', 'sh', code)
    else:
        codePath = fileCodePath % (codePath, 'sz', 'sz', code)
    print(codePath)
    data2 = readTdxLdayFile(codePath)

    data=getAllData(data2)
    if nextDate == None:
        (maxdate1, mindate1) = getBaseCalcDate(data)
    else:
        (maxdate1, mindate1) = getBaseCalcDate(data.loc[:nextDate])
    # print("getBaseCalcDate", maxdate1, mindate1)
    # 低点计算
    if minFlg == 1:
        (maxdate, mindate) = getCalcDate(data, mindate1, loop=loop)
        dfn1,dfn2 = getCalcLastData(data, mindate, mindate1)
        txtLabel = 'data low:%s, low1:%s' % (mindate, mindate1)
    else:
        (maxdate, mindate) = getCalcDate(data, maxdate1, loop=loop)
        dfn1,dfn2 = getCalcLastData(data, maxdate, maxdate1)
        txtLabel = 'data high:%s, high1:%s' % (maxdate, maxdate1)

    fig = plt.figure(dpi=100,figsize=(16,9))
    
    # plt.plot(dfn1.close,label = txtLabel,linewidth = 1)
    plt.plot(data.loc[dfn1.iloc[0].date:].close,label = txtLabel,linewidth = 1)
    pToday =data.iloc[-1].date + timedelta(1)
    # plt.plot(pre2.close,label = 'high2',linewidth = 2)
    showEndDate = data.iloc[-1].date + timedelta(20)
    plt.plot(dfn2.loc[:showEndDate].close,label = 'code=%s, type=%s， today=%s' % (code, minFlg, pToday),linewidth = 2)
    plt.axvline(x=mindate1)
    plt.axvline(x=mindate)
    plt.axvline(x=pToday)
    plt.legend()
    plt.show()
# 30年 30季 30月 30周 30日
gannList30 = [{'label':'30Y', 'y': 30, 'm': 0, 'w': 0,'d': 0}
    , {'label':'30S', 'y': 7, 'm': 6, 'w': 0,'d': 0}
    , {'label':'30M', 'y': 2, 'm': 6, 'w': 0,'d': 0}
    , {'label':'30W', 'y': 0, 'm': 0, 'w':30,'d': 0}
    , {'label':'30D', 'y': 0, 'm': 0, 'w': 0,'d':30}] ##30循环

def doCalcDate(calcDate, lastDate):
    # fileCodePath = "%s/vipdoc/%s/lday/%s%s.day"
    # if code[:1] == '6' or idx == "1":
    #     codePath = fileCodePath % (codePath, 'sh', 'sh', code)
    # else:
    #     codePath = fileCodePath % (codePath, 'sz', 'sz', code)
    # print(codePath)
    # data2 = readTdxLdayFile(codePath)

    # data=getAllData(data2)
#     print("data", data.tail())
    # lastDate = 20230120
    calcDate = pd.to_datetime(datetime.strptime(str(calcDate), '%Y%m%d'))
    # lastDate = pd.to_datetime(datetime.strptime(str(lastDate), '%Y%m%d'))
    # posB1Day = calcBAYMDate(calcDate, gannList30[0], False)
    # posB2Day = calcBAYMDate(posB1Day, gannList30[0], False)
    # print("calcDate1", gannList30[0], posB1Day, posB2Day)
    # posB1Day = calcDate
    out = {}
    posB1Day = calcDate
    for x in gannList30:
        posE1Day = calcBAYMDate(calcDate, x, False)
        if posE1Day > lastDate:
            continue
        posE2Day = calcBAYMDate(posE1Day, x, False)
        while posE2Day < lastDate:
            posB1Day = posE2Day
            posE1Day = calcBAYMDate(posB1Day, x, False)
            if posE1Day > lastDate:
                posE2Day = calcBAYMDate(posB1Day, x, True)
                break
            posE2Day = calcBAYMDate(posE1Day, x, False)
            # else:
            #     posE2Day = posE21Day

        # if posE1Day < lastDate:
        #     posE2Day = calcBAYMDate(posE1Day, x, False)
        # else:
        #     if x == gannList30[0]:
        #         posB1Day = posE1Day
        #         continue
        #     posE2Day = calcBAYMDate(posB1Day, x, True)
        # print("calc:", x['label'], calcDate, posB1Day, posE1Day, lastDate, posE2Day)
            # continue
        if posE1Day > posE2Day:
            temp = posE2Day
            posE2Day = posE1Day
            posE1Day = temp
            # print(posE2Day, lastDate, posE2Day < lastDate)
        # while posE2Day < lastDate:
        #     posB1Day = posE2Day
        #     posE1Day = calcBAYMDate(posB1Day, x, False)
        #     posE2Day = calcBAYMDate(posE1Day, x, False)

#         print("循环周期:", x['label'], "基点:", posB1Day.date(), "点1:", posE1Day.date(), "点2:", posE2Day.date())
        if posB1Day > posE1Day:
            # begD = data.loc[posE1Day]
            days = (lastDate - posB1Day).days - 20
            out[x['label']] = [posE1Day, posB1Day, posE2Day, days]
        else:
            # begD = data.loc[posB1Day]
            days = (lastDate - posE1Day).days - 20
            out[x['label']] = [posB1Day, posE1Day, posE2Day, days]
            
        # if x == gannList30[0]:
        #     posB1Day = posE1Day
        # if posE1Day > posB1Day and posE1Day > lastDate:
        #      posB1Day = posE1Day
    return out

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
    # p_df = p_df.reset_index()
    # 获取最新的period条数据
    # df1 = p_df.tail(period).reset_index(drop=True)
    df1 = p_df.copy().reset_index(drop=True)
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
    trade_date = data['date']
    days = trade_date - trade_date.shift(1)
    # 填充后转换为实际的天数数字
    days = (days.fillna(pd.Timedelta(0))).apply(lambda x:x.days)
    data['days'] = days
    # 对日期进行转换
#     data['date']=trade_date.apply(lambda x:x.strftime('%Y-%m-%d'))
    return data


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 4:
        # print('请输入通达信目录，股票代码路径，计划周期【当日 0，月1，周2，季3，年12】，高点点标记【低：1,高：0】，前测日期')
        print('请输入通达信目录，股票代码路径，idx=1：大盘 代码 日循环天数')
        print('例子: python gann-test-new.py C:/soft/new_tdx 1 000001 500')
        exit()

    codePath=sys.argv[1]
    idx=sys.argv[2]
    code=sys.argv[3]
    loopNums = sys.argv[4]
    # print("开始日期", calcData)
    # if argc >= 3:
    #     calcData = sys.argv[3:]
    # else:
    #     nextDate = None
    # exit()

    # elif argc == 3:
    # print(sys.argv)
    # if sys.argv[1] == 'all':
    #     run_all()
    # else:
    # allData = []
    fileCodePath = "%s/vipdoc/%s/lday/%s%s.day"
    if code[:1] == '6' or idx == "1":
        codePath = fileCodePath % (codePath, 'sh', 'sh', code)
    else:
        codePath = fileCodePath % (codePath, 'sz', 'sz', code)
    # print(codePath)
    data2 = readTdxLdayFile(codePath)

    allData=getAllData(data2)
    chkDates = h_l_line(allData, t = int(loopNums))

    lastDate = allData.index[-1]
    fig = plt.figure(dpi=100,figsize=(16,10))
    for idx2 in range(0, len(chkDates)):
    # for x in chkDates:
        x = datetime.strftime(chkDates.iloc[idx2].date.date(),'%Y%m%d')
        out = doCalcDate(calcDate = x, lastDate = lastDate)
        # fig = plt.figure(dpi=100,figsize=(16,9))
        for dx in out:
            # print("calcDate", dx, out[dx])
            predDf = pd.DataFrame() #预测值
            dbuf = []
            date0 =  out[dx][0]
            dataB0 = allData.loc[date0]
            date1 =  out[dx][1]
            dataB1 = allData.loc[date1]
            date2 =  out[dx][2]
            dataBN = out[dx][3]
            real0Date = date0 + timedelta(dataBN)
            pred0Date = date1 + timedelta(dataBN)
            label = "%s:%s:%s:%s:%s" % (code,dx,date0.date(),date1.date(),real0Date.date())
            N1 = (date1 - date0).days
            if N1 > 50:
                N1 = 50
            # print(out[1][dx])
            # print("calcDate", real0Date, pred0Date, N1)
            # bz1Date = dateg[0]
            pred1Date = pred0Date
            idx = 0
            hasData = True
            while idx < N1:
                # print(pred1Date + timedelta(idx))
                prow = allData.loc[real0Date + timedelta(idx)].copy()
                prow.date = pred1Date + timedelta(idx)
                # if idx == 0:
                #     print("close", dataB1.close, dataB0.close, prow.close, dataB1.close / dataB0.close * prow.close)
                prow.close = dataB1.close / dataB0.close * prow.close
                prow.high = dataB1.high / dataB0.high * prow.high
                prow.low = dataB1.low / dataB0.low * prow.low
                prow.open = dataB1.open / dataB0.open * prow.open
                prow.amount = dataB1.amount / dataB0.amount * prow.amount
                prow.vol = dataB1.vol / dataB0.vol * prow.vol
                dbuf.append(prow)
                chkDays = (lastDate - prow.date).days
                idx = idx + 1
                if chkDays < 20 and chkDays >= 0 and abs(prow.close - allData.loc[prow.date].close) / allData.loc[prow.date].close > 0.1:
                    # print("chk-data", chkDays, lastDate, prow.date)
                    hasData = False
                    break

            if hasData == False:
                continue

            tdata=pd.DataFrame(data=dbuf,columns=['code','date','open','high','low','close','amount','vol'])
            tdata.to_csv("%s-%s.csv" % (code, dx))
            tdata=tdata.set_index(['date'], drop=False)
            tdata.index.name='date'
            # print("tdata", tdata.tail(5))
            
            
            # plt.plot(dfn1.close,label = txtLabel,linewidth = 1)
            plt.plot(tdata.close,label = label,linewidth = 1)
            # pToday =lastDate
            # print("last-date", pToday)
            # plt.plot(pre2.close,label = 'high2',linewidth = 2)
            # showEndDate = data.iloc[-1].date + timedelta(20)
            # plt.plot(dfn2.loc[:showEndDate].close,label = 'code=%s, type=%s， today=%s' % (code, minFlg, pToday),linewidth = 2)
            # plt.axvline(x=mindate1)
            # plt.axvline(x=mindate)
            plt.axvline(x=lastDate)
    realData = allData.iloc[-30:].copy()
    plt.plot(realData.close,label = 'real',linewidth = 2)
    plt.legend()
    plt.show()
            
            # break
    # showdata(codePath=codePath, code=code, loop=30, minFlg=1, nextDate=calcData[0])
