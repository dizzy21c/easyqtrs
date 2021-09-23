import pandas as pd
import os
import datetime
import numpy as np 
import statsmodels.formula.api as sml
import QUANTAXIS as QA

import matplotlib.pyplot as plt
import scipy.stats as scs
import matplotlib.mlab as mlab
from easyquant.indicator.base import *
import sys, getopt
import json
from easyquant import MongoIo
import statsmodels.api as sm
from multiprocessing import Process, Pool, cpu_count, Manager
from multiprocessing import Process, Pool, cpu_count, Manager
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed

from func.tdx_func import *
executor = ThreadPoolExecutor(max_workers=cpu_count() * 2)
executor_func = ProcessPoolExecutor(max_workers=cpu_count() * 2)
executorN = ProcessPoolExecutor(max_workers=cpu_count())

mongo = MongoIo()

databuf_mongo = Manager().dict()
databuf_tdxfunc = Manager().dict()
databuf_hold = Manager().dict()
max_buy_nums = 5
max_hold_days = 20
pool_size = cpu_count()

# print("pool size=%d" % pool_size)
def tdx_base_func(code, data, func_name, mongo_np, st_start, code_list = None):
    """
    准备数据
    """
    try:
        # tdx_func_result, next_buy = tdx_dhmcl(data)
        # tdx_func_result, next_buy = tdx_hm(data)
        # tdx_func_result, next_buy = tdx_sxp(data)
        # tdx_func_result, next_buy = tdx_A01(data)
        # tdx_func_result, next_buy = tdx_nmddl(data)
        # print(func_name)
        # tdx_func_result, next_buy = tdx_fscd(data)
        # tdx_func_result, next_buy = tdx_swl(data)
        tdx_func_result, tdx_func_result2, next_buy = eval(func_name)(data)
    # 斜率
    except:
        tdx_func_result, tdx_func_result2, next_buy = 0, 0, False

    data = data.copy()
    # data['bflg'] = IF(REF(后炮,1) > 0, 1, 0)
    data['bflg'] = tdx_func_result
    data['sflg'] = tdx_func_result2
    # print("code=%s, bflg=%s" % (code, data['bflg'].iloc[-1]))
    # data['beta'] = 0
    # data['R2'] = 0
    # beta_rsquared = np.zeros((len(data), 2),)
    #
    # for i in range(N - 1, len(highs) - 1):
    # #for i in range(len(highs))[N:]:
    #     df_ne = data.iloc[i - N + 1:i + 1, :]
    #     model = sml.ols(formula='high~low', data = df_ne)
    #     result = model.fit()
    #
    #     # beta = low
    #     beta_rsquared[i + 1, 0] = result.params[1]
    #     beta_rsquared[i + 1, 1] = result.rsquared
    #
    # data[['beta', 'R2']] = beta_rsquared

    # 日收益率
    data['ret'] = data.close.pct_change(1)

    # 标准分
    # data['beta_norm'] = (data['beta'] - data.beta.rolling(M).mean().shift(1)) / data.beta.rolling(M).std().shift(1)
    #
    # beta_norm = data.columns.get_loc('beta_norm')
    # beta = data.columns.get_loc('beta')
    # for i in range(min(M, len(highs))):
    #     data.iat[i, beta_norm] = (data.iat[i, beta] - data.iloc[:i - 1, beta].mean()) / data.iloc[:i - 1, beta].std() if (data.iloc[:i - 1, beta].std() != 0) else np.nan

    # data.iat[2, beta_norm] = 0
    # data['RSRS_R2'] = data.beta_norm * data.R2
    # data = data.fillna(0)
    #
    # # 右偏标准分
    # data['beta_right'] = data.RSRS_R2 * data.beta
    # if code == '002003':
    #     print(data.tail(22))
    # print(data)
    dataN = data.query("date >= '%s'" % st_start).copy()
    # print(st_start, dataN.head())
    return do_buy_sell_fun(mongo_np, func_name, code, dataN, next_buy = next_buy)
    # return data

