from easyquant.indicator.base import *
from easyquant  import MongoIo
from easyquant import MongoIo4Pl
import polars as pl
# import pandas as pd
import math
from tdx.func.tdx_func import *
mongo = MongoIo()
try:
    import talib
except:
    print('PLEASE install TALIB to call these methods')
import pandas as pd
import numpy as np
lib  = cdll.LoadLibrary("/usr/share/talib/%s" % ("talib_ext.so"))


code = "002230"
data = mongo.get_stock_day([code], st_start = '1900-01-01')


C = data.close
O = data.open
X_1=EMA(C,2)
X_2=EMA(C,5)
X_3=EMA(C,13)
X_4=EMA(C,30)
X_5=X_2>=REF(X_2,1)
X_6=MAX(MAX(X_2,X_3),X_4)
X_7=MIN(MIN(X_2,X_3),X_4)
X_8=IFAND4(X_6<C, O<X_7, X_5, X_1>REF(X_1,1), True, False)
X_9=IF(X_8,1,0)
X_10=MA(C,5)
X_11=ATAN((X_10/REF(X_10,1)-1)*100)*180/3.1416
X_12=SMA(EMA((X_10-REF(X_10,1))/REF(X_10,1),3)*100,3,1)
X_13=EMA((X_12-REF(X_12,1)),3)
X_14=MA(C,10)
X_15=MA(C,30)
X_16=(C-X_15)/X_15*100
X_17_1 = IFAND3(COUNT(CROSS(X_11,30),5) >= 1, X_10>REF(X_10,1), X_16>REF(X_16,1), True, False)
X_17_2 = IFAND3(X_14>REF(X_14,1), X_13>REF(X_13,1), X_12>REF(X_12,1), True, False)

def FILTER3(COND, N):
#     ncount = len(COND)
#     ti_p = c_int * ncount
#     np_OUT = ti_p(0)
#     na_Cond = np.asarray(COND).astype(np.int32)
#     # na_NS=np.asarray(NS).astype(np.int32)
#     np_S = cast(na_Cond.ctypes.data, POINTER(c_int))
#     # np_N=cast(na_NS.ctypes.data, POINTER(c_int))
#     lib.filter(ncount, np_OUT, np_S, N)
#     return pd.Series(np.asarray(np_OUT), index=COND.index)

    ncount = len(cond)
    ti_p=c_int * ncount
    np_OUT =ti_p(0)
    na_Cond =np.asarray(cond).astype(np.float32)
    # na_NS=np.asarray(NS).astype(np.int32)
    
    np_S=cast(na_Cond.ctypes.data, POINTER(c_float))
    # np_N=cast(na_NS.ctypes.data, POINTER(c_int))
    
    lib.filter(ncount, np_OUT, np_S, N)
    
    return pd.Series(np.asarray(np_OUT), index=cond.index)


# cond = IFAND(X_17_1, X_17_2, 1, 0)
cond = IFAND(X_17_1, X_17_2, True, False)

out2 = tdx_JZZCJSD(data, False)[0]
print("out2", out2.iloc[-24: -9])