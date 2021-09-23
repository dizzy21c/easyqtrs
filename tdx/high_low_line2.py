#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import re
import struct
from matplotlib import pyplot as plt

# 当前数据存储的路径
BASE_PATH="D:/stockdata/"
RESULT_PATH=BASE_PATH
# 里面存的是股票代码
BASIC_STOCK_FILEPATH=RESULT_PATH+"stock_basic.csv"
#通达信的安装目录
LDAY_PATH_BASE="C:/zd_cjzq/"
LDAY_PATH=LDAY_PATH_BASE+'vipdoc/'
LDAY_PATH_SZ=LDAY_PATH+'sz/lday/'
LDAY_PATH_SH=LDAY_PATH+'sh/lday/'

def get_first_number(s_val):
    """
    获取字符串中第一组数字
    :param s_val:
    :return:
    """
    return re.search(r'(\d+)',s_val,re.I).group()

def tdx_get_fn(ts_code='sh603605'):
    """
    根据股票代码返回通达信lday数据文件名称,6/9开头的为上海，00、30开头的为深圳，其他返回None
    后续读取原始数据文件的内容通过这个文件名称读取
    :param ts_code:
    :return:
    """
    # 如果是6、9开头的为上海的股票，否则为深圳的股票
    if ts_code is None:
        return False
    ts_code = get_first_number(ts_code)
    fn = None
    if ts_code.startswith('6') or ts_code.startswith('9'):
        fn = "{}sh/lday/sh{}.day".format(LDAY_PATH,ts_code)
    if ts_code.startswith('00') or ts_code.startswith('30'):
        fn = "{}sz/lday/sz{}.day".format(LDAY_PATH, ts_code)
    if fn is None:
        return None
    # 检查文件是否存在，如果不存在则返回None
    if os.path.exists(fn):
        return fn
    return None

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
def tdx_read_data_from_file(ts_code=""):
    """
    从通达信的交易软件的日线数据文件lday总读股票行情数据，包括最高/最低/开盘/收盘/成交额/成交量
    注意日期字段是日期类型
    :param fname:
    :return:
    """
    fn = tdx_get_fn(ts_code)
    if fn is None :
        return None
    dataSet=[]
    with open(fn,'rb') as fl:
        buffer=fl.read() #读取数据到缓存，一次性读到内存中
        size=len(buffer) #查看缓存的数据长度
        rowSize=32 #通信达day数据，每32个字节一组数据，即一行数据
        for i in range(0,size,rowSize): #步长为32遍历buffer，即一行一行的处理数据
            row=list( struct.unpack('IIIIIfII',buffer[i:i+rowSize]) ) #这是python的数据结构拆分语法,将指定长度的缓存拆分成一个一个的元素，然后合成一个list
            row[0]=str(row[0]) #第一个是年月日，即20201026的格式的数字，转换为字符串时即为20201026
            row[1]=row[1]/100
            row[2]=row[2]/100
            row[3]=row[3]/100
            row[4]=row[4]/100
            row[5]=row[5]/10000
            row[6]=row[6]/100
            row.pop() #移除最后无意义字段
            row.insert(0,ts_code)
            dataSet.append(row)
    l_dtype={'ts_code':'str'}
    data=pd.DataFrame(data=dataSet,columns=['ts_code','trade_date','open','high','low','close','val','vol'],dtype=float)
    data['prev'] = data['close'].shift(1)
    data.loc[0, 'prev'] = data.loc[0, 'close']
    data['change'] = data['close'] - data['prev']
    data['pctchg'] = round((data['change'] / data['prev']) * 100, 2)
    # 日期转换为YYYY-MM-DD的方式
    data['trade_date'] = pd.to_datetime(data['trade_date'], format='%Y%m%d').apply(lambda x:x.strftime('%Y-%m-%d'))
    return data