def tdx_func(datam, func_name, st_start, code_list = None):
    """
    准备数据
    """
    # highs = data.high
    start_t = datetime.datetime.now()
    print("begin-tdx_func:", start_t)
    mongo_np = MongoIo()
    dataR = pd.DataFrame()
    if code_list is None:
        code_list = datam.index.levels[1]
    for code in code_list:
        data=datam.query("code=='%s'" % code)
        data = tdx_base_func(code, data, func_name, mongo_np, st_start)
        if len(dataR) == 0:
            dataR = data
        else:
            dataR = dataR.append(data)
    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func spent:{}'.format((end_t - start_t)))
    print("tdx-fun-result-len", len(dataR))
    return dataR.sort_index()

def tdx_func_mp(func_name, st_start):
    start_t = datetime.datetime.now()
    print("begin-tdx_func_mp :", start_t)
    task_list = []
    # pool = Pool(cpu_count())
    for key in range(pool_size):
        # tdx_func(databuf_mongo[key])
        task_list.append(executor_func.submit(tdx_func, databuf_mongo[key], func_name, st_start))
    # pool.close()
    # pool.join()

    # todo begin
    dataR = pd.DataFrame()
    # for i in range(pool_size):
    #     if len(dataR) == 0:
    #         dataR = databuf_tdxfunc[i]
    #     else:
    #         dataR = dataR.append(databuf_tdxfunc[i])
    #     # print(len(dataR))
    for task in as_completed(task_list):
        if len(dataR) == 0:
            dataR = task.result()
        else:
            dataR = dataR.append(task.result())

    dataR.sort_index()
    # todo end


    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func_mp spent:{}'.format((end_t - start_t)))

    return dataR
def buy_sell_fun(datam, code, S1=1.0, S2=0.8):
    """
    斜率指标交易策略标准分策略
    """
    price = datam.query("code=='%s'" % code)
    # data = price.copy()
    data = price.copy()
    return do_buy_sell_fun(code, data)

def buy_action(mongo_np, func_name, code, data, next_buy, col_pos_tup, i):
    (flag_col, position_col, hold_price_col, close_col, open_col) = col_pos_tup
    if next_buy:
        if i == len(data) - 1:
            return 0, 0
        # 去除开盘涨停跌停
        if data.iat[i+1, open_col] / data.iat[i, close_col] > 1.095 \
                or data.iat[i+1, open_col] / data.iat[i, close_col] < 0.88:
            return 0, 0
        dateObj = data.iloc[i+1].name[0]
        nowPrice = data.iat[i+1, close_col]
        _profi = mongo_np.upd_order(func_name, dateObj, code, nowPrice)

        data.iat[i + 1, flag_col] = 1
        data.iat[i + 1, position_col] = 1
        data.iat[i + 1, hold_price_col] = data.iat[i+1, open_col]
        print("buy  : date=%s code=%s price=%.2f" % (dateObj, code, nowPrice))
        if i < len(data) - 2:
            data.iat[i + 2, position_col] = 1
            data.iat[i + 2, hold_price_col] = data.iat[i + 1, hold_price_col]
    else:
        # 去除涨停/跌停
        if data.iat[i, close_col] / data.iat[i - 1, close_col] > 1.095 \
                or data.iat[i, close_col] / data.iat[i - 1, close_col] < 0.88:
            return 0, 0
        dateObj = data.iloc[i].name[0]
        nowPrice = data.iat[i, close_col]
        _profi = mongo_np.upd_order(func_name, dateObj, code, nowPrice)

        data.iat[i, flag_col] = 1
        data.iat[i, position_col] = 1
        data.iat[i, hold_price_col] = data.iat[i, close_col]
        print("buy  : date=%s code=%s price=%.2f" % (dateObj, code, nowPrice))
        if i < len(data) - 1:
            data.iat[i + 1, position_col] = 1
            data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]
    # position = 1
    position = 1
    hdays = 0
    return position, hdays

