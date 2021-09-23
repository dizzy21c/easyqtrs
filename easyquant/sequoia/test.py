# -*- encoding: UTF-8 -*-

import sys

import utils
from talib import ATR
import strategy.enter as enter
import strategy.low_atr as low_atr
import strategy.backtrace_ma250 as backtrace_ma250


import strategy.turtle_trade as turtle_trade
#from strategy import breakthrough_platform
import strategy.parking_apron as parking_apron


import logging

# data = utils.load("000012.h5")
#
# rolling_window = 21
# moving_average = 20
#
# average_true_range_list = ATR(
#     data.high.values[-rolling_window:],
#     data.low.values[-rolling_window:],
#     data.close.values[-rolling_window:],
#     timeperiod=moving_average
# )
#
# average_true_range = average_true_range_list[-1]
#
# settings.init()
# stock = ('002017', '东信和平')
# stock = ('601700', '风范股份')
def test_enter(code_name, end = '2019-05-17'):
  # code = '000001'
  # stock = ('600776', '东方通信')

  data = utils.read_data(code_name)
  # print(data)
  result = enter.check_ma(code_name, data, end_date=end) and backtrace_ma250.check(code_name, data, end_date=end)
  print("low atr check {0}'s result: {1}".format(code_name, result))
  #
  # rolling_window = 21
  # moving_average = 20
  #
  # average_true_range = ATR(
  #         data.high.values[-rolling_window:],
  #         data.low.values[-rolling_window:],
  #         data.close.values[-rolling_window:],
  #         timeperiod=moving_average
  #     )
  # print(data['high'].values)
  #
  # print(average_true_range)

  # print(atr_list)
  # atr = atr_list[-1]
  # print(atr)
  # print(enter.check_volume(stock, data, end_date="2018-01-02"))
  # import notify
  #
  # results = ['300188', '600271']
  # msg = '\n'.join("*代码：%s" % ''.join(x) for x in results)
  # notify.notify(msg)
  # print(results)

  # import tushare as ts
  #
  # data = ts.get_stock_basics()
  # print(data)

def end_date_filter(code_name, end_date = '2019-05-17'):
    data = utils.read_data(code_name)
    result = backtrace_ma250.check(code_name, data, end_date=end_date)
    # result = parking_apron.check(code_name, data, end_date=end_date)
    # result = low_atr.check_low_increase(code_name, data, end_date=end_date)
    # result = enter.check_ma(code_name, data, end_date=end_date) \
    #     and breakthrough_platform.check(code_name, data, end_date=end_date)
    if result:
        message = turtle_trade.calculate(code_name, data)
        # logging.info("{0} {1}".format(code_name, message))
        print("{0} {1}".format(code_name, message))
        # notify.notify("{0} {1}".format(code_name, message))
    return result

def main(argv):
  code = '000001'
  flg = "1"
  if len(sys.argv) > 1:
    code = sys.argv[1]

  if len(sys.argv) > 2:
    flg = sys.argv[2]

  stock = (code, 'other')
  # stock = ('600776', '东方通信')

  if flg == "1":
    print("do test_enter")
    test_enter(stock)
  elif flg == "2":
    print("do end_date_filter")
    end_date_filter(stock)
  else:
    print("do nothing") 

if __name__ == "__main__":
    main(sys.argv)