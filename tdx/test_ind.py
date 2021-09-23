from easyquant import MongoIo
from easyquant.indicator.base import *
from time import strftime, localtime
import datetime
import pandas as pd
import sys
mongo = MongoIo()

argv = sys.argv[1:]
if len(argv) > 1:
  codes=argv[1:]
else:
  # codes = ['000001']
  codes = list(mongo.get_positions().index)
  
if len(argv) > 2:
  fname = argv[2]
  # print(fname)
  codeDf = pd.read_csv(fname, sep='\t')
  codes=list(codeDf['代码'])[:-1]


# print("codes", codes)
dateFmt = '%Y-%m-%d'
if len(argv) > 0:
  dateStr = argv[0]
else:
  dateStr = strftime(dateFmt,localtime())
  

df = pd.DataFrame()
for code in codes:
  cdata = {}
  data = mongo.get_stock_day(code)
  if len(data) == 0:
    print("code %s is 0" % code)
    continue
  # print(len(data))

  # to = TURNOVER(data, dateStr)
  # print(to, BIDASKVOL(data, dateStr))
  # print(CAPITAL(data))
  # print(__INITDATAS())
  cap = CAPITAL(data)
  cdata = {'code':code}
  for x in range(-6, 1):
    # cdObj = pd.to_datetime(dateStr) + datetime.timedelta(x)
    cdObj = datetime.datetime.strptime(dateStr,dateFmt) +  + datetime.timedelta(x)
    if cdObj.weekday() > 4:
      continue
    cdStr = cdObj.strftime(dateFmt)
    to = TURNOVER(data, cdStr)
    cdata[cdStr] = to[0] / cap
    if x == 0:
      ld = mongo.get_realtime(code = code, dateStr = cdStr)
      if len(ld) > 0:
        cdata['now'] = float(ld.at[ld.index[-1],'now'])
        lclose = float(ld.at[ld.index[-1],'close'])
        # print(type(lclose), type(cdata['now']))
        if lclose > 0:
          cdata['chg'] = (cdata['now'] - lclose) / lclose * 100
        else:
          cdata['chg'] = 0.0
      else:
        cdata['now'] = 0.0
        cdata['chg'] = 0.0
  # df = df.append({'code':code, 'cap':cap, 'mmb': to[0] / cap}, ignore_index=True)
  # print(cdata)
  df = df.append(cdata, ignore_index=True)
  # print(cap.tail)
  # print("code=%s, mmb %6.2f" % (code, to[0] / cap))
df = df.set_index(['code'])
# print(df)
print(df.sort_values(by=dateStr))