def sell_action(mongo_np, func_name, code, data, col_pos_tup, i, sell_pct):
    (flag_col, position_col, hold_price_col, win_flg_col, sell_flg_col, close_col) = col_pos_tup
    data.iat[i, flag_col] = -1
    data.iat[i, sell_flg_col] = 1
    close_price = data.iat[i, close_col]
    hold_price = data.iat[i, hold_price_col]
    if close_price > hold_price * 1.01:
        data.iat[i, win_flg_col] = 1
    data.iat[i + 1, position_col] = 0
    data.iat[i + 1, hold_price_col] = 0
    # print("sell 60 : date=%s code=%s  price=%.2f, hold-price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], close_price, hold_price))
    # logout_out(data, 1, i, sell_pct)
    dateObj = data.iloc[i].name[0]
    nowPrice = data.iat[i, close_col]
    profi = mongo_np.upd_sell_order(func_name, code, nowPrice, dateObj)

    print("pct=%.2f, sell : date=%s code=%s  price=%.2f hold-price=%.2f" %
          (profi, data.iloc[i].name[0], data.iloc[i].name[1], close_price, hold_price))
    # 持仓标记
    position = 0
    # 盈亏标记
    sflg = 0
    return position, sflg

def do_buy_sell_fun(mongo_np, func_name, code, data, next_buy = False, S1=1.0, S2=0.8):
    """
    斜率指标交易策略标准分策略
    """
    # price = datam.query("code=='%s'" % code)
    # # data = price.copy()
    # data = price.copy()
    data['flag'] = 0 # 买卖标记
    data['position'] = 0 # 持仓标记
    data['hold_price'] = 0.0  # 持仓价格
    data['sell_close'] = data['close']  # 卖出价格
    data['win_flg'] = 0  # 盈利标记
    data['sell_flg'] = 0  # 盈利标记
    bflag = data.columns.get_loc('bflg')
    sflag = data.columns.get_loc('sflg')
    # beta = data.columns.get_loc('beta')
    flag_col = data.columns.get_loc('flag')
    position_col = data.columns.get_loc('position')
    close_col = data.columns.get_loc('close')
    sell_close_col = data.columns.get_loc('sell_close')
    high_col = data.columns.get_loc('high')
    low_col = data.columns.get_loc('low')
    open_col = data.columns.get_loc('open')
    hold_price_col = data.columns.get_loc('hold_price')
    win_flg_col = data.columns.get_loc('win_flg')
    sell_flg_col = data.columns.get_loc('sell_flg')
    position = 0 # 是否持仓，持仓：1，不持仓：0
    sflg = 0
    hdays = 0
    for i in range(1,data.shape[0] - 1):
        # 开仓
        # print("do_buy_sell_fun=", data.iat[i, bflag])
        if position > 0:
            hdays = hdays + 1
        else:
            hdays = 0
        if data.iat[i, bflag] > 0 and position == 0:
            # print("do_buy_sell_fun=", data.iat[i, bflag])
            sflg = 0
            # 涨停不能买入
            # if data.iat[i+1,open_col] < data.iat[i,close_col] * 1.092\
            #         and data.iat[i+1,open_col] > data.iat[i,close_col] * 1.02\
            #     and buy_ctl_check(data.iloc[i].name[0], buy_ctl_dict, share_lock):
            # if data.iat[i+1,open_col] > data.iat[i,close_col] * 1.07:

            # # 去除一字板
            # if data.iat[i, high_col] > data.iat[i, low_col] \
            #         and buy_ctl_check(data.iloc[i].name[0], buy_ctl_dict, share_lock):
            # 去除涨停
            # if data.iat[i, close_col] / data.iat[i - 1, close_col] < 1.095:
            position, hdays = buy_action(mongo_np, func_name, code, data, next_buy, (flag_col, position_col, hold_price_col, close_col, open_col), i)
            # else:
            #     # data.iat[i, position_col] = 0
            #     data.iat[i + 1, position_col] = data.iat[i, position_col]
            #     data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]
                # pass
        # 平仓
        elif data.iat[i, sflag] > 0 and position == 1:
            # cprice = data.iat[i, close_col]
            # hold_price = data.iat[i, hold_price_col]
            sell_action_param = (flag_col, position_col, hold_price_col, win_flg_col, sell_flg_col, close_col)
            position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 999)
        # elif data.iat[i, bflag] == S2 and position == 1:
        elif data.iat[i, sflag] == -1 and data.iat[i, position_col] > 0 and position == 1:
            cprice = data.iat[i, close_col]
            hold_price = data.iat[i, hold_price_col]
            if cprice < hold_price * 0.93:# or oprice < hold_price * 0.95:
                sflg = -1
            elif cprice > hold_price * 1.1 and sflg <= 0:
                sflg = 1
                high_price = data.iat[i, high_col]
            elif cprice > hold_price * 1.2 and sflg < 2:
                sflg = 2
                high_price = data.iat[i, high_col]
            elif cprice > hold_price * 1.3 and sflg < 3:
                sflg = 3
                high_price = data.iat[i, high_col]
            elif cprice > hold_price * 1.4 and sflg < 4:
                sflg = 4
                high_price = data.iat[i, high_col]
            elif cprice > hold_price * 1.5 and sflg < 5:
                sflg = 5
                high_price = data.iat[i, high_col]
            elif cprice > hold_price * 1.6 and sflg < 6:
                sflg = 6
                high_price = data.iat[i, high_col]
            elif cprice > hold_price * 1.7 and sflg < 7:
                sflg = 7
                high_price = data.iat[i, high_col]
            elif cprice > hold_price * 1.8 and sflg < 8:
                sflg = 8
                high_price = data.iat[i, high_col]
            elif cprice > hold_price * 1.9 and sflg < 9:
                sflg = 9
                high_price = data.iat[i, high_col]
            sell_action_param = (flag_col, position_col, hold_price_col, win_flg_col, sell_flg_col, close_col)
            if sflg < 0:# or cprice > hprice * 1.2:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, -5)
            elif sflg == 9 and high_price / cprice > 1.15:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 90)
            elif sflg == 8 and high_price / cprice > 1.12:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 80)
            elif sflg == 7 and high_price / cprice > 1.1:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 70)
            elif sflg == 6 and high_price / cprice > 1.1:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 60)
            elif sflg == 5 and high_price / cprice > 1.09:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 50)
            elif sflg == 4 and high_price / cprice > 1.08:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 40)
            elif sflg == 3 and high_price / cprice > 1.06:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 30)
            elif sflg == 2 and high_price / cprice > 1.05:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 20)
            elif sflg == 1 and high_price / cprice > 1.04:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 10)
            elif sflg == 0 and hdays > max_hold_days:
                position, sflg = sell_action(mongo_np, func_name, code, data, sell_action_param, i, 0)
            else:
                data.iat[i + 1, position_col] = data.iat[i, position_col]
                data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]

        # 保持
        else:
            data.iat[i + 1, position_col] = data.iat[i, position_col]
            data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]

    data['nav'] = (1+data.close.pct_change(1).fillna(0) * data.position).cumprod() - 1

    # if code == '002003':
    #     data.to_csv("%s.csv" % code)

    return data

