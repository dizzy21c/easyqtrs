# coding:utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2016-2018 yutiansut/QUANTAXIS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


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

import os
# lib  = cdll.LoadLibrary("%s/%s" % (os.path.abspath("."), "talib_ext.so"))
lib  = cdll.LoadLibrary("/usr/share/talib/%s" % ("talib_ext.so"))


"""
Series 类

这个是下面以DataFrame为输入的基础函数
return pd.Series format
"""

__STOCK_INFOS = pd.DataFrame()
__REALTIME_DATAS = {}

def __INITDATAS(dateStr = None):
    mongo = MongoIo()
    global __STOCK_INFOS, __REALTIME_DATAS
    if len(__STOCK_INFOS) == 0:
        __STOCK_INFOS = mongo.get_stock_info()
    # STOCK_INFOS = 
    if dateStr == None:
        dateObj = datetime.datetime.now()
    else:
        # datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S"))
        dateObj = datetime.datetime.strptime(dateStr, "%Y-%m-%d")
    weekDay = dateObj.weekday()
    if weekDay > 4:
        dateObj = dateObj - datetime.timedelta(weekDay - 4)
    dateStr = dateObj.strftime('%Y-%m-%d')
    if dateStr not in __REALTIME_DATAS.keys():
        __REALTIME_DATAS[dateStr] = mongo.get_realtime(dateStr=dateStr)
    return dateStr

def __STOCK_INFO(code):
    __INITDATAS()
    return __STOCK_INFOS.query("code=='%s'" % code)

def __REALTIME_DATA(code, dateStr):
    global __REALTIME_DATAS
    dateStr = __INITDATAS(dateStr)
    try:
        return __REALTIME_DATAS[dateStr].query("code=='%s'" % code)
    except Exception as e:
        # print("__REALTIME_DATA", code, dateStr, e)
        return pd.DataFrame()

def EMA_TA(Series, N):
    # return pd.Series.ewm(Series, span=N, min_periods=N - 1, adjust=True).mean()
    if N == 1:
        return Series
#     Series = Series.fillna(0)
    return talib.EMA(Series, N)
#     return pd.Series(res, index=Series.index)

def EMA(Series, N):
    ncount = len(Series)
    Series = Series.fillna(0)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)
    na_Series = np.asarray(Series).astype(np.float32)
    np_S = cast(na_Series.ctypes.data, POINTER(c_float))
    lib.ema(ncount, np_OUT, np_S, N)
    return pd.Series(np.asarray(np_OUT), index=Series.index)

def EXPMA(Series, N):
    # return pd.Series.ewm(Series, span=N, min_periods=N - 1, adjust=True).mean()
    if N == 1:
        return Series
#     Series = Series.fillna(0)
    return talib.EMA(Series, N)
#     return pd.Series(res, index=Series.index)

def MA(Series, N):
    return talib.MA(Series, N)

def VAR(Series, N, M = 1):
    return talib.VAR(Series, timeperiod=N, nbdev=m)

# 威廉SMA  参考https://www.joinquant.com/post/867
def SMA(Series, N, M=1):
    """
    威廉SMA算法

    本次修正主要是对于返回值的优化,现在的返回值会带上原先输入的索引index
    2018/5/3
    @yutiansut
    """
    ret = []
    i = 1
    length = len(Series)
    # 跳过X中前面几个 nan 值
    while i < length:
        if np.isnan(Series.iloc[i-1]):
            ret.append(0)
            i += 1
        else:
            break
    if i < length:
        preY = Series.iloc[i-1]  # Y'
    else:
        preY = None
    ret.append(preY)
    while i < length:
        Y = (M * Series.iloc[i] + (N - M) * preY) / float(N)
        ret.append(Y)
        preY = Y
        i += 1
    return pd.Series(ret, index=Series.tail(len(ret)).index)


def DIFF(Series, N=1):
    return pd.Series(Series).diff(N)


