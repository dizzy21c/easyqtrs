
from functools import reduce
import math
import numpy as np
import pandas as pd
from ctypes import *
# from .talib_series import LINEARREG_SLOPE
from easyquant.easydealutils.easymongo import MongoIo
import datetime
try:
    import talib
except:
    print('PLEASE install TALIB to call these methods')

from easyquant import MongoIo
from easyquant.indicator.base import *
import sys

import os
# # lib  = cdll.LoadLibrary("%s/%s" % (os.path.abspath("."), "talib_ext.so"))
lib  = cdll.LoadLibrary("./talib_ext.so")
#
# def SUMS(Series, NS):
#     ncount = len(NS)
#     tf_p=c_float * ncount
#     np_OUT =tf_p(0)
#     na_Series=np.asarray(Series).astype(np.float32)
#     na_NS=np.asarray(NS).astype(np.int32)
#
#     np_S=cast(na_Series.ctypes.data, POINTER(c_float))
#     np_N=cast(na_NS.ctypes.data, POINTER(c_int))
#
#     lib.sum(ncount, np_OUT, np_S, np_N)
#
#     return pd.Series(np.asarray(np_OUT))
#
#
def EMA2(Series, Weight):
    ncount = len(Series)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)
    na_Series = np.asarray(Series).astype(np.float32)
#     na_Weight = np.asarray(Weight.fillna(1)).astype(np.float32)

    np_S = cast(na_Series.ctypes.data, POINTER(c_float))
#     np_W = cast(na_Weight.ctypes.data, POINTER(c_float))

    lib.ema(ncount, np_OUT, np_S, Weight)

    return pd.Series(np.asarray(np_OUT), index=Series.index)

def COSTA(Data, Percent):
    # print(Capital, type(Capital))
    ncount = len(Data)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)
#     capital = CAPITAL(Data)

    na_High = np.asarray(Data.high).astype(np.float32)
    na_Low = np.asarray(Data.low).astype(np.float32)
    na_Vol = np.asarray(Data.volume * 100).astype(np.float32)
    na_Amount = np.asarray(Data.amount).astype(np.float32)
    na_Turnover = np.asarray(Data.turn/100).astype(np.float32)
    np_H = cast(na_High.ctypes.data, POINTER(c_float))
    np_L = cast(na_Low.ctypes.data, POINTER(c_float))
    np_V = cast(na_Vol.ctypes.data, POINTER(c_float))
    np_A = cast(na_Amount.ctypes.data, POINTER(c_float))
    np_Turnover = cast(na_Turnover.ctypes.data, POINTER(c_float))
    # np_C = cast(na_Close.ctypes.data, POINTER(c_float))
    # np_H = cast(na_High.ctypes.data, POINTER(c_float))
    # np_W = cast(na_Weight.ctypes.data, POINTER(c_float))
    lib.cost(ncount, np_OUT, np_H, np_L, np_V, np_A, Percent, np_Turnover)
    # lib.winner(ncount, np_OUT, np_S, np_W)
    return pd.Series(np.asarray(np_OUT), dtype=np.float64, index=Data.index)

def WINNERA(Data,Price = None):
    ncount = len(Data)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)

    na_High = np.asarray(Data.high).astype(np.float32)
    na_Low = np.asarray(Data.low).astype(np.float32)
    na_Vol = np.asarray(Data.volume*100).astype(np.float32)
    na_Amount = np.asarray(Data.amount).astype(np.float32)
    na_Turnover = np.asarray(Data.turn/100).astype(np.float32)

    if Price is None:
        na_Close = np.asarray(Data.close).astype(np.float32)
    else:
        Data['price'] = Price
        na_Close = np.asarray(Data['price']).astype(np.float32)

    np_H = cast(na_High.ctypes.data, POINTER(c_float))
    np_L = cast(na_Low.ctypes.data, POINTER(c_float))
    np_V = cast(na_Vol.ctypes.data, POINTER(c_float))
    np_A = cast(na_Amount.ctypes.data, POINTER(c_float))
    np_C = cast(na_Close.ctypes.data, POINTER(c_float))
    np_Turnover = cast(na_Turnover.ctypes.data, POINTER(c_float))
    # np_H = cast(na_High.ctypes.data, POINTER(c_float))
    # np_W = cast(na_Weight.ctypes.data, POINTER(c_float))
    lib.winner(ncount, np_OUT, np_H, np_L, np_V, np_A, np_C, np_Turnover)
    # lib.winner(ncount, np_OUT, np_S, np_W)
    return pd.Series(np.asarray(np_OUT), dtype=np.float64, index=Data.index)
#
# def COST(Data, Percent, Capital):
#     # print(Capital, type(Capital))
#     ncount = len(Data)
#     tf_p = c_float * ncount
#     np_OUT = tf_p(0)
#
#     na_High = np.asarray(Data.high).astype(np.float32)
#     na_Low = np.asarray(Data.low).astype(np.float32)
#     na_Vol = np.asarray(Data.volume).astype(np.float32)
#     na_Amount = np.asarray(Data.amount).astype(np.float32)
#
#     # if Price is None:
#     #     na_Close = np.asarray(Data.close).astype(np.float32)
#     # else:
#     #     Data['price'] = Price
#     #     na_Close = np.asarray(Data['price']).astype(np.float32)
#     # na_High = np.asarray(Data.high).astype(np.float32)
#
#     # na_Weight = np.asarray(Weight.fillna(1)).astype(np.float32)
#
#     np_H = cast(na_High.ctypes.data, POINTER(c_float))
#     np_L = cast(na_Low.ctypes.data, POINTER(c_float))
#     np_V = cast(na_Vol.ctypes.data, POINTER(c_float))
#     np_A = cast(na_Amount.ctypes.data, POINTER(c_float))
#     # np_C = cast(na_Close.ctypes.data, POINTER(c_float))
#     # np_H = cast(na_High.ctypes.data, POINTER(c_float))
#     # np_W = cast(na_Weight.ctypes.data, POINTER(c_float))
#     lib.cost(ncount, np_OUT, np_H, np_L, np_V, np_A, Percent, c_float(Capital))
#
#     # lib.winner(ncount, np_OUT, np_S, np_W)
#
#     return pd.Series(np.asarray(np_OUT), index=Data.index)


print("exam:python test_func.py <code:123456> <func-name:dqe_test_A01>")

m=MongoIo()
data=m.get_stock_day(sys.argv[1], st_start="1999-10-08",qfq=1)
print("data-len", len(data))
start_t = datetime.datetime.now()

# # print(data.close[:10])
# out = EMA2(data.close, 5)
# print(out[:10])
# print("winner ...")
# out2 = WINNERA(data)
# print(out2[-1:])
print("cost ...")
out2 = COSTA(data, 25)
print(out2[-1:])

# out=eval("%s" % sys.argv[2])(data, None)
# end_t = datetime.datetime.now()
# print(end_t, 'tdx_func_mp spent:{}'.format((end_t - start_t)))
# EMA2(out, 5)
# print(out[0:3])
# print(out[-10:])