def backtest(indices_DataFrame):
    start_t = datetime.datetime.now()
    print("begin-backtest:", start_t)
    result01 = indices_DataFrame['close'].groupby(level=['date']).count()
    dataR = pd.DataFrame()
    print("index-len:", len(result01.index))
    for x in result01.index:
        # print(x)
        df_prices = indices_DataFrame.query("date=='%s'" % x)
        # print(x, len(df_prices))
        task_list = []
        for x in df_prices.index:
            print(df_prices.loc[x].name[0])
            row_data = df_prices.loc[x]
            code="***"
            task_list.append(executor.submit(do_buy_sell_fun, code, row_data, x))
        # data = price.copy()
        # data = price.copy()
        # codes =
        start_t = datetime.datetime.now()
        print("begin-backtest:", start_t)
        for task in as_completed(task_list):
            if len(dataR) == 0:
                dataR = task.result()
            else:
                dataR = dataR.append(task.result())
        end_t = datetime.datetime.now()
        print(end_t, 'buy_sell_fun_mp-02 spent:{}'.format((end_t - start_t)))

        print(dataR)
        break

    end_t = datetime.datetime.now()
    print(end_t, 'backtest spent:{}'.format((end_t - start_t)))

def summary(func_name, st_start, st_end, datam, S1=1.0, S2=0.8):
    start_t = datetime.datetime.now()
    print("begin-buy_sell_fun_mp-01:", start_t)
    # datam.to_csv("datam.csv")
    # print(datam.tail(50))
    datam.sort_index()
    # print(datam.head())
    result01 = datam['nav'].groupby(level=['date']).sum()
    # result02 = datam['nav'].groupby(level=['date']).count()
    result02 = datam['position'].groupby(level=['date']).sum()
    win_num = datam['win_flg'].sum()
    sell_num = datam['sell_flg'].sum()
    # result02.to_csv("result02.csv")
    for i in range(len(result02)):
        if result02[i] <= 0:
            result02[i] = 1
        if i > 0:
            if result02[i] < result02[i - 1]:
                result02.iloc[i] = result02.iloc[i - 1]
    print(result02.tail(10))
    num = datam.flag.abs().sum()
    # dataR = pd.DataFrame({'nav':result01 - result02 + 1,'flag':0})
    dataR = pd.DataFrame({'nav': 1 + result01 / result02, 'flag': 0, 'pos':result02})
    # dataR2['flag'] = 0
    dataR.iat[-1,1] = num
    # result['nav'] = result['nav']  - len(datam.index.levels[1]) + 1

    num = dataR.flag.abs().sum() / 2
    nav = dataR.nav[dataR.shape[0] - 1]
    # print(resultT.tail(300))
    # resultT.to_csv("resultT.csv")
    # mnav = min(dataR.nav)
    max_dropback = round(float(max([(dataR.nav.iloc[idx] - dataR.nav.iloc[idx::].min()) / dataR.nav.iloc[idx] for idx in range(len(dataR.nav))])),2)
    # max_dropback = 0
    print('策略名称 = %s, begin=%s, end=%s' % (func_name, st_start, st_end))
    print('交易次数 = %d' %(num))
    print('完成交易次数 = %d, 胜数=%d , 胜率=%.3f' % (sell_num, win_num, win_num / sell_num * 100))
    print('策略净值为= %.2f 最大回撤 %.2f ' % ((nav - 1) * 100, max_dropback * 100))
    return dataR

