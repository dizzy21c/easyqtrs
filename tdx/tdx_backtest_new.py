import datetime
import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase
import random
from strategybase import StrategyBase
import numpy as np
import pandas as pd
from func.tdx_func import tdx_dhmcl, tdx_hm, tdx_sxp, tdx_hmdr
import math
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
from multiprocessing import Process, Pool, cpu_count, Manager

max_hold_days = 5
deal_amount = 50000
executor = ProcessPoolExecutor(max_workers=cpu_count() * 2)
bs_flg = 'BS_FLG'
def buy_action(data, next_buy, col_pos_tup, i):
    (flag_col, position_col, hold_price_col, close_col) = col_pos_tup
    if next_buy:
        data.iat[i + 1, flag_col] = 1
        # print("buy  : date=%s code=%s price=%.2f" % (data.iloc[i+1].name[0], data.iloc[i+1].name[1+1], data.iloc[i+1].close))
    else:
        data.iat[i, flag_col] = 1
        data.iat[i, position_col] = 1
        data.iat[i, hold_price_col] = data.iat[i, close_col]
        # print("buy  : date=%s code=%s price=%.2f" % (data.iloc[i+1].name[0], data.iloc[i].name[1], data.iloc[i].close))

    data.iat[i + 1, position_col] = 1
    data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]
    # position = 1
    position = 1
    hdays = 0
    return position, hdays

def sell_action(data, col_pos_tup, i, sell_pct):
    (flag_col, position_col, hold_price_col) = col_pos_tup
    data.iat[i, flag_col] = -1
    data.iat[i + 1, position_col] = 0
    data.iat[i + 1, hold_price_col] = 0
    # print("sell 60 : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
    # logout_out(data, 1, i, sell_pct)
    # print("pct=", sell_pct, ", sell : date=%s code=%s  price=%.2f" % (data.iloc[i].name[0], data.iloc[i].name[1], data.iloc[i].close))
    # 持仓标记
    position = 0
    # 盈亏标记
    sflg = 0
    return position, sflg

def do_buy_sell_fun(data, next_buy = False, S1=1.0, S2=0.8):
    # print(data.tail())
    """
    斜率指标交易策略标准分策略
    """
    # price = datam.query("code=='%s'" % code)
    # # data = price.copy()
    # data = price.copy()
    data[bs_flg] = 0 # 买卖标记
    data['position'] = 0 # 持仓标记
    data['hold_price'] = 0  # 持仓价格
    data['sell_close'] = data['close']  # 卖出价格
    bflag = data.columns.get_loc('bflg')
    # beta = data.columns.get_loc('beta')
    flag_col = data.columns.get_loc(bs_flg)
    position_col = data.columns.get_loc('position')
    close_col = data.columns.get_loc('close')
    sell_close_col = data.columns.get_loc('sell_close')
    high_col = data.columns.get_loc('high')
    low_col = data.columns.get_loc('low')
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
            # 涨停不能买入
            # if data.iat[i+1,open_col] < data.iat[i,close_col] * 1.092\
            #         and data.iat[i+1,open_col] > data.iat[i,close_col] * 1.02\
            #     and buy_ctl_check(data.iloc[i].name[0], buy_ctl_dict, share_lock):
            # if data.iat[i+1,open_col] > data.iat[i,close_col] * 1.07:

            # # 去除一字板
            # if data.iat[i, high_col] > data.iat[i, low_col] \
            #         and buy_ctl_check(data.iloc[i].name[0], buy_ctl_dict, share_lock):
            # 去除涨停
            if data.iat[i, close_col] / data.iat[i - 1, close_col] < 1.095:
            # if data.iat[i, close_col] / data.iat[i - 1, close_col] < 1.095 \
            #         and buy_ctl_check(data.iloc[i].name[0], buy_ctl_dict, share_lock):
                position, hdays = buy_action(data, next_buy, (flag_col, position_col, hold_price_col, close_col), i)
            # else:
            #     # data.iat[i, position_col] = 0
            #     data.iat[i + 1, position_col] = data.iat[i, position_col]
            #     data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]
                # pass
        # 平仓
        # elif data.iat[i, bflag] == S2 and position == 1:
        elif data.iat[i, position_col] > 0 and position == 1:
            # buy_ctl_check(data.iloc[i].name[0], buy_ctl_dict, share_lock)
            cprice = data.iat[i, close_col]
            # cprice = data.iat[i, open_col]
            # oprice = data.iat[i, open_col]
            hold_price = data.iat[i, hold_price_col]
            if cprice < hold_price * 0.95:# or oprice < hold_price * 0.95:
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

            if sflg < 0:# or cprice > hprice * 1.2:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, -5)
            elif sflg == 9 and high_price / cprice > 1.15:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 90)
            elif sflg == 8 and high_price / cprice > 1.12:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 80)
            elif sflg == 7 and high_price / cprice > 1.1:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 70)
            elif sflg == 6 and high_price / cprice > 1.1:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 60)
            elif sflg == 5 and high_price / cprice > 1.09:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 50)
            elif sflg == 4 and high_price / cprice > 1.08:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 40)
            elif sflg == 3 and high_price / cprice > 1.06:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 30)
            elif sflg == 2 and high_price / cprice > 1.05:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 20)
            elif sflg == 1 and high_price / cprice > 1.04:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 10)
            elif sflg == 0 and hdays > max_hold_days:
                position, sflg = sell_action(data, (flag_col, position_col, hold_price_col), i, 0)
            else:
                data.iat[i + 1, position_col] = data.iat[i, position_col]
                data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]

            # if position == 0:
            #     buy_ctl_check(data.iloc[i].name[0], buy_ctl_dict, share_lock, False)
        # 保持
        else:
            data.iat[i + 1, position_col] = data.iat[i, position_col]
            data.iat[i + 1, hold_price_col] = data.iat[i, hold_price_col]

    # data['nav'] = (1+data.close.pct_change(1).fillna(0) * data.position).cumprod() - 1
    return data

