
from easyquant.indicator.base import *
from easyquant  import MongoIo
from easyquant import MongoIo4Pl
import polars as pl
import pandas as pd
import math
from tdx.func.tdx_func import *
from tdx.func.func_sys import *
mongo = MongoIo()
try:
    import talib
except:
    print('PLEASE install TALIB to call these methods')
import pandas as pd
#import pandas as np
import QUANTAXIS as qa

start_t = datetime.datetime.now()
codelist = getCodeList('all')
databuf_mongo = mongo.get_stock_day(codelist, st_start='1990-01-01', st_end='2035-12-31')

# print("data-total-len:", len(dataR))
for code in codelist:
#     print(code)
    #tempData = mongo.get_stock_day([code], st_start = '1990-01-01')
    tempData = databuf_mongo.query("code=='%s'" % code)
    if len(tempData) == 0:
        continue
    try:
        #A1 = tdx_CDLPattern(tempData)[0].tail(3).sum()
        A1 = tdx_JZZCJSD(tempData)[0].tail(3).sum()
#         print(A1.sum())
#         if A1 > 0:
#             print(code, 'tdx_CDYTDXG', A1)
    except:
        pass
#     try:
#         A2 = tdx_LLDDX(data)[0].tail(5).sum()
#         if A2 > 0:
#             print(code, 'tdx_LLDDX', A2)
#     except:
#         pass
#    break
end_t = datetime.datetime.now()
# print("data-total-len:", len(dataR))
print(end_t, 'get_data spent:{}'.format((end_t - start_t)))

