# coding:utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2018-2020 azai/Rgveda/GolemQuant
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
基于 QUANTAXIS 的 DataStruct.add_func 使用，也可以单独使用处理 Kline数据，基于RSRS择时，
RSRS(阻力支撑相对强度)择时策略研究，
聚宽： https://www.joinquant.com/view/community/detail/df07581179e8a3c73e46978cb52d7448?type=best
"""

# 阻力支撑相对强度RSRS是一个强趋势策略，最适合单边牛市，同时具备逃顶能力，能抵抗类似类似15 16年熔断的股灾。

# 详细了解：https://zhuanlan.zhihu.com/p/33501881

# 通过和网格策略的有机结合还可以适应震荡市行情。



import pandas as pd
import os
import datetime
import numpy as np
import statsmodels.formula.api as sml

import matplotlib.pyplot as plt
import scipy.stats as scs
import matplotlib.mlab as mlab

# import statsmodels.api as sm
# from pandas.stats.api import ols
try:
    import QUANTAXIS as QA
    from QUANTAXIS.QAIndicator.talib_numpy import *
except:
    print('PLEASE run "pip install QUANTAXIS" to call these modules')
    pass

import statsmodels.api as sm


def pre_rsrs_data_func(data, N=18, M=252):
    """
    准备数据
    """
    data=data.dropna()
    highs = data.high.values
    lows = data.low.values
    start_t = datetime.datetime.now()
    print(start_t)

    # 斜率
    data['beta'] = 0
    data['R2'] = 0
    beta_rsquared = np.zeros((len(data), 2), )

    for i in range(len(highs))[N:]:
        data_high = highs[i - N:i]
        data_low = lows[i - N:i]
        X = sm.add_constant(data_low)
        model = sm.OLS(data_high, X)
        results = model.fit()

        # beta = low
        if (len(results.params) > 1):
            beta_rsquared[i, 0] = results.params[1]
        else:
            beta_rsquared[i, 0] = results.params[0]
        beta_rsquared[i, 1] = results.rsquared

    data[['beta', 'R2']] = beta_rsquared

    # 日收益率
    data['ret'] = data.close.pct_change(1)

    # 标准分
    # data['beta_norm'] = data['beta'].rolling(M).apply(lambda x: scs.zscore(x.values)[-1])
    data['beta_norm'] = data['beta'].rolling(M).apply(lambda x: scs.zscore(x)[-1])

    beta = data.columns.get_loc('beta')
    beta_norm = data.columns.get_loc('beta_norm')
    data.iloc[:min(M, len(highs)), beta_norm] = scs.zscore(data.iloc[:min(M, len(highs)), beta].values)
    data['RSRS_R2'] = data.beta_norm * data.R2
    data = data.fillna(0)

    # 右偏标准分
    data['beta_right'] = data.RSRS_R2 * data.beta

    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))
    return data


def pre_rsrs_data_v1_func(data, N=18, M=252):
    """
    准备数据
    """
    highs = data.high
    start_t = datetime.datetime.now()
    print(start_t)

    # 斜率
    data['beta'] = 0
    data['R2'] = 0
    beta_rsquared = np.zeros((len(data), 2), )

    for i in range(N - 1, len(highs) - 1):
        # for i in range(len(highs))[N:]:
        df_ne = data.iloc[i - N + 1:i + 1, :]
        model = sml.ols(formula='high~low', data=df_ne)
        result = model.fit()

        # beta = low
        beta_rsquared[i + 1, 0] = result.params[1]
        beta_rsquared[i + 1, 1] = result.rsquared

    data[['beta', 'R2']] = beta_rsquared

    # 日收益率
    data['ret'] = data.close.pct_change(1)

    # 标准分
    data['beta_norm'] = (data['beta'] - data.beta.rolling(M).mean().shift(1)) / data.beta.rolling(M).std().shift(1)

    beta_norm = data.columns.get_loc('beta_norm')
    beta = data.columns.get_loc('beta')
    for i in range(min(M, len(highs))):
        data.iat[i, beta_norm] = (data.iat[i, beta] - data.iloc[:i - 1, beta].mean()) / data.iloc[:i - 1,
                                                                                        beta].std() if (
                    data.iloc[:i - 1, beta].std() != 0) else np.nan

    data.iat[2, beta_norm] = 0
    data['RSRS_R2'] = data.beta_norm * data.R2
    data = data.fillna(0)

    # 右偏标准分
    data['beta_right'] = data.RSRS_R2 * data.beta
    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))
    return data


def pre_rsrs_data_v2_func(data, N=18, M=252):
    """
    准备数据
    """
    highs = data.high

    # 斜率
    data['beta'] = 0
    data['R2'] = 0
    beta_rsquared = np.zeros((len(data), 2), )

    for i in range(N - 1, len(highs) - 1):
        # for i in range(len(highs))[N:]:
        df_ne = data.iloc[i - N + 1:i + 1, :]
        model = sml.ols(formula='high~low', data=df_ne)
        result = model.fit()

        # beta = low
        beta_rsquared[i + 1, 0] = result.params[1]
        beta_rsquared[i + 1, 1] = result.rsquared

    data[['beta', 'R2']] = beta_rsquared

    # 日收益率
    data['ret'] = data.close.pct_change(1)

    # 标准分
    # data['beta_norm'] = (data['beta'] - data.beta.rolling(M).mean().shift(1))
    # / data.beta.rolling(M).std().shift(1)
    # data['beta_norm'] = data['beta'].rolling(M).apply(lambda x: scs.zscore(x.values)[-1])
    data['beta_norm'] = data['beta'].rolling(M).apply(lambda x: scs.zscore(x)[-1])

    beta = data.columns.get_loc('beta')
    beta_norm = data.columns.get_loc('beta_norm')
    data.iloc[:min(M, len(highs)), beta_norm] = scs.zscore(data.iloc[:min(M, len(highs)), beta].values)
    # beta_norm = data.columns.get_loc('beta_norm')
    # beta = data.columns.get_loc('beta')
    # for i in range(min(M, len(highs))):
    # data.iat[i, beta_norm] = (data.iat[i, beta] - data.iloc[:i - 1,
    # beta].mean()) / data.iloc[:i - 1, beta].std() if (data.iloc[:i - 1,
    # beta].std() != 0) else np.nan

    # data.iat[2, beta_norm] = 0
    data['RSRS_R2'] = data.beta_norm * data.R2
    data = data.fillna(0)

    # 右偏标准分
    data['beta_right'] = data.RSRS_R2 * data.beta

    return data


def RSRS1(price, S1=1.0, S2=0.8):
    """
    斜率指标交易策略标准分策略
    """
    data = price.copy()
    data['flag'] = 0  # 买卖标记
    data['position'] = 0  # 持仓标记

    beta = data.columns.get_loc('beta')
    flag = data.columns.get_loc('flag')
    position_col = data.columns.get_loc('position')

    position = 0  # 是否持仓，持仓：1，不持仓：0
    for i in range(1, data.shape[0] - 1):
        # 开仓
        if data.iat[i, beta] > S1 and position == 0:
            data.iat[i, flag] = 1
            data.iat[i + 1, position_col] = 1
            position = 1

        # 平仓
        elif data.iat[i, beta] < S2 and position == 1:
            data.iat[i, flag] = -1
            data.iat[i + 1, position_col] = 0
            position = 0

        # 保持
        else:
            data.iat[i + 1, position_col] = data.iat[i, position_col]

    data['nav'] = (1 + data.close.pct_change(1).fillna(0) * data.position).cumprod()

    return (data)


def RSRS2(price,
          S=0.7):
    """
    标准分策略
    """
    data = price.copy()
    data['flag'] = 0  # 买卖标记
    data['position'] = 0  # 持仓标记

    beta_norm = data.columns.get_loc('beta_norm')
    flag = data.columns.get_loc('flag')
    position_col = data.columns.get_loc('position')

    position = 0  # 是否持仓，持仓：1，不持仓：0
    for i in range(1, data.shape[0] - 1):
        # 开仓
        if data.iat[i, beta_norm] > S and position == 0:
            data.iat[i, flag] = 1
            data.iat[i + 1, position_col] = 1
            position = 1
        # 平仓
        elif data.iat[i, beta_norm] < -S and position == 1:
            data.iat[i, flag] = -1
            data.iat[i + 1, position_col] = 0
            position = 0

        # 保持
        else:
            data.iat[i + 1, position_col] = data.iat[i, position_col]

    data['nav'] = (1 + data.close.pct_change(1).fillna(0) * data.position).cumprod()

    return (data)


def RSRS3(HS300, S=0.7):
    """
    修正标准分策略
    """
    data = HS300.copy()
    data['flag'] = 0  # 买卖标记
    data['position'] = 0  # 持仓标记

    RSRS_R2 = data.columns.get_loc('RSRS_R2')
    flag = data.columns.get_loc('flag')
    position_col = data.columns.get_loc('position')

    position = 0  # 是否持仓，持仓：1，不持仓：0
    for i in range(1, data.shape[0] - 1):
        # 开仓
        if data.iat[i, RSRS_R2] > S and position == 0:
            data.iat[i, flag] = 1
            data.iat[i + 1, position_col] = 1
            position = 1
        # 平仓
        elif data.iat[i, RSRS_R2] < -S and position == 1:
            data.iat[i, flag] = -1
            data.iat[i + 1, position_col] = 0
            position = 0
        # 保持
        else:
            data.iat[i + 1, position_col] = data.iat[i, position_col]

    data['nav'] = (1 + data.close.pct_change(1).fillna(0) * data.position).cumprod()

    return (data)


def RSRS4(price,
          S=0.7):
    """
    #右偏标准分策略
    """
    data = price.copy()
    data['flag'] = 0  # 买卖标记
    data['position'] = 0  # 持仓标记

    beta_right = data.columns.get_loc('beta_right')
    flag = data.columns.get_loc('flag')
    position_col = data.columns.get_loc('position')

    position = 0  # 是否持仓，持仓：1，不持仓：0
    for i in range(1, data.shape[0] - 1):

        # 开仓
        if data.iat[i, beta_right] > S and position == 0:
            data.iat[i, flag] = 1
            data.iat[i + 1, position_col] = 1
            position = 1
        # 平仓
        elif data.iat[i, beta_right] < -S and position == 1:
            data.iat[i, flag] = -1
            data.iat[i + 1, position_col] = 0
            position = 0

        # 保持
        else:
            data.iat[i + 1, position_col] = data.iat[i, position_col]

    data['nav'] = (1 + data.close.pct_change(1).fillna(0) * data.position).cumprod()

    return (data)


if __name__ == '__main__':
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    codelist = ['512690', '510900', '513100', '510300',
                '512980', '512170', '515000', '512800',
                '159941', '159994', '515050', '159920',
                '159952', '159987', '159805', '159997',
                '159919', ]

    codelist = ['510300']

    # 获取ETF/股票中文名称，只是为了看得方便，交易策略并不需要ETF/股票中文名称
    # stock_names = QA.QA_fetch_etf_name(codelist)
    # codename = [stock_names.at[code, 'name'] for code in codelist]

    ## 读取 ETF基金 日线，存在index_day中
    # data_day = QA.QA_fetch_index_day_adv(codelist,
    #    start='2010-01-01',
    #    end='{}'.format(datetime.date.today()))

    # codelist = ['600519']
    # codelist = ['600239']
    # codelist = ['600338']
    # codelist = ['000671']
    # codelist = ['600095','600822','600183']
    codelist = ['600718']
    # 获取股票中文名称，只是为了看得方便，交易策略并不需要股票中文名称
    stock_names = QA.QA_fetch_stock_name(codelist)
    codename = [stock_names.at[code, 'name'] for code in codelist]

    data_day = QA.QA_fetch_stock_day_adv(codelist,
                                         '2008-01-01',
                                         '{}'.format(datetime.date.today(), )) #.to_qfq()

    indices_rsrsT = data_day.add_func(pre_rsrs_data_v2_func)
    resultT = RSRS1(indices_rsrsT)
    num = resultT.flag.abs().sum() / 2
    nav = resultT.nav[resultT.shape[0] - 1]
    print('RSRS1_T 交易次数 = ', num)
    print('策略净值为= ', nav)

    resultT2 = RSRS2(indices_rsrsT)
    num = resultT2.flag.abs().sum() / 2
    nav = resultT2.nav[resultT2.shape[0] - 1]
    ret_year = (nav - 1)
    print('RSRS2_T 交易次数 = ', num)
    print('策略净值为= ', nav)

    resultT3 = RSRS3(indices_rsrsT)
    num = resultT3.flag.abs().sum() / 2
    nav = resultT3.nav[resultT.shape[0] - 1]
    ret_year = (nav - 1)
    print('RSRS3_T 交易次数 = ', num)
    print('策略净值为= ', nav)

    resultT4 = RSRS4(indices_rsrsT)
    num = resultT4.flag.abs().sum() / 2
    nav = resultT4.nav[resultT.shape[0] - 1]
    ret_year = (nav - 1)
    print('RSRS4_T 交易次数 = ', num)
    print('策略净值为= ', nav)

    indices_rsrs = data_day.add_func(pre_rsrs_data_func)
    result = RSRS1(indices_rsrs)
    print(indices_rsrs)

    ##斜率数据分布
    # plt.figure(figsize=(15,5))
    # plt.hist(indices['beta'], bins= 100, range= None, normed= False, weights=
    # None, cumulative= False,
    #         bottom= None, histtype= 'bar', align= 'mid', orientation=
    #         'vertical', rwidth= None, log= False, color= 'g',
    #         label='直方图', stacked= False)

    ##RSRS标准分和右偏变准分分布
    # plt.figure(figsize=(15,5))
    # plt.hist(indices['beta_norm'], bins= 100, range= None, normed= False,
    # weights= None, cumulative= False,
    #         bottom= None, histtype= 'bar', align= 'mid', orientation=
    #         'vertical', rwidth= None, log= False, color= 'g',
    #         label='直方图', stacked= False)

    # plt.figure(figsize=(15,5))
    # plt.hist(indices['RSRS_R2'], bins= 100, range= None, normed= False,
    # weights= None, cumulative= False,
    #         bottom= None, histtype= 'bar', align= 'mid', orientation=
    #         'vertical', rwidth= None, log= False, color= 'g',
    #         label='直方图', stacked= False)
    # plt.show()

    num = result.flag.abs().sum() / 2
    nav = result.nav[result.shape[0] - 1]
    print('RSRS1 交易次数 = ', num)
    print('策略净值为= ', nav)
    print(result[['close', 'ret', 'beta', 'R2', 'beta_norm', 'RSRS_R2', 'flag', 'position', 'nav']].tail(50))

    result2 = RSRS2(indices_rsrs)
    num = result2.flag.abs().sum() / 2
    nav = result2.nav[result.shape[0] - 1]
    ret_year = (nav - 1)
    print('RSRS2 交易次数 = ', num)
    print('策略净值为= ', nav)

    result3 = RSRS3(indices_rsrs)
    num = result3.flag.abs().sum() / 2
    nav = result3.nav[result.shape[0] - 1]
    ret_year = (nav - 1)
    print('RSRS3 交易次数 = ', num)
    print('策略净值为= ', nav)

    result4 = RSRS4(indices_rsrs)
    num = result4.flag.abs().sum() / 2
    nav = result4.nav[result.shape[0] - 1]
    ret_year = (nav - 1)
    print('RSRS4 交易次数 = ', num)
    print('策略净值为= ', nav)

    # xtick = np.arange(0,result.shape[0],int(result.shape[0] / 7))
    # xticklabel = pd.Series(result.index.date[xtick])
    xticklabel = result.index.get_level_values(level=0).to_series().apply(lambda x: x.strftime("%Y-%m-%d")[2:16])

    plt.figure(figsize=(15, 3))
    fig = plt.axes()
    plt.plot(np.arange(result.shape[0]), result.nav, label='RSRS1', linewidth=2)
    plt.plot(np.arange(result.shape[0]), result2.nav, label='RSRS2', linewidth=2)
    plt.plot(np.arange(result.shape[0]), result3.nav, label='RSRS3', linewidth=2)
    plt.plot(np.arange(result.shape[0]), result4.nav, label='RSRS4', linewidth=2)
    plt.plot(np.arange(result.shape[0]), indices_rsrs.close / indices_rsrs.close[0], label=codelist[0], linewidth=2)

    fig.set_xticks(range(0, len(xticklabel),
                         round(len(xticklabel) / 12)))
    fig.set_xticklabels(xticklabel[::round(len(xticklabel) / 12)],
                        rotation=45)
    # plt.legend()
    # plt.show()