def tdx_base_func(datam, code):
    try:
        data = datam.query("code=='%s'" % code)
        # data = datam
        # tdx_func_result, next_buy = tdx_dhmcl(data)
        # tdx_func_result, next_buy = tdx_hm(data)
        tdx_func_result, next_buy = tdx_sxp(data)
        # tdx_func_result, next_buy = tdx_hmdr(data)
    # 斜率
    except:
        tdx_func_result, next_buy = False, False

    data = data.copy()
    data['bflg'] = tdx_func_result
    return do_buy_sell_fun(data, next_buy)

# class SimpleBacktest01(QAStrategyStockBase):
class SimpleBacktest01(StrategyBase):
    def on_bar(self, bar):
        # res = self.ma()
        # print(res.iloc[-1])
        # if np.isnan(res.MA2[-1]) or np.isnan(res.MA5[-1]):
        #     return
        code=bar.name[1]
        # print(bar.name)
        # print("code=%s, ma2=%6.2f, m5=%6.2f" % (code, res.MA2[-1], res.MA5[-1]))
        # print(res)
        # print(self.get_positions(code))
        # if res.MA5[-1] > res.MA30[-1]:
        if bar[bs_flg] > 0:
        # if res.DIF[-1] > res.DEA[-1]:

            # print('LONG price=%8.2f' % (bar['close']))
            price = bar['close']
            volume = math.floor(deal_amount / ( price * 100 )) * 100
            if self.get_positions(code).volume_long == 0 and volume > 100:
                self.send_order('BUY', 'OPEN', code=code, price=bar['close'], volume=volume)
                # print('time=%s, code=%s, BUY price=%8.2f' % (bar.name[0], code, bar['close']))
            # if self.positions.volume_short > 0:
            #     self.send_order('BUY', 'CLOSE', code=code, price=bar['close'], volume=1)

        elif bar[bs_flg] < 0:
            # print('SHORT price=%8.2f' % (bar['close']))

            # if self.acc.positions == {} or self.acc.positions.volume_short == 0:
            #     self.send_order('SELL', 'OPEN', code=code, price=bar['close'], volume=1)
            if self.get_positions(code).volume_long > 0:
                self.send_order('SELL', 'CLOSE', code=code, price=bar['close'], volume=1000)
                # print('time=%s, code=%s, SELL price=%8.2f' % (bar.name[0], code, bar['close']))

    def ma(self,):
        return QA.QA_indicator_MA(self.market_data, 5, 30)
        # return QA.QA_indicator_MACD(self.market_data)

    def risk_check(self):
        pass

    def get_data(self):
        start_t = datetime.datetime.now()
        print("get_data-begin-time:", start_t)

        # data = self.mongo.get_stock_day(code, st_start=start)
        # data = data.sort_index()

        data = QA.QA_quotation(self.code, self.start, self.end, source=QA.DATASOURCE.MONGO,
                               frequence=self.frequence, market=self.market_type, output=QA.OUTPUT_FORMAT.DATASTRUCT)

        dataR = pd.DataFrame()
        datam = data.data.sort_index()

        end_t = datetime.datetime.now()
        print(end_t, 'get_data-spent:{}'.format((end_t - start_t)))

        start_t = datetime.datetime.now()
        print("calc_data-begin-time:", start_t)

        task_list = []
        for code in self.code:
            task_list.append(executor.submit(tdx_base_func, datam, code))

        for task in task_list:
            tdx_func_result = task.result()
            if len(dataR) == 0:
                dataR = tdx_func_result
            else:
                dataR = dataR.append(tdx_func_result)

        end_t = datetime.datetime.now()
        print(end_t, 'calc_data-spent:{}'.format((end_t - start_t)))

        return dataR.sort_index()


