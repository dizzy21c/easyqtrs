import datetime
import time
import numpy as np
import pandas as pd

try:
    import QUANTAXIS as QA
except:
    print('PLEASE run "pip install QUANTAXIS" to call these modules')
    pass

try:
    from GolemQ.GQUtil.parameter import (
        AKA,
        INDICATOR_FIELD as FLD,
        TREND_STATUS as ST
    )
except:
    class AKA():
        """
        常量，专有名称指标，定义成常量可以避免直接打字符串造成的拼写错误。
        """

        # 蜡烛线指标
        CODE = 'code'
        NAME = 'name'
        OPEN = 'open'
        HIGH = 'high'
        LOW = 'low'
        CLOSE = 'close'
        VOLUME = 'volume'
        VOL = 'vol'
        DATETIME = 'datetime'
        LAST_CLOSE = 'last_close'
        PRE_CLOSE = 'pre_close'

        def __setattr__(self, name, value):
            raise Exception(u'Const Class can\'t allow to change property\' value.')
            return super().__setattr__(name, value)


def fetch_stock_day_realtime_adv(codelist,
                                    data_day,
                                    verbose=True):
    """
    查询日线实盘数据，支持多股查询
    """
    # if ((datetime.datetime.combine(datetime.date.today(),
    #                                datetime.datetime.min.time()) - data_day.data.index.get_level_values(level=0)[-1].to_pydatetime()) > datetime.timedelta(hours=10)):
    if verbose:
        if (verbose== True):
            print('时间戳差距超过：', datetime.datetime.combine(datetime.date.today(),
                                                             datetime.datetime.min.time()) - data_day.data.index.get_level_values(level=0)[-1].to_pydatetime(),
                  '尝试查找实盘数据....')
        data_realtime = QA.QA_fetch_stock_realtime_adv(codelist, num=5000,)
        if (data_realtime is not None) and \
            (len(data_realtime) > 0):
            # 合并实盘实时数据
            data_realtime = data_realtime.drop_duplicates((["datetime",
                        'code'])).set_index(["datetime",
                        'code'],
                            drop=False)
            data_realtime = data_realtime.reset_index(level=[1], drop=True)
            data_realtime['date'] = pd.to_datetime(data_realtime['datetime']).dt.strftime('%Y-%m-%d')
            data_realtime['datetime'] = pd.to_datetime(data_realtime['datetime'])
            for code in codelist:
                # *** 注意，QA QA_data_tick_resample_1min 函数不支持多标的 *** 需要循环处理
                data_realtime_code = data_realtime[data_realtime['code'].eq(code)]
                if (len(data_realtime_code) > 0):
                    data_realtime_code = data_realtime_code.set_index(['datetime']).sort_index()
                    if ('volume' in data_realtime_code.columns) and \
                        ('vol' not in data_realtime_code.columns):
                        # 我也不知道为什么要这样转来转去，但是各家(新浪，pytdx)l1数据就是那么不统一
                        data_realtime_code.rename(columns={"volume": "vol"},
                                                    inplace = True)
                    elif ('volume' in data_realtime_code.columns):
                        data_realtime_code['vol'] = np.where(np.isnan(data_realtime_code['vol']),
                                                             data_realtime_code['volume'],
                                                             data_realtime_code['vol'])

                    # 一分钟数据转出来了
                    data_realtime_1min = QA.QA_data_tick_resample_1min(data_realtime_code,
                                                                       type_='1min')
                    try:
                        data_realtime_1min = QA.QA_data_tick_resample_1min(data_realtime_code,
                                                                           type_='1min')
                    except:
                        print('fooo1', code)
                        print(data_realtime_code)
                        raise('foooo1{}'.format(code))
                    data_realtime_1day = QA.QA_data_min_to_day(data_realtime_1min)
                    if (len(data_realtime_1day) > 0):
                        # 转成日线数据
                        data_realtime_1day.rename(columns={"vol": "volume"},
                                                    inplace = True)

                        # 假装复了权，我建议复权那几天直接量化处理，复权几天内对策略买卖点影响很大
                        data_realtime_1day['adj'] = 1.0
                        data_realtime_1day['datetime'] = pd.to_datetime(data_realtime_1day.index)
                        data_realtime_1day = data_realtime_1day.set_index(['datetime', 'code'],
                                                                        drop=True).sort_index()
                        if (verbose== True):
                            # print(u'追加实时实盘数据，股票代码：{} 时间：{} 价格：{}'.format(data_realtime_1day.index[0][1],
                            print(u'add realtime data，code：{} time：{} price：{}'.format(data_realtime_1day.index[0][1],
                                                                                     data_realtime_1day.index[0][0],
                                                                                     data_realtime_1day[AKA.CLOSE][-1]))
                        data_day.data = data_day.data.append(data_realtime_1day,
                                                                sort=True)

    return data_day


def fetch_stock_min_realtime_adv(codelist,
                                    data_min,
                                    frequency,
                                    verbose=True):
    """
    查询分钟线实盘数据
    """
    data_realtime_1min = data_realtime_1min.reset_index(level=[1], drop=False)
    data_realtime_5min = QA.QA_data_min_resample(data_realtime_1min,
                                                 type_='5min')
    print(data_realtime_5min)

    data_realtime_15min = QA.QA_data_min_resample(data_realtime_1min,
                                                  type_='15min')
    print(data_realtime_15min)

    data_realtime_30min = QA.QA_data_min_resample(data_realtime_1min,
                                                  type_='30min')
    print(data_realtime_30min)
    data_realtime_1hour = QA.QA_data_min_resample(data_realtime_1min,
                                                 type_='60min')
    print(data_realtime_1hour)
    return data_min


if __name__ == '__main__':
    """
    用法示范
    """
    # codelist = ['600157', '300263', '600765']
    # codelist = ['000001']
    codelist = ['000410', '600718']
    data_day = QA.QA_fetch_stock_day_adv(codelist,
                                        '2018-01-01',
                                        '{}'.format(datetime.date.today(),)).to_qfq()

    data_day = fetch_stock_day_realtime_adv(codelist, data_day)