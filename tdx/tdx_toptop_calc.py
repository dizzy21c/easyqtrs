import pandas as pd
import os
import datetime
import numpy as np 
import statsmodels.formula.api as sml

import matplotlib.pyplot as plt
import scipy.stats as scs
import matplotlib.mlab as mlab
from easyquant.indicator.base import *
import traceback
import json
from easyquant import MongoIo
import statsmodels.api as sm
from multiprocessing import Process, Pool, cpu_count, Manager
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
from func.tdx_func import tdx_dhmcl, tdx_hm, tdx_sxp, tdx_hmdr, tdx_A01

executor = ThreadPoolExecutor(max_workers=cpu_count() * 2)

mongo = MongoIo()

databuf_mongo = Manager().dict()
databuf_tdxfunc = Manager().dict()
pool_size = cpu_count()
# print("pool size=%d" % pool_size)
def tdx_base_func(data, code_list = None):
    """
    准备数据
    """
    # highs = data.high
    # start_t = datetime.datetime.now()
    # print("begin-tdx_base_func:", start_t)

    # CLOSE=data.close
    # C=data.close
    # 前炮 = CLOSE > REF(CLOSE, 1) * 1.099
    # 小阴小阳 = HHV(ABS(C - REF(C, 1)) / REF(C, 1) * 100, BARSLAST(前炮)) < 9
    # 小阴小阳1 = ABS(C - REF(C, 1)) / REF(C, 1) * 100 < 9
    # 时间限制 = IFAND(COUNT(前炮, 30) == 1, BARSLAST(前炮) > 5, True, False)
    # 后炮 = IFAND(REF(IFAND(小阴小阳, 时间限制, 1, 0), 1) , 前炮, 1, 0)
    # return pd.DataFrame({'FLG': 后炮}).iloc[-1]['FLG']
    # return 后炮.iloc[-1]
    # bsFlg, nb = tdx_A01(data)
    bsFlg, nb = tdx_hmdr(data)
    # 斜率
    data = data.copy()
    # data['bflg'] = IF(REF(后炮,1) > 0, 1, 0)
    data['bflg'] = bsFlg
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
    # if code == '000732':
    #     print(data.tail(22))
    return do_buy_sell_fun(data)
    # return data

def do_tdx_func(key):
    # calc_data = tdx_func(databuf_mongo[key])
    try:
        databuf_tdxfunc[key] = tdx_func(databuf_mongo[key])
    except:
        traceback.print_exc()
        databuf_tdxfunc[key] = pd.DataFrame()

def tdx_func(datam, code_list = None):
    """
    准备数据
    """
    # highs = data.high
    start_t = datetime.datetime.now()
    print("begin-tdx_func:", start_t)
    dataR = pd.DataFrame()
    if code_list is None:
        code_list = datam.index.levels[1]
    for code in code_list:
        data=datam.query("code=='%s'" % code)
        data = tdx_base_func(data)
        if len(dataR) == 0:
            dataR = data
        else:
            dataR = dataR.append(data)
    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func spent:{}'.format((end_t - start_t)))
    return dataR.sort_index()

def tdx_func_mp():
    start_t = datetime.datetime.now()
    print("begin-tdx_func_mp :", start_t)
    pool = Pool(cpu_count())
    for i in range(pool_size):
        pool.apply_async(do_tdx_func, args=(i, ))

    pool.close()
    pool.join()

    # todo begin
    dataR = pd.DataFrame()
    for i in range(pool_size):
        if len(dataR) == 0:
            dataR = databuf_tdxfunc[i]
        else:
            dataR = dataR.append(databuf_tdxfunc[i])
        # print(len(dataR))
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
    return do_buy_sell_fun(data)