def buy_sell_fun_mp_new(datam, S1=1.0, S2=0.8):
    """
    斜率指标交易策略标准分策略
    """
    # dataR = pd.DataFrame()
    start_t = datetime.datetime.now()
    print("begin-buy_sell_fun_mp-01:", start_t)
    task_list = []
    for code in datam.index.levels[1]:
        # data = price.copy()
        # price = datam.query("code=='%s'" % code)
        # data = price.copy()
        # data = buy_sell_fun(data)
        task_list.append(executor.submit(buy_sell_fun, datam, code))
        # if code == '000732':
        #     print(data.tail(22))
        # if len(dataR) == 0:
        #     dataR = data
        # else:
        #     dataR = dataR.append(data)
    end_t = datetime.datetime.now()
    print(end_t, 'buy_sell_fun_mp-01 spent:{}'.format((end_t - start_t)))

    dataR = pd.DataFrame()
    start_t = datetime.datetime.now()
    print("begin-buy_sell_fun_mp-02:", start_t)
    for task in as_completed(task_list):
        if len(dataR) == 0:
            dataR = task.result()
        else:
            dataR = dataR.append(task.result())
    end_t = datetime.datetime.now()
    print(end_t, 'buy_sell_fun_mp-02 spent:{}'.format((end_t - start_t)))

    result01 = dataR['nav'].groupby(level=['date']).sum()
    result02 = dataR['nav'].groupby(level=['date']).count()

    num = dataR.flag.abs().sum()
    dataR2 = pd.DataFrame({'nav':result01 - result02 + 1,'flag':0})
    # dataR2['flag'] = 0
    dataR2.iat[-1,1] = num
    # result['nav'] = result['nav']  - len(datam.index.levels[1]) + 1
    return dataR2

