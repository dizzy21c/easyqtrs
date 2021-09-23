#


"""
stock_base
"""
import uuid
import datetime
import json
import os
import threading
import requests
import pandas as pd
import pymongo
from qaenv import (eventmq_ip, eventmq_password, eventmq_port,
                   eventmq_username, mongo_ip)

import QUANTAXIS as QA
from QUANTAXIS.QAARP import QA_Risk, QA_User
from QUANTAXIS.QAEngine.QAThreadEngine import QA_Thread
from QUANTAXIS.QAUtil.QAParameter import MARKET_TYPE, RUNNING_ENVIRONMENT, ORDER_DIRECTION
from QAPUBSUB.consumer import subscriber_topic,  subscriber_routing
from QAPUBSUB.producer import publisher_routing
from QAStrategy.qactabase import QAStrategyCTABase
from QIFIAccount import QIFI_Account

# from qactabase import QAStrategyBase
from easyquant import MongoIo


class StrategyBase:

    def __init__(self, code=['000001'], frequence='1min', strategy_id='QA_STRATEGY', risk_check_gap=1
                 , portfolio='default', init_cash=1000000
                 , start='2019-01-01', end='2019-10-21', send_wx=False, market_type='stock_cn',
                 data_host=eventmq_ip, data_port=eventmq_port, data_user=eventmq_username, data_password=eventmq_password,
                 trade_host=eventmq_ip, trade_port=eventmq_port, trade_user=eventmq_username, trade_password=eventmq_password,
                 taskid=None, mongo_ip=mongo_ip, model='py'):
        """
        code 可以传入单个标的 也可以传入一组标的(list)
        会自动基于code来判断是什么市场
        TODO: 支持多个市场同时存在

        self.trade_host 交易所在的eventmq的ip  [挂ORDER_ROUTER的]

        /



        """
        self.username = 'admin'
        self.password = 'admin'

        self.trade_host = trade_host
        self.code = code
        self.frequence = frequence
        self.strategy_id = strategy_id

        self.portfolio = portfolio

        self.data_host = data_host
        self.data_port = data_port
        self.data_user = data_user
        self.data_password = data_password
        self.trade_host = trade_host
        self.trade_port = trade_port
        self.trade_user = trade_user
        self.trade_password = trade_password

        self.start = start
        self.end = end
        self.init_cash = init_cash
        self.taskid = taskid

        self.running_time = ''

        self.market_preset = QA.QAARP.MARKET_PRESET()
        self._market_data = []
        self.risk_check_gap = risk_check_gap
        self.latest_price = {}

        self.isupdate = False
        self.model = model
        self.new_data = {}
        self._systemvar = {}
        self._signal = []
        self.send_wx = send_wx
        if isinstance(self.code, str):

            self.last_order_towards = {self.code: {'BUY': '', 'SELL': ''}}
        else:
            self.last_order_towards = dict(
                zip(self.code, [{'BUY': '', 'SELL': ''} for i in range(len(self.code))]))
        self.dt = ''
        if isinstance(self.code, str):
            self.market_type = MARKET_TYPE.STOCK_CN
        else:
            # self.market_type = MARKET_TYPE.FUTURE_CN if re.search(
            #     r'[a-zA-z]+', self.code[0]) else MARKET_TYPE.STOCK_CN
            self.market_type = MARKET_TYPE.STOCK_CN

        self.bar_order = {'BUY_OPEN': 0, 'SELL_OPEN': 0,
                          'BUY_CLOSE': 0, 'SELL_CLOSE': 0}

        self._num_cached = 120
        self._cached_data = []
        self.user_init()

        # super().__init__(code=code, frequence=frequence, strategy_id=strategy_id, risk_check_gap=risk_check_gap, portfolio=portfolio,
        #                  start=start, end=end, send_wx=send_wx,
        #                  data_host=eventmq_ip, data_port=eventmq_port, data_user=eventmq_username, data_password=eventmq_password,
        #                  trade_host=eventmq_ip, trade_port=eventmq_port, trade_user=eventmq_username, trade_password=eventmq_password,
        #                  taskid=taskid, mongo_ip=mongo_ip)


        # self.code = code
        self.send_wx = send_wx

        self.mongo = MongoIo()

    @property
    def bar_id(self):
        return len(self._market_data)


    def run_backtest(self):
        self.debug()
        self.acc.save()

        risk = QA_Risk(self.acc)
        risk.save()

        try:
            """add rank flow if exist

            QARank是我们内部用于评价策略ELO的库 此处并不影响正常使用
            """
            from QARank import QA_Rank
            QA_Rank(self.acc).send()
        except:
            pass

    def user_init(self):
        """
        用户自定义的init过程
        """
        pass

    def subscribe_data(self, code, frequence, data_host, data_port, data_user, data_password):
        """[summary]

        Arguments:
            code {[type]} -- [description]
            frequence {[type]} -- [description]
        """
        
        self.sub = subscriber_topic(exchange='realtime_stock_{}'.format(
            frequence), host=data_host, port=data_port, user=data_user, password=data_password, routing_key='')
        for item in code:
            self.sub.add_sub(exchange='realtime_stock_{}'.format(
                frequence), routing_key=item)
        self.sub.callback = self.callback

    def upcoming_data(self, new_bar):
        """upcoming_bar :

        Arguments:
            new_bar {json} -- [description]
        """
        self._market_data = pd.concat([self._old_data, new_bar])
        # QA.QA_util_log_info(self._market_data)

        if self.isupdate:
            self.update()
            self.isupdate = False

        self.update_account()
        # self.positions.on_price_change(float(new_bar['close']))
        self.on_bar(new_bar)

    def ind2str(self, ind, ind_type):
        z = ind.tail(1).reset_index().to_dict(orient='records')[0]
        return json.dumps({'topic': ind_type, 'code': self.code, 'type': self.frequence, 'data': z})

    def callback(self, a, b, c, body):
        """在strategy的callback中,我们需要的是

        1. 更新数据
        2. 更新bar
        3. 更新策略状态
        4. 推送事件

        Arguments:
            a {[type]} -- [description]
            b {[type]} -- [description]
            c {[type]} -- [description]
            body {[type]} -- [description]
        """

        self.new_data = json.loads(str(body, encoding='utf-8'))

        self.latest_price[self.new_data['code']] = self.new_data['close']

        self.running_time = self.new_data['datetime']
        if self.dt != str(self.new_data['datetime'])[0:16]:
            # [0:16]是分钟线位数
            print('update!!!!!!!!!!!!')
            self.dt = str(self.new_data['datetime'])[0:16]
            self.isupdate = True

            
        self.acc.on_price_change(self.new_data['code'], self.new_data['close'])
        bar = pd.DataFrame([self.new_data]).set_index(['datetime', 'code']
                                                      ).loc[:, ['open', 'high', 'low', 'close', 'volume']]
        self.upcoming_data(bar)

    def _debug_sim(self):
        self.running_mode = 'sim'

        self._old_data = QA.QA_fetch_stock_min(self.code, QA.QA_util_get_last_day(
            QA.QA_util_get_real_date(str(datetime.date.today()))), str(datetime.datetime.now()), format='pd', frequence=self.frequence).set_index(['datetime', 'code'])

        self._old_data = self._old_data.loc[:, [
            'open', 'high', 'low', 'close', 'volume']]

        self.database = pymongo.MongoClient(mongo_ip).QAREALTIME

        self.client = self.database.account
        self.subscriber_client = self.database.subscribe

        self.acc = QIFI_Account(
            username=self.strategy_id, password=self.strategy_id, trade_host=mongo_ip)
        self.acc.initial()

        self.pub = publisher_routing(exchange='QAORDER_ROUTER', host=self.trade_host,
                                     port=self.trade_port, user=self.trade_user, password=self.trade_password)

        self.subscribe_data(self.code, self.frequence, self.data_host,
                            self.data_port, self.data_user, self.data_password)

        self.database.strategy_schedule.job_control.update(
            {'strategy_id': self.strategy_id},
            {'strategy_id': self.strategy_id, 'taskid': self.taskid,
             'filepath': os.path.abspath(__file__), 'status': 200}, upsert=True)

        # threading.Thread(target=, daemon=True).start()
        self.sub.start()

    def on_dailyopen(self):
        pass

    def on_dailyclose(self):
        pass

    def _on_1min_bar(self):
        #raise NotImplementedError
        if len(self._systemvar.keys()) > 0:
            self._signal.append(copy.deepcopy(self._systemvar))
        try:
            self.on_1min_bar()
        except:
            pass

    def on_deal(self, order):
        """

        order is a dict type
        """
        print('------this is on deal message ------')
        print(order)

    def on_1min_bar(self):
        raise NotImplementedError

    def on_5min_bar(self):
        raise NotImplementedError

    def on_15min_bar(self):
        raise NotImplementedError

    def on_30min_bar(self):
        raise NotImplementedError

    def order_handler(self):
        self._orders = {}

    def daily_func(self):
        QA.QA_util_log_info('DAILY FUNC')

    def run(self):
        while True:
            pass

    def x1(self, item):
        self.latest_price[item.name[1]] = item['close']
        if str(item.name[0])[0:10] != str(self.running_time)[0:10]:
            self.on_dailyclose()
            self.on_dailyopen()
            if self.market_type == QA.MARKET_TYPE.STOCK_CN:
                # print('backtest: Settle!')
                self.acc.settle()
        self._on_1min_bar()
        self._market_data.append(item)
        self.running_time = str(item.name[0])
        self.on_bar(item)


    def debug(self):
        self.running_mode = 'backtest'
        self.database = pymongo.MongoClient(mongo_ip).QUANTAXIS
        user = QA_User(username="admin", password='admin')
        port = user.new_portfolio(self.portfolio)
        self.acc = port.new_accountpro(
            account_cookie=self.strategy_id, init_cash=self.init_cash, market_type=self.market_type, frequence= self.frequence)
        #self.positions = self.acc.get_position(self.code)

        print(self.acc)

        print(self.acc.market_type)
        # data = QA.QA_quotation(self.code, self.start, self.end, source=QA.DATASOURCE.MONGO,
        #                        frequence=self.frequence, market=self.market_type, output=QA.OUTPUT_FORMAT.DATASTRUCT)
        #
        # data.data.apply(self.x1, axis=1)
        # data = self.get_data(self.code, self.start, self.end)
        data = self.get_data()
        data.apply(self.x1, axis=1)

    def get_data_old(self, codelist, start, end):
        # raise NotImplementedError
        pass

    def get_data(self):
        raise NotImplementedError

    def update_account(self):
        if self.running_mode == 'sim':
            QA.QA_util_log_info('{} UPDATE ACCOUNT'.format(
                str(datetime.datetime.now())))

            self.accounts = self.acc.account_msg
            self.orders = self.acc.orders
            self.positions = self.acc.positions

            self.trades = self.acc.trades
            self.updatetime = self.acc.dtstr
        elif self.running_mode == 'backtest':
            #self.positions = self.acc.get_position(self.code)
            self.positions = self.acc.positions

    def get_positions(self, code):
        if self.running_mode == 'sim':
            self.update_account()
            return self.acc.get_position(code)
        elif self.running_mode == 'backtest':
            return self.acc.get_position(code)

    def send_order(self,  direction='BUY', offset='OPEN', code=None, price=3925, volume=10, order_id='',):

        towards = eval('ORDER_DIRECTION.{}_{}'.format(direction, offset))
        order_id = str(uuid.uuid4()) if order_id == '' else order_id

        if self.market_type == QA.MARKET_TYPE.STOCK_CN:
            """
            在此对于股票的部分做一些转换
            """
            if towards == ORDER_DIRECTION.SELL_CLOSE:
                towards = ORDER_DIRECTION.SELL
            elif towards == ORDER_DIRECTION.BUY_OPEN:
                towards = ORDER_DIRECTION.BUY

        if isinstance(price, float):
            pass
        elif isinstance(price, pd.Series):
            price = price.values[0]

        if self.running_mode == 'sim':

            QA.QA_util_log_info(
                '============ {} SEND ORDER =================='.format(order_id))
            QA.QA_util_log_info('direction{} offset {} price{} volume{}'.format(
                direction, offset, price, volume))

            if self.check_order(direction, offset):
                self.last_order_towards = {'BUY': '', 'SELL': ''}
                self.last_order_towards[direction] = offset
                now = str(datetime.datetime.now())

                order = self.acc.send_order(
                    code=code, towards=towards, price=price, amount=volume, order_id=order_id)
                order['topic'] = 'send_order'
                self.pub.pub(
                    json.dumps(order), routing_key=self.strategy_id)

                self.acc.make_deal(order)
                self.bar_order['{}_{}'.format(direction, offset)] = self.bar_id
                if self.send_wx:
                    for user in self.subscriber_list:
                        QA.QA_util_log_info(self.subscriber_list)
                        try:
                            "oL-C4w2WlfyZ1vHSAHLXb2gvqiMI"
                            """http://www.yutiansut.com/signal?user_id=oL-C4w1HjuPRqTIRcZUyYR0QcLzo&template=xiadan_report&\
                                        strategy_id=test1&realaccount=133496&code=rb1910&order_direction=BUY&\
                                        order_offset=OPEN&price=3600&volume=1&order_time=20190909
                            """

                            requests.post('http://www.yutiansut.com/signal?user_id={}&template={}&strategy_id={}&realaccount={}&code={}&order_direction={}&order_offset={}&price={}&volume={}&order_time={}'.format(
                                user, "xiadan_report", self.strategy_id, self.acc.user_id, code, direction, offset, price, volume, now))
                        except Exception as e:
                            QA.QA_util_log_info(e)

            else:
                QA.QA_util_log_info('failed in ORDER_CHECK')

        elif self.running_mode == 'backtest':

            self.bar_order['{}_{}'.format(direction, offset)] = self.bar_id

            self.acc.receive_simpledeal(
                code=code, trade_time=self.running_time, trade_towards=towards, trade_amount=volume, trade_price=price, order_id=order_id)
            #self.positions = self.acc.get_position(self.code)


if __name__ == '__main__':
    StrategyBase(code=['000001', '000002']).run_sim()
