from easyquant import StrategyTemplate
from datetime import datetime
from threading import Thread, current_thread, Lock
import time

class calcStrategy(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self._data = data

    def run(self):
        f = open('data/out-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S'), 'a+')
        for d in self._data:
            # print(d)
            f.write("'%s':'%s'," % ('code', d))
            for key, value in self._data[d].items():
                f.write("'%s':'%s'," %(key, value))
            f.write("\n")
        f.close()
        # print ('Consumer %s Receive.' % (current_thread()))

class Strategy(StrategyTemplate):
    name = 'save'

    def strategy(self, event):
        self.log.info('\n\nStrategy save event')
        t = calcStrategy(event.data)
        t.start()
        t.join()
        # self.log.info('data: stock-code-name %s' % event.data['162411'])
        # self.log.info('check balance')
        # self.log.info(self.user.balance)
        # self.log.info('\n')
        # file = open('data/out-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S'), 'a+')
        # for d in event.data:
        #     print(d)
        #     file.write("'%s':'%s'," % ('code', d))
        #     for key, value in event.data[d].items():
        #         file.write("'%s':'%s'," %(key, value))
        #     file.write("\n")
        # file.close()


