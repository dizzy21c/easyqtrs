import os
import struct
import pandas as pd
import numpy as np
import time, datetime
import multiprocessing

def readTdxLdayFile(fname="data/sh000001.day"):
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
  data['date'] = data['tradeDate'].apply(lambda x: datetime.datetime.strptime(str(x),'%Y%m%d').date())
  data=data.set_index(['date']) #.sort_index
  return code, data

def recalc(code, data):
    if data.size == 0:
        return
    beg_date = data.index[0]
    end_date = data.index[-1]
    today = datetime.datetime.today().date()
    # date_p = datetime.datetime.strptime(str(data.tradeDate[0]),'%Y%m%d').date()
    # newdata=pd.DataFrame()
    # prerow=None
    ds = None
    while beg_date <= today:
        if beg_date in data.index:
            ds = data.loc[beg_date]
        else:
            ds.name = beg_date
            data = data.append(ds)
        
        beg_date = beg_date + datetime.timedelta(1)
    # for idx,row in data.iterrows():
    #     if str(row['tradeDate']) == str(date_p).replace('-',''):
    #         prerow=row
    #         output=output.append(row)
    #         date_p=date_p+datetime.timedelta(1)
    #     else:
    #         print(code, row['tradeDate'])
    #         while(int(str(date_p).replace('-','')) < row['tradeDate']):
    #             prerow['tradeDate']=int(str(date_p).replace('-',''))
    #             output=output.append(prerow)
    #             date_p=date_p+datetime.timedelta(1)
    #         prerow=row
    #         output=output.append(row)
    #         date_p=date_p+datetime.timedelta(1)
    data = data.sort_index()
    data.to_csv('%s.csv'%code)
    return data

def asyncCalc(fname, queue):
  code, df = readTdxLdayFile(fname)
  # queue.put(recalc(code, df))
  recalc(code, df)
    
def readPath(path):
  files = os.listdir(path)
  # codes=[]
  q = multiprocessing.Queue()
  jobs = []
  # dataSet=[]multiprocessing
  pool_size = multiprocessing.cpu_count()
  pool = multiprocessing.Pool(pool_size)
  output=pd.DataFrame()
  for i in range(0,len(files)):
    fname = os.path.join(path,files[i])
    if os.path.isdir(fname):
      continue
    pool.apply_async(asyncCalc, args=(fname))
    p = multiprocessing.Process(target=asyncCalc, args=(fname, q))
    jobs.append(p)
    p.start()
  
  for p in jobs:
    p.join()

  # for j in jobs:
  #   t = q.get()
#     if t is not None:
#       output=output.append(t)
  return output

readPath('data') #读取目录下面的所有文件
# print(output.head())
# output.to_csv('test-org.csv')
# output.query('dfh==True and dfc1==True and dfc2==True').to_csv('test-data.csv')