def h_l_line(p_df, t=21,period=1000,fn=None):
    """
    根据给定的周期找出最高最低点的日期和数据，然后计算对应的斐波纳契数据
    :param fn: 高低线输出到文件,如果文件参数为None则不输出到文件
    :param p_df:股票交易数据
    :param t:数据周期
    :param period:数据长度
    :return:有效数据点，包括股票代码，日期，高低点周期交易天数、高低点周期自然天数
    """
    if p_df is None or len(p_df)<t:
        return None
    # 获取最新的period条数据
    # df1 = p_df.tail(period).reset_index(drop=True)
    df1 = p_df[['close','high','low','trade_date','ts_code']].copy()
    df1['cv'] = 0 #添加一列为后续保留值准备
    high = df1['high']
    low = df1['low']

    # 保留数据的df
    data = pd.DataFrame([])
    #获取首行为有效的数据点,加入到保留数据框中
    df1.loc[0,'cv'] = df1.iloc[0].high #最高价作为当前价
    first = df1.iloc[0:1]
    data = data.append(first)

    #取第一个日期的最高值作为当前值,开始为0，默认为上涨周期
    ci=0
    cv=df1.iloc[ci].high
    cup=True

    #循环处理每一个周期
    n=0
    lt = t
    while ci<df1.index.max():
        n=n+1
        # 取含当前日期的一个周期的最高和最低价以及索引值,如果出现下一个周期中当前点成为了这个周期的最高和最低点即当前点未变化则
        # 在前周期长度上扩展1个周期,一旦出现拐点则恢复周期。
        # 周期超高了数据长度则结束，当前点加入到数据有效点中。
        # 为什么不是从下一个点找周期，因为下一个点开始的周期则一定存在一个高低点，而这个高低点和当前点的高点或低点比较后一定会
        # 出现一个拐点，有时候不一定有拐点存在,所以要包含当前点
        ih = high[ci:ci+lt].idxmax()
        il = low[ci:ci+lt].idxmin()
        ihv = df1.iloc[ih].high
        ilv = df1.iloc[il].low
        if (ih==ci) & (il==ci):
            #数据结束了吗?如果结束了则直接添加当前数据到数据点和最后一个数据到数据点
            if (ci+lt)>df1.index.max():
                # 数据结束了,最后一个数据是否要添加到数据点中，由循环结束时处理
                break
            else:
                # 三点重叠但数据为结束 , 周期延长重新计算
                lt = lt + t
                continue
        if cup:
            # 上涨阶段
            if (ihv >= cv) & (ci != ih):
                # 如果上升周期中最高价有更新则仍然上涨持续，上涨价格有效，下跌的价格为噪声
                ci = ih
                cv = ihv
                cup = True
            else:
                # 未持续上涨，则下跌价格有效，出现了转折，此时上一个价格成为转折点价格,恢复计算周期
                df1.loc[ci,'cv'] = cv
                data = data.append(df1.iloc[ci:ci + 1])
                ci = il
                cv = ilv
                cup = False
                lt = t
        else:
            # 下跌阶段
            if (ilv<=cv) & (ci != il):
                # 下跌阶段持续创新低，则下跌价格有效，上涨价格为噪声
                ci = il
                cv = ilv
                cup = False
            else:
                # 未持续下跌，此时转为上涨，上涨价格有效，此时上一个价格成为转折点价格,恢复计算周期
                df1.loc[ci, 'cv'] = cv
                data = data.append(df1.iloc[ci:ci + 1])
                ci = ih
                cv = ihv
                cup = True
                lt = t

        # print(df1.iloc[ci:ci+1])
        # print(n,ci,cv,cup,ih,il)

        # if last+t>=df1.index.max():
        #     # 最后计算恰好为最后一个周期，则直接加入最后一个周期进入数据有效点，并且结束循环
        #     last = df1.index.max()
        #     df1.loc[last, 'cv'] = df1.iloc[last].close
        #     data = data.append(df1.iloc[last:last + 1])
        #     break
    #结束了，把当前点加入到数据有效点中
    df1.loc[ci, 'cv'] = cv
    data = data.append(df1.iloc[ci:ci + 1])
    if ci != df1.index.max():
        # 当前点不是最后一个点，则把最后一个点加入到数据点中
        df1.loc[df1.index.max(), 'cv'] = df1.iloc[df1.index.max()].close
        data = data.append(df1.tail(1))

    data = data.reset_index(drop=False)
    # 计算高低点转换的交易日数量即时间周期
    data['period'] = (data['index'] - data['index'].shift(1)).fillna(0)
    # 计算日期的差值,将字符串更改为日期
    trade_date = pd.to_datetime(data['trade_date'],format='%Y-%m-%d')
    days = trade_date - trade_date.shift(1)
    # 填充后转换为实际的天数数字
    days = (days.fillna(pd.Timedelta(0))).apply(lambda x:x.days)
    data['days'] = days
    # 对日期进行转换
    data['trade_date']=trade_date.apply(lambda x:x.strftime('%Y-%m-%d'))
    return data