def HHV(Series, NS):
    if isinstance(NS, int):
        NS = [ NS for i in range(len(Series))]
        for i in range(0,NS[0]):
            NS[i] = i
        NS = pd.Series(NS)

    ncount = len(NS)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)
    na_Series = np.asarray(Series).astype(np.float32)
    na_NS = np.asarray(NS).astype(np.int32)

    np_S = cast(na_Series.ctypes.data, POINTER(c_float))
    np_N = cast(na_NS.ctypes.data, POINTER(c_int))

    lib.hhv(ncount, np_OUT, np_S, np_N)

    return pd.Series(np.asarray(np_OUT), dtype=np.float64, index=Series.index)

#     if isinstance(NS, pd.Series):
#         ncount = len(NS)
#         tf_p = c_float * ncount
#         np_OUT = tf_p(0)
#         na_Series = np.asarray(Series).astype(np.float32)
#         na_NS = np.asarray(NS).astype(np.int32)

#         np_S = cast(na_Series.ctypes.data, POINTER(c_float))
#         np_N = cast(na_NS.ctypes.data, POINTER(c_int))

#         lib.hhv(ncount, np_OUT, np_S, np_N)

#         return pd.Series(np.asarray(np_OUT), dtype=np.float64, index=Series.index)

#     if NS == 0:
#         return Series

#     return talib.MAX(Series, NS) #pd.Series(Series).rolling(NS).max()


def LLV(Series, NS):
    if isinstance(NS, int):
        NS = [ NS for i in range(len(Series))]
        for i in range(0,NS[0]):
            NS[i] = i
        NS = pd.Series(NS)
    ncount = len(NS)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)
    na_Series = np.asarray(Series).astype(np.float32)
    na_NS = np.asarray(NS).astype(np.int32)

    np_S = cast(na_Series.ctypes.data, POINTER(c_float))
    np_N = cast(na_NS.ctypes.data, POINTER(c_int))

    lib.llv(ncount, np_OUT, np_S, np_N)

    return pd.Series(np.asarray(np_OUT), dtype=np.float64, index=Series.index)

#     if isinstance(NS, pd.Series):
#         ncount = len(NS)
#         tf_p = c_float * ncount
#         np_OUT = tf_p(0)
#         na_Series = np.asarray(Series).astype(np.float32)
#         na_NS = np.asarray(NS).astype(np.int32)

#         np_S = cast(na_Series.ctypes.data, POINTER(c_float))
#         np_N = cast(na_NS.ctypes.data, POINTER(c_int))

#         lib.llv(ncount, np_OUT, np_S, np_N)

#         return pd.Series(np.asarray(np_OUT), dtype=np.float64, index=Series.index)

#     if NS == 0:
#         return Series

#     return talib.MIN(Series, NS) #pd.Series(Series).rolling(NS).min()

def SUMS(Series, NS):
    ncount = len(Series)
    tf_p=c_float * ncount
    np_OUT =tf_p(0)
    na_Series=np.asarray(Series).astype(np.float32)
    na_NS=np.asarray(NS).astype(np.int32)
    
    np_S=cast(na_Series.ctypes.data, POINTER(c_float))
    np_N=cast(na_NS.ctypes.data, POINTER(c_int))
    
    lib.sum(ncount, np_OUT, np_S, np_N)

    return pd.Series(np.asarray(np_OUT), dtype=np.float64)

def SUMBARS(Series, NS):
    ncount = len(Series)
    if isinstance(NS, pd.Series):
        pass
    else:
        nsA = np.full(ncount, NS, dtype = float)
        NS = pd.Series(nsA, index = Series.index)
    tf_p=c_float * ncount
    np_OUT =tf_p(0)
    na_Series=np.asarray(Series).astype(np.float32)
    na_NS=np.asarray(NS).astype(np.float32)
    
    np_S=cast(na_Series.ctypes.data, POINTER(c_float))
    np_N=cast(na_NS.ctypes.data, POINTER(c_float))
    
    lib.sumbars(ncount, np_OUT, np_S, np_N)

    return pd.Series(np.asarray(np_OUT), dtype=np.float64)