def buy_sell_fun_mp_org(datam, S1=1.0, S2=0.8):
    """
    斜率指标交易策略标准分策略
    """
    start_t = datetime.datetime.now()
    print("begin-buy_sell_fun_mp:", start_t)
    dataR = pd.DataFrame()
    for code in datam.index.levels[1]:
        # data = price.copy()
        # price = datam.query("code=='%s'" % code)
        # data = price.copy()
        data = buy_sell_fun(datam, code)
        # if code == '000732':
        #     print(data.tail(22))
        if len(dataR) == 0:
            dataR = data
        else:
            dataR = dataR.append(data)

    end_t = datetime.datetime.now()
    print(end_t, 'buy_sell_fun_mp spent:{}'.format((end_t - start_t)))

    result01 = dataR['nav'].groupby(level=['date']).sum()
    # result02 = dataR['nav'].groupby(level=['date']).count()
    # TODO
    result02 = dataR['nav'].groupby(level=['date']).sum()

    num = dataR.flag.abs().sum()
    dataR2 = pd.DataFrame({'nav':result01 - result02 + 1,'flag':0})
    # dataR2['flag'] = 0
    dataR2.iat[-1,1] = num
    # result['nav'] = result['nav']  - len(datam.index.levels[1]) + 1
    return dataR2

def do_get_data_mp(key, codelist, st_start, st_end):
    mongo_mp = MongoIo()
    # start_t = datetime.datetime.now()
    # print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
    databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start, st_end = st_end)
    # end_t = datetime.datetime.now()
    # print(end_t, 'get_data do_get_data_mp spent:{}'.format((end_t - start_t)))

def get_data(st_start, st_end):
    start_t = datetime.datetime.now()
    print("begin-get_data:", start_t)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    # codelist = ['512690', '510900', '513100', '510300',
    #             '512980', '512170', '515000', '512800',
    #             '159941', '159994', '515050', '159920',
    #             '159952', '159987', '159805', '159997',
    #             '159919',]

    # codelist = ['510300']

    # # 获取ETF/股票中文名称，只是为了看得方便，交易策略并不需要ETF/股票中文名称
    # #stock_names = QA.QA_fetch_etf_name(codelist)
    # #codename = [stock_names.at[code, 'name'] for code in codelist]

    # ## 读取 ETF基金 日线，存在index_day中
    # #data_day = QA.QA_fetch_index_day_adv(codelist,
    # #    start='2010-01-01',
    # #    end='{}'.format(datetime.date.today()))

    # # codelist = ['600519']
    # #codelist = ['600239']
    # #codelist = ['600338']
    # codelist = ['600095','600822','600183']
    # codelist = ["600109", "600551", "600697", "601066", "000732", "000905", "002827","600338","002049","300620"]
    # # codelist = ['600380','600822']

    # code_file = "../config/stock_list.json"
    # codelist = []
    limit_len = 0
    codelist=QA.QA_fetch_stock_block_adv().code
    # with open(code_file, 'r') as f:
    #     data = json.load(f)
    #     for d in data['code']:
    #         if len(d) > 6:
    #             d = d[len(d) - 6:len(d)]
    #         # if d[0:3] == '300' or d[0:3] == '301' or d[0:3] == '688' or d[0:3] == '002':
    #         #     continue
    #         # if d[0:3] != '600' and d[0:3] != '602' and d[0:3] != '603':
    #         # if d[0:3] != '300':
    #         # if d[0:3] != '002':
    #         #     continue
    #         codelist.append(d)
    #         limit_len = limit_len + 1
    #         # if limit_len > 20:
    #         #     break
    # codelist = ["",",","",""]
    codelist = list(mongo.get_positions().index)
    subcode_len = int(len(codelist) / pool_size)
    code_dict = {}
    pool = Pool(cpu_count())
    for i in range(pool_size):
        if i < pool_size - 1:
            code_dict[str(i)] = codelist[i* subcode_len : (i+1) * subcode_len]
        else:
            code_dict[str(i)] = codelist[i * subcode_len:]

        pool.apply_async(do_get_data_mp, args=(i, code_dict[str(i)], st_start, st_end))

    pool.close()
    pool.join()

    # # todo begin
    # data_day = pd.DataFrame()
    # for i in range(pool_size):
    #     if len(data_day) == 0:
    #         data_day = databuf_mongo[i]
    #     else:
    #         data_day = data_day.append(databuf_mongo[i])
    #     # print(len(dataR))
    # data_day.sort_index()
    # # todo end
    # 获取股票中文名称，只是为了看得方便，交易策略并不需要股票中文名称
    # stock_names = QA.QA_fetch_stock_name(codelist)
    # codename = [stock_names.at[code] for code in codelist]

    # data_day = QA.QA_fetch_stock_day_adv(codelist,
    #                                     '2010-01-01',
    #                                     '{}'.format(datetime.date.today(),)).to_qfq()

    # st_start="2018-12-01"
    # data_day = mongo.get_stock_day(codelist, st_start=st_start)

    end_t = datetime.datetime.now()
    # print("data-total-len:", len(dataR))
    print(end_t, 'get_data spent:{}'.format((end_t - start_t)))

    # return data_day

