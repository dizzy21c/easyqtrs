# import os
# import struct
# import pandas as pd

# def readTdxLdayFile(fname="/home/zhangjx/Downloads/sh000001.day"):
#   dataSet=[]
#   with open(fname,'rb') as fl:
#     buffer=fl.read() #读取数据到缓存
#     size=len(buffer) 
#     rowSize=32 #通信达day数据，每32个字节一组数据
#     code=os.path.basename(fname).replace('.day','')
#     for i in range(0,size,rowSize): #步长为32遍历buffer
#       row=list( struct.unpack('IIIIIfII',buffer[i:i+rowSize]) )
#       row[1]=row[1]/100
#       row[2]=row[2]/100
#       row[3]=row[3]/100
#       row[4]=row[4]/100
#       row.pop() #移除最后无意义字段
#       row.insert(0,code)
#       dataSet.append(row) 

#   data=pd.DataFrame(data=dataSet,columns=['code','tradeDate','open','high','low','close','amount','vol'])
#   data=data.set_index(['code','tradeDate'])
#   print(data)

# readTdxLdayFile()
import os
import struct
import pandas as pd
import numpy as np

def readTdxLdayFile(fname="/home/zhangjx/Downloads/sh000001.day"):
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
df['mon'] = df.tradeDate.apply(lambda x : str(x)[0:6])
df=df.set_index(['tradeDate'])
dfmax=df.groupby(['mon']).apply(lambda x: x[x.close ==x.close.max()])
dfmin=df.groupby(['mon']).apply(lambda x: x[x.close ==x.close.min()])
# dfmax.head()
# dfmin.head()
dfmax.to_csv("max.csv")
dfmin.to_csv("min.csv")
