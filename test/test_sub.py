
from easyquant import EasyMq
from easyquant import MongoIo
import pandas as pd
from easyquant import base
import talib as tdx
from easyquant.indicator.udf_formula import *

# # import pandas as pd

# # a = EasyMq()

# # a.init_receive(exchange='stockcn')
# # a.add_sub_key('000735')
# # a.add_sub_key('000410')

# # a.start()

# from easyquant import MongoIo
# m=MongoIo()
# a=m.get_stock_day('000028')
# # a.date=pd.to_datetime(a.date)
# # b=a.set_index(['date'])

# print(udf_yao_check_df(a))

# con1=base.BARSLAST(b.close>10)
# print(con1.head())

# df=pd.concat([tdx.MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)[-1:]
# df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

# print(df.m5.iloc[-1])



m=MongoIo()

# d1=m.get_index_min_realtime("000001")
# print(d1.tail())

d2=m.get_index_min_realtime('513050')
print(d2.tail())

import json

m.db['collection'].insert(json.loads(d2.T.to_json()).values())


