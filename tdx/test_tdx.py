#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import os
import re
import struct

import pandas as pd


def tdx_readme():
    return "tdx接口的ts_code要求均为sh600770或sz300171格式,同时日期格式为YYYYMMDD,导出数据的日期格式为YYYY-MM-DD"


# def get_begin_day(df):
#     if df is None or len(df) < 1:
#         return '2010-01-01'
#     max = df['trade_date'].max()
#     max_date = pd.to_datetime(max, format='%Y-%m-%d')
#     begin_date = max_date + dt.timedelta(days=1)
#     return begin_date.strftime('%Y-%m-%d')

def tdx_is_the_format(s_ts_code, p=r"[A-Z]+[0-9]+"):
    """
    检查 ts_code 是否满足 SZ300171这样的格式
    :param p:
    :param s_ts_code:
    :return:
    """
    m = re.match(p, s_ts_code, re.I)
    if m is not None:
        return True
    return False


def tdx_get_fn(p_path: str, ts_code='sh603605'):
    """
    根据股票代码返回通达信lday数据文件名称,6/9开头的为上海，00、30开头的为深圳，其他返回None
    后续读取原始数据文件的内容通过这个文件名称读取
    :param p_path:
    :param ts_code: 证券代码
    :return:
    """
    # 如果是6、9开头的为上海的股票，否则为深圳的股票
    if ts_code is None:
        return False
    fn = None
    if ts_code.startswith('6') or ts_code.startswith('9'):
        fn = "{}sh/lday/sh{}.day".format(p_path, ts_code)
    if ts_code.startswith('00') or ts_code.startswith('30'):
        fn = "{}sz/lday/sz{}.day".format(p_path, ts_code)
    if fn is None:
        return None
    # print(fn)
    # 检查文件是否存在，如果不存在则返回None
    if os.path.exists(fn):
        return fn
    return None


def tdx_get_qfq_fn(p_qfq_path: str, ts_code='sh603605'):
    """
    根据股票代码返回通达信导出的前复权数据文件名称,6/9开头的为上海，00、30开头的为深圳，其他返回None
    后续读取前复权数据文件的内容通过这个文件名称读取
    :param p_qfq_path:
    :param ts_code:可以是000021这样只有股票代码,也可以是000021.SZ这样的股票代码
    :return:
    """
    # 如果是6、9开头的为上海的股票，否则为深圳的股票
    if ts_code is None:
        return False
    fn = None
    # 保证证券代码复合要求
    if tdx_is_the_format(ts_code) is False:
        if ts_code.startswith('6') or ts_code.startswith('9'):
            fn = "{}SH{}.csv".format(p_qfq_path, ts_code)
        elif ts_code.startswith('00') or ts_code.startswith('30'):
            fn = "{}SZ{}.csv".format(p_qfq_path, ts_code)
    else:
        fn = "{}{}.csv".format(p_qfq_path, ts_code.upper())

    # 检查文件是否存在，如果不存在则返回None
    if fn is not None and os.path.exists(fn):
        return fn
    return None


def tdx_get_ts_code(fn):
    """
    根据通达信的文件名称获取通达信的文件名不含.day字符串，根据通达信的交易软件的日线数据目录下的文件名称获取股票代码
    :param fn:
    :return:股票代码
    """
    return os.path.basename(fn).replace('.day', '')


'''
Python实现将通信达.day文件读取为DataFrame
每4个字节为一个字段，每个字段内低字节在前
00 ~ 03 字节：年月日, 整型
04 ~ 07 字节：开盘价*100， 整型
08 ~ 11 字节：最高价*100, 整型
12 ~ 15 字节：最低价*100, 整型
16 ~ 19 字节：收盘价*100, 整型
20 ~ 23 字节：成交额（元），float型
24 ~ 27 字节：成交量（股），整型
28 ~ 31 字节：（保留）
'''


def tdx_read_data_from_file(p_path: str, ts_code=""):
    """
    从通达信的交易软件的日线数据文件lday总读股票行情数据，包括最高/最低/开盘/收盘/成交额/成交量
    注意日期字段是日期类型
    :param p_path:
    :param ts_code:
    :return:
    """
    fn = tdx_get_fn(p_path, ts_code)
    if fn is None:
        return None
    dataSet = []
    with open(fn, 'rb') as fl:
        buffer = fl.read()  # 读取数据到缓存，一次性读到内存中
        size = len(buffer)  # 查看缓存的数据长度
        rowSize = 32  # 通信达day数据，每32个字节一组数据，即一行数据
        for i in range(0, size, rowSize):  # 步长为32遍历buffer，即一行一行的处理数据
            row = list(
                struct.unpack('IIIIIfII', buffer[i:i + rowSize]))  # 这是python的数据结构拆分语法,将指定长度的缓存拆分成一个一个的元素，然后合成一个list
            row[0] = str(row[0])  # 第一个是年月日，即20201026的格式的数字，转换为字符串时即为20201026
            row[1] = row[1] / 100
            row[2] = row[2] / 100
            row[3] = row[3] / 100
            row[4] = row[4] / 100
            row[5] = row[5] / 10000
            row[6] = row[6] / 100
            row.pop()  # 移除最后无意义字段
            row.insert(0, ts_code)
            dataSet.append(row)
    l_dtype = {'ts_code': 'str'}
    data = pd.DataFrame(data=dataSet, columns=['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'val', 'vol'],
                        dtype=float)
    data['prev'] = data['close'].shift(1)
    data.loc[0, 'prev'] = data.loc[0, 'close']
    data['change'] = data['close'] - data['prev']
    data['pctchg'] = round((data['change'] / data['prev']) * 100, 2)
    # 日期转换为YYYY-MM-DD的方式
    data['trade_date'] = pd.to_datetime(data['trade_date'], format='%Y%m%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    return data


def tdx_read_qfq_daily(p_path: str, ts_code):
    """
    根据股票代码读取指定的文件，并且返回数据框，包括股票代码、交易日、开盘价、收盘价、最高价、最低价、成交额、成交量、日涨跌值、涨跌幅
    注意数据为通达信导出的日线数据，注意存放的路径。
    注意日期字段是日期类型
    :param p_path:
    :param ts_code: 不含.SH和.SZ的代码，即纯粹的股票代码(全部为数据)
    :return:数据框或None
    """
    fn = tdx_get_qfq_fn(p_path, ts_code)
    # print('fn',fn)
    if fn is None:
        return None
    ll = []
    with open(fn) as f:
        lines = f.readlines()
    for l in lines:
        ls = l.strip().split(',')
        if len(ls) < 6:
            continue
        ll.append(ls)
    df = pd.DataFrame(ll, columns=['trade_date', 'open', 'high', 'low', 'close', 'vol', 'val'], dtype=float)
    if df is None or len(df) < 1:
        return None
    df['ts_code'] = ts_code
    df['prev'] = df['close'].shift(1)
    df.loc[0, 'prev'] = df.loc[0, 'close']
    df['change'] = df['close'] - df['prev']
    df['pctchg'] = round((df['change'] / df['prev']) * 100, 2)
    # df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d').apply(lambda x:x.strftime('%Y-%m-%d'))
    return df


if __name__ == "__main__":
    print(tdx_get_qfq_fn('test', "000859"))
    print(tdx_get_fn('test', "000859"))
    print(tdx_read_data_from_file('test', "000859"))
    print(tdx_read_qfq_daily('test', "000859"))
