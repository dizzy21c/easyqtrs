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

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 5:
        print('请输入通达信目录，股票代码路径，计划周期【当日 0，月1，周2，季3，年12】，高点点标记【低：1,高：0】，前测日期')
        print('例子: python gann-test.py C:/soft/new_tdx 000859 1 1 20221001')
        exit()
    
    if argc == 6:
        nextDate = datetime.strptime(sys.argv[5], '%Y%m%d') + timedelta(1)
    else:
        nextDate = None
    
    # elif argc == 3:
    # print(sys.argv)
    # if sys.argv[1] == 'all':
    #     run_all()
    # else:
    showdata(codePath=sys.argv[1], code=sys.argv[2], loop=int(sys.argv[3]), minFlg=int(sys.argv[4]), nextDate=nextDate)