def DMA(Series, Weight):
    ncount = len(Series)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)
    na_Series = np.asarray(Series).astype(np.float32)
    na_Weight = np.asarray(Weight.fillna(1)).astype(np.float32)

    np_S = cast(na_Series.ctypes.data, POINTER(c_float))
    np_W = cast(na_Weight.ctypes.data, POINTER(c_float))

    lib.dma(ncount, np_OUT, np_S, np_W)

    return pd.Series(np.asarray(np_OUT), dtype=np.float64, index=Series.index)


def SUM(Series, N):
    if N == 0:
        return Series.cumsum()
    else:
        return pd.Series.rolling(Series, N).sum()


def ABS(Series):
    return abs(Series)


def MAX(A, B):
    var = IF(A > B, A, B)
    return var


def MIN(A, B):
    var = IF(A < B, A, B)
    return var


def SINGLE_CROSS(A, B):
    if A.iloc[-2] < B.iloc[-2] and A.iloc[-1] > B.iloc[-1]:
        return True
    else:
        return False


def CROSS(A, B):
    """A<B then A>B  A上穿B B下穿A

    Arguments:
        A {[type]} -- [description]
        B {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    if isinstance(A, int) or isinstance(A, float):
        A1 = pd.Series(B).copy()
        A1[:] = A
        A = A1

    var = np.where(A < B, 1, 0)
    return (pd.Series(var, index=A.index).diff() < 0).apply(int)


def COUNT(COND, N):
    """
    2018/05/23 修改

    参考https://github.com/QUANTAXIS/QUANTAXIS/issues/429

    现在返回的是series
    """
    return pd.Series(np.where(COND, 1, 0), index=COND.index).rolling(N).sum()


def IF(COND, V1, V2):
    # if isinstance(V1, np.int64) or isinstance(V1, np.int):
    if isinstance(COND, np.bool_) or isinstance(COND, bool):
        if COND:
            return V1
        else:
            return V2

    var = np.where(COND, V1, V2)
    if isinstance(V1, pd.Series):
        return pd.Series(var, index=V1.index)
    else:
        return pd.Series(var, index=COND.index)


def IFAND(COND1, COND2, V1, V2):
    if isinstance(COND1, np.bool) and isinstance(COND2, np.bool):
        if COND1 and COND2:
            return V1
        else:
            return V2
    if isinstance(COND1, np.bool_) or isinstance(COND1, bool):
        temp = COND1
        COND1 = COND2
        COND2 = temp
    elif isinstance(COND2, np.bool_) or isinstance(COND2, bool):
        pass
    else:
        if len(COND1) < len(COND2):
            COND2=COND2[COND2.index>=COND1.index[0]]
        elif len(COND1) > len(COND2):
            COND1 = COND1[COND1.index >= COND2.index[0]]
    var = np.where(np.logical_and(COND1,COND2), V1, V2)
    return pd.Series(var, index=COND1.index)

def IFAND3(COND1, COND2, COND3, V1, V2):
    # if len(COND1) < len(COND2):
    #     COND2=COND2[COND2.index>=COND1.index[0]]
    # elif len(COND1) > len(COND2):
    #     COND1 = COND1[COND1.index >= COND2.index[0]]
    var1 = np.where(np.logical_and(COND1,COND2), True, False)
    var = np.where(np.logical_and(var1, COND3), V1, V2)
    return pd.Series(var, index=COND1.index)
    # if isinstance(V1, pd.Series):
    #     return pd.Series(var, index=V1.index)
    # else:
    #     return pd.Series(var, index=COND1.index)

def IFAND4(COND1, COND2, COND3, COND4, V1, V2):
    # if len(COND1) < len(COND2):
    #     COND2=COND2[COND2.index>=COND1.index[0]]
    # elif len(COND1) > len(COND2):
    #     COND1 = COND1[COND1.index >= COND2.index[0]]
    var1 = np.where(np.logical_and(COND1,COND2), True, False)
    var2 = np.where(np.logical_and(var1, COND3), True, False)
    var = np.where(np.logical_and(var2, COND4), V1, V2)
    return pd.Series(var, index=COND1.index)
    # if isinstance(V1, pd.Series):
    #     return pd.Series(var, index=V1.index)
    # else:
    #     return pd.Series(var, index=COND1.index)

def IFAND5(COND1, COND2, COND3, COND4, COND5, V1, V2):
    # if len(COND1) < len(COND2):
    #     COND2=COND2[COND2.index>=COND1.index[0]]
    # elif len(COND1) > len(COND2):
    #     COND1 = COND1[COND1.index >= COND2.index[0]]
    var1 = np.where(np.logical_and(COND1,COND2), True, False)
    var2 = np.where(np.logical_and(var1, COND3), True, False)
    var3 = np.where(np.logical_and(var2, COND4), True, False)
    var = np.where(np.logical_and(var3, COND5), V1, V2)
    return pd.Series(var, index=COND1.index)
    # if isinstance(V1, pd.Series):
    #     return pd.Series(var, index=V1.index)
    # else:
    #     return pd.Series(var, index=COND1.index)


def IFAND6(COND1, COND2, COND3, COND4, COND5, COND6, V1, V2):
    # if len(COND1) < len(COND2):
    #     COND2=COND2[COND2.index>=COND1.index[0]]
    # elif len(COND1) > len(COND2):
    #     COND1 = COND1[COND1.index >= COND2.index[0]]
    var1 = np.where(np.logical_and(COND1,COND2), True, False)
    var2 = np.where(np.logical_and(var1, COND3), True, False)
    var3 = np.where(np.logical_and(var2, COND4), True, False)
    var4 = np.where(np.logical_and(var3, COND5), True, False)
    var = np.where(np.logical_and(var4, COND6), V1, V2)
    return pd.Series(var, index=COND1.index)
    # if isinstance(V1, pd.Series):
    #     return pd.Series(var, index=V1.index)
    # else:
    #     return pd.Series(var, index=COND1.index)

def IFOR(COND1, COND2, V1, V2):
    if len(COND1) < len(COND2):
        COND2=COND2[COND2.index>=COND1.index[0]]
    elif len(COND1) > len(COND2):
        COND1 = COND1[COND1.index >= COND2.index[0]]
    var = np.where(np.logical_or(COND1,COND2), V1, V2)
    return pd.Series(var, index=COND1.index)
    # if isinstance(V1, pd.Series):
    #     return pd.Series(var, index=V1.index)
    # else:
    #     return pd.Series(var, index=COND1.index)
# 
def IFOR3(COND1, COND2, COND3, V1, V2):
    COND_N = IFOR(COND1, COND2, True, False)
    return IFOR(COND_N, COND3, V1, V2)

def IFOR4(COND1, COND2, COND3, COND4, V1, V2):
    COND_N1 = IFOR(COND1, COND2, True, False)
    COND_N2 = IFOR(COND1, COND2, True, False)
    return IFOR(COND_N1, COND_N2, V1, V2)

##TODO 通达信测试结果的出的
## 0 - 1
def FILTER(COND, N):
    ncount = len(COND)
    ti_p = c_int * ncount
    np_OUT = ti_p(0)
    na_Cond = np.asarray(COND).astype(np.int32)
    # na_NS=np.asarray(NS).astype(np.int32)
    np_S = cast(na_Cond.ctypes.data, POINTER(c_int))
    # np_N=cast(na_NS.ctypes.data, POINTER(c_int))
    lib.filter(ncount, np_OUT, np_S, N)
    return pd.Series(np.asarray(np_OUT), index=COND.index)

# true - false
def FILTER2(COND, N):
    ncount = len(cond)
    ti_p=c_bool * ncount
    np_OUT =ti_p(0)
    na_Cond =np.asarray(cond).astype(np.bool)
    # na_NS=np.asarray(NS).astype(np.int32)
    
    np_S=cast(na_Cond.ctypes.data, POINTER(c_bool))
    # np_N=cast(na_NS.ctypes.data, POINTER(c_int))
    
    lib.filter2(ncount, np_OUT, np_S, N)
    
    return pd.Series(np.asarray(np_OUT), index=cond.index)

def REF(Series, N):
    if isinstance(Series[0], bool) or isinstance(Series[0], np.bool_):
        N = pd.Series(np.full(len(Series),N), index=Series.index)
        
    if isinstance(N, pd.Series):
        # var = np.where(N > 0, Series[N.index - N], Series)
        # var = np.where(N > 0, Series[IF(N.index - N > 0, N.index - N, 0)], Series)
        N1 = N.reset_index()
        var = np.where(N > 0, Series[IF(N1.index - N > 0, N1.index - N, 0)], Series)
        return pd.Series(var, index=N.index)

    var = Series.diff(N)
    var = Series - var
    return var


def LAST(COND, N1, N2):
    """表达持续性
    从前N1日到前N2日一直满足COND条件

    Arguments:
        COND {[type]} -- [description]
        N1 {[type]} -- [description]
        N2 {[type]} -- [description]
    """
    N2 = 1 if N2 == 0 else N2
    assert N2 > 0
    assert N1 > N2
    return COND.iloc[-N1:-N2].all()


def STD(Series, N):
    return pd.Series.rolling(Series, N).std()


def AVEDEV(Series, N):
    """
    平均绝对偏差 mean absolute deviation
    修正: 2018-05-25 

    之前用mad的计算模式依然返回的是单值
    """
    return Series.rolling(N).apply(lambda x: (np.abs(x - x.mean())).mean(), raw=True)


def MACD(Series, FAST=12, SLOW=26, MID=9):
    """macd指标 仅适用于Series
    对于DATAFRAME的应用请使用QA_indicator_macd
    """
    EMAFAST = EMA(Series, FAST)
    EMASLOW = EMA(Series, SLOW)
    DIFF = EMAFAST - EMASLOW
    DEA = EMA(DIFF, MID)
    MACD = (DIFF - DEA) * 2
    DICT = {'DIFF': DIFF, 'DEA': DEA, 'MACD': MACD}
    VAR = pd.DataFrame(DICT)
    return VAR

def KDJ(DataFrame, N=9, M1=3, M2=3):
    C = DataFrame['close']
    H = DataFrame['high']
    L = DataFrame['low']

    RSV = (C - LLV(L, N)) / (HHV(H, N) - LLV(L, N)) * 100
    K = SMA(RSV, M1)
    D = SMA(K, M2)
    J = 3 * K - 2 * D
    DICT = {'KDJ_K': K, 'KDJ_D': D, 'KDJ_J': J}
    return pd.DataFrame(DICT)


def BBIBOLL(Series, N1, N2, N3, N4, N, M):  # 多空布林线

    bbiboll = BBI(Series, N1, N2, N3, N4)
    UPER = bbiboll + M * STD(bbiboll, N)
    DOWN = bbiboll - M * STD(bbiboll, N)
    DICT = {'BBIBOLL': bbiboll, 'UPER': UPER, 'DOWN': DOWN}
    VAR = pd.DataFrame(DICT)
    return VAR


def BBI(Series, N1, N2, N3, N4):
    '多空指标'

    bbi = (MA(Series, N1) + MA(Series, N2) +
           MA(Series, N3) + MA(Series, N4)) / 4
    DICT = {'BBI': bbi}
    VAR = pd.DataFrame(DICT)
    return VAR

def BARSLAST(cond, yes=True):
    ncount = len(cond)
    ti_p=c_int * ncount
    np_OUT =ti_p(0)
    na_Cond =np.asarray(cond).astype(np.float32)
    # na_NS=np.asarray(NS).astype(np.int32)
    
    np_S=cast(na_Cond.ctypes.data, POINTER(c_float))
    # np_N=cast(na_NS.ctypes.data, POINTER(c_int))
    
    lib.barslast(ncount, np_OUT, np_S, 0)
    
    return pd.Series(np.asarray(np_OUT), index=cond.index)

    # # return BARLAST(cond, yes)
    # cond2 = cond[cond == yes]
    # if cond2 is None:
    #     return pd.Series(np.zeros(len(cond), dtype = int))
    # else:
    #     # TODO
    #     len_c1 = len(cond)
    #     cond2=cond[cond==yes]
    #     if len(cond2) > 1:
    #         cond3=pd.Series(np.zeros(len_c1, dtype = int))
    #         j = 1
    #         for d in range(cond2.index[0], len(cond3.index)):
    #             if d < cond2.index[j] and d >= cond2.index[j-1]:
    #                 cond3[d] = cond2.index[j-1]
    #             else:
    #                 j += 1
    #                 if j < len(cond2):
    #                     cond3.iloc[d] = cond2.index[j-1]
    #                 else:
    #                     j -= 1
    #                     cond3.iloc[d] = cond2.index[j]
            
    #         # var1 = len_c1 - (len_c1 - cond2.index[-1])
    #         # var2 = np.arange(len_c1) - var1
    #         # var = np.where(var2 < 0, 0, var2)
    #         # var = np.where(cond.index.values-cond2.index[-1]>=0, cond.index.values-cond2.index[-1],cond.index.values-cond2.index[-2] )
    #         var = np.where(cond.index - cond3 > 0, cond.index - cond3, 0)

    #         return pd.Series(var)
            
    #     return pd.Series(np.zeros(len_c1, dtype = int))
    #     # return len(cond) - cond[cond==yes].index[-1]

def BARLAST(cond, yes=True):
    """支持MultiIndex的cond和DateTimeIndex的cond
    条件成立  yes= True 或者 yes=1 根据不同的指标自己定

    Arguments:
        cond {[type]} -- [description]
    """
    if isinstance(cond.index, pd.MultiIndex):
        return len(cond)-cond.index.levels[0].tolist().index(cond[cond != yes].index[-1][0])-1
    elif isinstance(cond.index, pd.DatetimeIndex):
        return len(cond)-cond.index.tolist().index(cond[cond != yes].index[-1])-1


XARROUND =  lambda x,y:np.round(y*(round(x/y-math.floor(x/y)+0.00000000001)+ math.floor(x/y)),2)

def WINNER(Data,Price):
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

def COST(Data, Percent):
    ncount = len(Data)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)

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

def SLOPE(Series, timeperiod=14):
#     Series = Series.fillna(0)
    return talib.LINEARREG_SLOPE(Series, timeperiod)
#     return pd.Series(res, index=Series.index)
    # return pd.Series(res, index=SerLINEARREG_SLOPEies.index)

def INDEX(data, code='000001', type='D'):
    beg_date = data.iloc[0].name[0].strftime("%Y-%m-%d")
    end_date = data.iloc[-1].name[0].strftime("%Y-%m-%d")
    mongo = MongoIo()
    if type == 'D':
        df = mongo.get_index_day(code, beg_date, end_date)
    else:
        df = mongo.get_index_min(code, beg_date, end_date)
    df = df.reset_index()
    df.code = data.iloc[0].name[1]
    df = df.set_index(['date', 'code'])
    return df

def INDEXC(data, code='000001', type='D'):
    return INDEX(data, code, type).close

# def POW(Series, M):
#     return Series.pow(M)

def ATAN(Series):
#     Series = Series.fillna(0)
    return talib.ATAN(Series)
#     return pd.Series(res, index=Series.index)

def EXIST(Series, N):
    return COUNT(Series, N) > 0
    # return res > 0

def CAPITAL(data):
    # code = data.index.levels[1][0]
    code = data.index[0][1]
    dataInfo = __STOCK_INFO(code)
    if len(dataInfo) > 0:
        return dataInfo.liutongguben.values[0] / 100.0
    else:
        return 0

def FINANCE(data, N):
    close = data.close[-1]
    code = data.index[0][1]
    dataInfo = __STOCK_INFO(code)
    if len(data) > 0:
        if N == 40:
            return dataInfo.liutongguben.values[0] * close
        elif N == 7:
            return dataInfo.liutongguben.values[0]
        elif N == 30:
            return dataInfo.liutongguben.values[0] / 100.0
        # return data.liutongguben[0]
    else:
        return 0

def ISLASTBAR(data):
    dl = len(data)
    at = [False] * dl
    at[dl - 1] = True
    return pd.Series(at, index=data.index)

def BIDASKVOL(data, dateStr = None):
    mongo = MongoIo()
    code = data.index[0][1]
    if dateStr == None:
        dateStr = data.index[-1][0].strftime("%Y-%m-%d")
    df = __REALTIME_DATA(code, dateStr)
    if len(df) > 0:
        return df.iloc[-1]['bid1_volume'], df.iloc[-1]['ask1_volume']
    return 0, 0

def BIDASK5VOL(data, dateStr = None):
    mongo = MongoIo()
    code = data.index[0][1]
    if dateStr == None:
        dateStr = data.index[-1][0].strftime("%Y-%m-%d")
    df = __REALTIME_DATA(code, dateStr)
    if len(df) > 0:
        rd = df.iloc[-1]
        bv = rd['bid1_volume'] + rd['bid2_volume'] + rd['bid3_volume'] + rd['bid4_volume'] + rd['bid5_volume']
        sv = rd['ask1_volume'] + rd['ask2_volume'] + rd['ask3_volume'] + rd['ask4_volume'] + rd['ask5_volume']
        return bv, sv
    return 0, 0

def CURBIDASKVOL(data):
    return data['bid1_volume'], data['ask1_volume']

def TURNOVER(data, dateStr = None):
    code = data.index[0][1]
    if dateStr == None:
        dateStr = data.index[-1][0].strftime("%Y-%m-%d")
    df = __REALTIME_DATA(code, dateStr)
    if len(df) > 0:
        return df.iloc[-1]['turnover'], df.iloc[-1]['volume']
    return 0, 0

def BIDVOL(data, dateStr = None):
    code = data.index[0][1]
    if dateStr == None:
        dateStr = data.index[-1][0].strftime("%Y-%m-%d")
    df = __REALTIME_DATA(code, dateStr)
    if len(df) > 0:
        return df.iloc[-1]['bid1_volume']
    return 0

def ASKVOL(data, dateStr = None):
    code = data.index[0][1]
    if dateStr == None:
        dateStr = data.index[-1][0].strftime("%Y-%m-%d")
    df = __REALTIME_DATA(code, dateStr)
    if len(df) > 0:
        return df.iloc[-1]['ask1_volume']
    return 0

def POW(Series, N):
    if N == 2:
        return talib.MULT(Series, Series)
    elif N == 3:
        return talib.MULT(Series, talib.MULT(Series, Series))
    elif N == 4:
        temp = talib.MULT(Series, Series)
        return talib.MULT(temp, temp)
    else:
        return Series.apply(lambda x : math.pow(x, N))

def SQRT(Series):
    return talib.SQRT(Series)

def VALUEWHEN(COND, VALUE):
    ncount = len(COND)
    tf_p = c_float * ncount
    np_OUT = tf_p(0)
    
    na_Cond = np.asarray(COND).astype(np.bool)
    na_VALUE = np.asarray(VALUE).astype(np.float32)
    # na_NS=np.asarray(NS).astype(np.int32)

    np_Cond = cast(na_Cond.ctypes.data, POINTER(c_bool))
    np_Value = cast(na_VALUE.ctypes.data, POINTER(c_float))
    # np_N=cast(na_NS.ctypes.data, POINTER(c_int))
    lib.valueWhen(ncount, np_OUT, np_Cond, np_Value)
    return pd.Series(np.asarray(np_OUT), index=COND.index)