def get_data(code_list, start, end, frequence='day', market_type='stock_cn'):
    start_t = datetime.datetime.now()
    print("get_data1-begin-time:", start_t)

    # data = self.mongo.get_stock_day(code, st_start=start)
    # data = data.sort_index()

    data = QA.QA_quotation(code_list, start, end, source=QA.DATASOURCE.MONGO,
                           frequence=frequence, market=market_type, output=QA.OUTPUT_FORMAT.DATASTRUCT)

    dataR = pd.DataFrame()
    datam = data.data.sort_index()

    end_t = datetime.datetime.now()
    print(end_t, 'get_data1-spent:{}'.format((end_t - start_t)))

    start_t = datetime.datetime.now()
    print("get_data2-begin-time:", start_t)

    task_list = []
    for code in code_list:
        # data = datam.query("code=='%s'" % code)
        task_list.append(executor.submit(tdx_base_func, datam, code))
        # tdx_func_result = tdx_base_func(data)
        # if len(dataR) == 0:
        #     dataR = tdx_func_result
        # else:
        #     dataR = dataR.append(tdx_func_result)

    for task in task_list:
        tdx_func_result = task.result()
        if len(dataR) == 0:
            dataR = tdx_func_result
        else:
            dataR = dataR.append(tdx_func_result)

    end_t = datetime.datetime.now()
    print(end_t, 'get_data2-spent:{}'.format((end_t - start_t)))

    return dataR.sort_index()

if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)
    codes_df = QA.QA_fetch_stock_list_adv()
    code_list = list(codes_df['code'])

    # get_data(code_list, start='2019-01-01', end='2020-12-31')

    # print(code_list)
    # code = QA.QA_fetch_stock_block_adv().code
    # print(code)
    s = SimpleBacktest01(
                # code=['000001', '000002','600822','000859']
                # code=code_list
                code=code_list
                # code=QA.QA_fetch_stock_block_adv().code
                # , init_cash = 1000000000000
                , frequence='day'
                , start='2019-12-01', end='2020-12-31'
                , portfolio='newback'
                , strategy_id='sxp2')
    # s.debug()
    s.run_backtest()
    # msg = s.acc.message
    # print("alpha=%6.2f, " % (msg['']))
    # s.update_account()
    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))

    risk = QA.QA_Risk(s.acc)
    # risk.plot_assets_curve().show()
    print(risk.annualize_return)
    print(risk.profit_construct)