def main_param(argv):
    st_begin = ''
    st_end = ''
    func = ''
    try:
        opts, args = getopt.getopt(argv[1:], "hb:e:f:", ["st-begin=", "st-end=", "func="])
    except getopt.GetoptError:
        print(argv[0], ' -b <st-begin> [-e <st-end>] [-f <func-name:dhm>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(argv[0], ' -b2 <st-begin> [-e st-end] [-f func-name:dhm]')
            sys.exit()
        elif opt in ("-b", "--st-begin"):
            st_begin = arg
        elif opt in ("-e", "--st-end"):
            st_end = arg
        elif opt in ("-f", "--func"):
            func = 'tdx_%s' % arg
    return st_begin, st_end, func

if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)
    st_start, st_end, func = main_param(sys.argv)
    if st_end == "":
        st_end = start_t.strftime("%Y-%m-%d")
    print("input", st_start, st_end, func)
    # 计算数据步骤
    # 1, 读取数据（多进程，读入缓冲）
    # 2, 计算公式（多进程，读取缓冲）
    # 3, 回测（按照日期循环）
    # 3.1, 按照code循环计算（多进程／多线程）
    # 4, 结果统计／输出图形


    # 1, 读取数据（多进程，读入缓冲）
    # 开始日期
    # data_day = get_data(st_start)
    # print(data_day)
    # indices_rsrsT = tdx_func(data_day)
    start_date = datetime.datetime.strptime(st_start, "%Y-%m-%d") - datetime.timedelta(100)
    st_start2 = datetime.datetime.strftime(start_date, "%Y-%m-%d")
    get_data(st_start2, st_end)

    # 2, 计算公式（多进程，读取缓冲）
    indices_rsrsT = tdx_func_mp(func, st_start)
    # print(indices_rsrsT.head())
    # 3, 回测（按照日期循环）
    # result_Back = backtest(indices_rsrsT)

    resultT = summary(func, st_start, st_end, indices_rsrsT)

    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))

    benchcode = "000300"
    result = mongo.get_index_day(benchcode, st_start=st_start, st_end = st_end)
    # indices_rsrs = data_day.add_func(pre_rsrs_data_func)
    # result = indices_rsrs
    # print(indices_rsrs)

    #xtick = np.arange(0,result.shape[0],int(result.shape[0] / 7))
    #xticklabel = pd.Series(result.index.date[xtick])
    xticklabel = result.index.get_level_values(level=0).to_series().apply(lambda x: x.strftime("%Y-%m-%d")[2:16])

    # TODO
    plt.figure(figsize=(15,3))
    fig = plt.axes()
    plt.plot(np.arange(resultT.shape[0]), resultT.nav,label = 'MyCodes',linewidth = 2)
    plt.plot(np.arange(result.shape[0]), result.close / result.close[0], label = benchcode, linewidth = 2)

    fig.set_xticks(range(0, len(xticklabel),
                         round(len(xticklabel) / 12)))
    fig.set_xticklabels(xticklabel[::round(len(xticklabel) / 12)],
                        rotation = 45)
    plt.legend()
    plt.show()
