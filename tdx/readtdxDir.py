import os
import struct
import pandas as pd
import numpy as np

def readTdxLdayPath(path):
  files = os.listdir(path)
  dataSet=[]
  for i in range(0,len(files)):
    fname = os.path.join(path,files[i])
    if os.path.isdir(fname):
      continue
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

  data=pd.DataFrame(data=dataSet,columns=['code','tradeDate','open','high','low','close','amount','vol'])
  data=data.set_index(['code','tradeDate'])
  return data

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

  data=pd.DataFrame(data=dataSet,columns=['code','tradeDate','open','high','low','close','amount','vol'])
#   data=data.set_index(['tradeDate'])
  return data

df=readTdxLdayFile()
df.to_csv('sh-data.csv')
df['mon'] = df.tradeDate.apply(lambda x : str(x)[0:6])
df['year'] = df.tradeDate.apply(lambda x : str(x)[0:4])
df=df.set_index(['tradeDate'])
dfmax=df.groupby(['mon']).apply(lambda x: x[x.high ==x.high.max()])
dfmax.drop_duplicates(subset=['high','mon'],keep='first',inplace=True)
dfmin=df.groupby(['mon']).apply(lambda x: x[x.low ==x.low.min()])
dfmin.drop_duplicates(subset=['low','mon'],keep='first',inplace=True)
dfmax.to_csv("mon-max.csv")
dfmin.to_csv("mon-min.csv")

dfymax=df.groupby(['year']).apply(lambda x: x[x.high ==x.high.max()])
dfymin=df.groupby(['year']).apply(lambda x: x[x.low ==x.low.min()])
dfymax.to_csv("year-max.csv")
dfymin.to_csv("year-min.csv")

for index, row in dfmax.iterrows():
    # if index[1] == 19901231:
    print(index[1])
    print(row.close)


data_df=readTdxLdayPath('data') #读取目录下面的所有文件
