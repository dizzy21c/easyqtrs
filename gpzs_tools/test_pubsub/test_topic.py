#!/usr/bin/env python

import QAPUBSUB
import threading

from QAPUBSUB.consumer import subscriber_topic
from QAPUBSUB.producer import publisher_topic


z1 = subscriber_topic(exchange='testTopic', routing_key='#')
z2 = subscriber_topic(exchange='testTopic', routing_key='#.SZ')
z3 = subscriber_topic(exchange='testTopic', routing_key='#.SH')


z1.callback = lambda a, b, c, x: print('FROM X1 {}'.format(x))
z2.callback = lambda a, b, c, x: print('FROM X2 {}'.format(x))

z2.add_sub(exchange='testTopic', routing_key='000001.SZ')

z3.callback = lambda a, b, c, x: print('FROM X3 {}'.format(x))
p = publisher_topic(exchange='testTopic', )


threading.Thread(target=z1.start).start()

threading.Thread(target=z2.start).start()
threading.Thread(target=z3.start).start()


p.pub('000001', routing_key='000001.SZ')

p.pub('000002', routing_key='000002.SZ')
p.pub('601318', routing_key='601318.SH')
"""
在exchange为 xx的mq中


routing_key = x1 ==>  有一个订阅者 z1
routing_key = x2 ==>  有两个订阅者 z2, z3

"""