def do_buy_sell_fun(data, S1=1.0, S2=0.8):
    """
    斜率指标交易策略标准分策略
    """
    # price = datam.query("code=='%s'" % code)
    # # data = price.copy()
    # data = price.copy()
    data['flag'] = 0 # 买卖标记
    data['position'] = 0 # 持仓标记
    data['hold_price'] = 0  # 持仓价格
    bflag = data.columns.get_loc('bflg')
    # beta = data.columns.get_loc('beta')
    flag = data.columns.get_loc('flag')
    position_col = data.columns.get_loc('position')
    close_col = data.columns.get_loc('close')
    high_col = data.columns.get_loc('high')
    open_col = data.columns.get_loc('open')
    hold_price_col = data.columns.get_loc('hold_price')
    position = 0 # 是否持仓，持仓：1，不持仓：0
    sflg = 0
    hdays = 0
    for i in range(1,data.shape[0] - 1):
        # 开仓
        if position > 0:
            hdays = hdays + 1
        else:
            hdays = 0
        if data.iat[i, bflag] > 0 and position == 0:
            sflg = 0
            if data.iat[i+1,open_col] < data.iat[i,close_col] * 1.092\
                    and data.iat[i+1,open_col] > data.iat[i,close_col] * 1.02:
            # if data.iat[i+1,open_col] > data.iat[i,close_col] * 1.07:
                data.iat[i + 1, flag] = 1
                data.iat[i + 1, position_col] = 1
                data.iat[i + 1, hold_price_col] = data.iat[i+1, open_col]
                position = 1
                print("buy  : date=%s code=%s price=%.2f" % (data.iloc[i+1].name[0], data.iloc[i+1].name[1], data.iloc[i+1].close))
                # hdays = 0
            else:
                data.iat[i + 1, position_col] = data.iat[i, position_col]
                data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]
                # pass
        # 平仓
        # elif data.iat[i, bflag] == S2 and position == 1:
        elif data.iat[i, position_col] > 0 and position == 1:
            cprice = data.iat[i, close_col]
            # oprice = data.iat[i, open_col]
            hold_price = data.iat[i, hold_price_col]
            if cprice < hold_price * 0.95:
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
            if sflg < 0:# or cprice > hprice * 1.2:
                data.iat[i, flag] = -1
                data.iat[i + 1, position_col] = 0
                data.iat[i + 1, hold_price_col] = 0
                position = 0
                print("sell -5 : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
                sflg = 0
            elif sflg == 5 and high_price / cprice > 1.08:
                data.iat[i, flag] = -1
                data.iat[i + 1, position_col] = 0
                data.iat[i + 1, hold_price_col] = 0
                position = 0
                print("sell 50 : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
                sflg = 0
            elif sflg == 4 and high_price / cprice > 1.07:
                data.iat[i, flag] = -1
                data.iat[i + 1, position_col] = 0
                data.iat[i + 1, hold_price_col] = 0
                position = 0
                print("sell 40 : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
                sflg = 0
            elif sflg == 3 and high_price / cprice > 1.06:
                data.iat[i, flag] = -1
                data.iat[i + 1, position_col] = 0
                data.iat[i + 1, hold_price_col] = 0
                position = 0
                print("sell 30 : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
                sflg = 0
            elif sflg == 2 and high_price / cprice > 1.05:
                data.iat[i, flag] = -1
                data.iat[i + 1, position_col] = 0
                data.iat[i + 1, hold_price_col] = 0
                position = 0
                print("sell 20 : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
                sflg = 0
            elif sflg == 1 and high_price / cprice > 1.04:
                data.iat[i, flag] = -1
                data.iat[i + 1, position_col] = 0
                data.iat[i + 1, hold_price_col] = 0
                position = 0
                print("sell 10 : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
                sflg = 0
            elif sflg == 0 and hdays > 3:
                data.iat[i, flag] = -1
                data.iat[i + 1, position_col] = 0
                data.iat[i + 1, hold_price_col] = 0
                position = 0
                print("sell : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
                sflg = 0

            else:
                data.iat[i + 1, position_col] = data.iat[i, position_col]
                data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]
        # 保持
        else:
            data.iat[i + 1, position_col] = data.iat[i, position_col]
            data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]

    data['nav'] = (1+data.close.pct_change(1).fillna(0) * data.position).cumprod() - 1
    return data
def buy_sell_fun_mp(datam, S1=1.0, S2=0.8):
    start_t = datetime.datetime.now()
    print("begin-buy_sell_fun_mp-01:", start_t)

    result01 = datam['nav'].groupby(level=['date']).sum()
    # result02 = datam['nav'].groupby(level=['date']).count()
    result02 = datam['position'].groupby(level=['date']).sum()
    # print(result02)
    for i in range(len(result02)):
        if result02[i] <= 0:
            result02[i] = 1
        if i > 0:
            if result02[i] < result02[i - 1]:
                result02.iloc[i] = result02.iloc[i - 1]
    # print(result02)
    num = datam.flag.abs().sum()
    # dataR = pd.DataFrame({'nav':result01 - result02 + 1,'flag':0})
    dataR = pd.DataFrame({'nav': 1 + result01 / result02, 'flag': 0})
    # dataR2['flag'] = 0
    dataR.iat[-1,1] = num
    # result['nav'] = result['nav']  - len(datam.index.levels[1]) + 1
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

def do_get_data_mp(key, codelist, st_start):
    mongo_mp = MongoIo()
    start_t = datetime.datetime.now()
    print("begin-get_data do_get_data_mp: key=%s, time=%s" %( key,  start_t))
    databuf_mongo[key] = mongo_mp.get_stock_day(codelist, st_start=st_start)
    end_t = datetime.datetime.now()
    print(end_t, 'get_data do_get_data_mp spent:{}'.format((end_t - start_t)))

def get_data(st_start):
    start_t = datetime.datetime.now()
    print("begin-get_data:", start_t)
    # ETF/股票代码，如果选股以后：我们假设有这些代码
    codelist = ['512690', '510900', '513100', '510300',
                '512980', '512170', '515000', '512800',
                '159941', '159994', '515050', '159920',
                '159952', '159987', '159805', '159997',
                '159919',]

    codelist = ['510300']

    # 获取ETF/股票中文名称，只是为了看得方便，交易策略并不需要ETF/股票中文名称
    #stock_names = QA.QA_fetch_etf_name(codelist)
    #codename = [stock_names.at[code, 'name'] for code in codelist]

    ## 读取 ETF基金 日线，存在index_day中
    #data_day = QA.QA_fetch_index_day_adv(codelist,
    #    start='2010-01-01',
    #    end='{}'.format(datetime.date.today()))

    # codelist = ['600519']
    #codelist = ['600239']
    #codelist = ['600338']
    codelist = ['600095','600822','600183']
    codelist = ["600109", "600551", "600697", "601066", "000732", "000905", "002827","600338","002049","300620"]
    # codelist = ['600380','600822']

    code_file = "../config/stock_list.json"
    codelist = []
    with open(code_file, 'r') as f:
        data = json.load(f)
        for d in data['code']:
            if len(d) > 6:
                d = d[len(d) - 6:len(d)]
            codelist.append(d)
    subcode_len = int(len(codelist) / pool_size)
    code_dict = {}
    pool = Pool(cpu_count())
    for i in range(pool_size):
        if i < pool_size - 1:
            code_dict[str(i)] = codelist[i* subcode_len : (i+1) * subcode_len]
        else:
            code_dict[str(i)] = codelist[i * subcode_len:]

        pool.apply_async(do_get_data_mp, args=(i, code_dict[str(i)], st_start))

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

if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)

    st_start="2019-12-01"
    # data_day = get_data(st_start)
    # print(data_day)
    # indices_rsrsT = tdx_func(data_day)
    get_data(st_start)
    indices_rsrsT = tdx_func_mp()
    resultT = buy_sell_fun_mp(indices_rsrsT)
    # resultT = indices_rsrsT
    num = resultT.flag.abs().sum() / 2
    nav = resultT.nav[resultT.shape[0] - 1]
    print(resultT)
    # mnav = min(resultT.nav)
    max_dropback = round(float(max([(resultT.nav.iloc[idx] - resultT.nav.iloc[idx::].min()) / resultT.nav.iloc[idx] for idx in range(len(resultT.nav))])),2)
    # max_dropback = 0
    print('RSRS1_T 交易次数 = ',num)
    print('策略净值为= %.2f 最大回撤 %.2f ' % (nav, max_dropback * 100))

    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))

    benchcode = "000300"
    result = mongo.get_index_day(benchcode, st_start=st_start)
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
    # plt.plot(np.arange(result.shape[0]), result2.nav,label = 'RSRS2',linewidth = 2)
    # plt.plot(np.arange(result.shape[0]), result3.nav,label = 'RSRS3',linewidth = 2)
    # plt.plot(np.arange(result.shape[0]), result4.nav,label = 'RSRS4',linewidth = 2)
    plt.plot(np.arange(result.shape[0]), result.close / result.close[0], label = benchcode, linewidth = 2)

    fig.set_xticks(range(0, len(xticklabel),
                         round(len(xticklabel) / 12)))
    fig.set_xticklabels(xticklabel[::round(len(xticklabel) / 12)],
                        rotation = 45)
    plt.legend()
    plt.show()