def h_l_line_png(p_df,ts_code,fn):
    """
    生成图并且保存到指定的文件中，每生成一个图后关闭图形
    :param p_df:
    :param ts_code:
    :param fn:
    :return:
    """
    fig = plt.figure(dpi=100,figsize=(16,9))
    plt.title(ts_code)
    # 坐标轴范围
    # https://www.cnblogs.com/zhizhan/p/5615947.html
    # https://www.cnblogs.com/chaoren399/p/5792168.html
    # plt.axis([0,data['index'].max(),data['cv'].min(),data['cv'].max()])
    plt.xlabel('index')
    plt.ylabel('price')
    # 设置刻度显示的值,显示日期，第一个数组为位置，第二个数组为显示的标签
    plt.xticks(p_df['index'], p_df['trade_date'], rotation=90)
    # 设置y坐标轴的范围
    plt.ylim(p_df['cv'].min()*0.9,p_df['cv'].max()*1.1)
    for idx, row in p_df.iterrows():
        # 绘制指示线
        plt.plot([row['index'], row['index']], [0, row.cv], linestyle="--", linewidth=0.5, color='gray')
        # 注释 https://blog.csdn.net/leaf_zizi/article/details/82886755
        s = "{}({},{})".format(row.cv,row.days,int(row.period))
        plt.annotate(s, xy=(row['index'], row.cv))

    plt.plot(p_df['index'], p_df['cv'])
    plt.savefig(fn)
    # 一定要关闭，否则会消耗完内存
    plt.close(fig)
    # plt.show()

def single_tdx(ts_code,save_path='',save_suffix='high_low_line_'):
    """
    处理单个股票的高低点数据，包含高点的的价格、日期、周期等，保存数据和图到指定的目录下.
    :param save_suffix: 文件名称前缀
    :param save_path: 保存路径
    :param ts_code:
    :return:
    """
    fn = tdx_get_fn(ts_code)
    data = tdx_read_data_from_file(fn)
    # 获取高低点数据
    data = h_l_line(data, 21, 600)
    if data is not None and len(data)>0:
        # 数据保存在D盘下
        fn_png = '{}{}{}.png'.format(save_path,save_suffix, ts_code)
        fn_csv = '{}{}{}.csv'.format(save_path,save_suffix, ts_code)
        # 保存高低点图片
        h_l_line_png(data, ts_code, fn_png)
        # 保存高低点的表格数据
        data.to_csv(fn_csv, index=False)
        print(ts_code,'OK')
        return True
    return False

def all_tdx():
    """
    处理指定目录下的所有股票计算高低价格的点
    含股票的代码、高低点的最高价和最低价，以及日期、前后高低点的自然日周期数和交易日周期数，并且将数据和文件存到指定的目录下
    """
    stocks = pd.read_csv(BASIC_STOCK_FILEPATH, dtype=str)
    for i, row in stocks.iterrows():
        single_tdx(row.ts_code)

if __name__ == "__main__":
    ts_code = '000859'
    single_tdx(ts_code)