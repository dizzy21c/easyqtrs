#!/usr/bin/env python

import QAPUBSUB
import threading

from QAPUBSUB.consumer import subscriber_routing
from QAPUBSUB.producer import publisher_routing




z1= subscriber_routing(exchange='xx',routing_key='x1')
z2 = subscriber_routing(exchange='xx',routing_key='x2')
z3 = subscriber_routing(exchange='xx',routing_key='x2')

z1.callback= lambda a,b,c,x: print('FROM X1 {}'.format(x))
z2.callback= lambda a,b,c,x: print('FROM X2 {}'.format(x))
z3.callback= lambda a,b,c,x: print('FROM X3 {}'.format(x))
p = publisher_routing(exchange='xx')


threading.Thread(target=z1.start).start()

threading.Thread(target=z2.start).start()
threading.Thread(target=z3.start).start()
p.pub('xxxxx',routing_key='x1')

p.pub('1',routing_key='x2')

"""
在exchange为 xx的mq中


routing_key = x1 ==>  有一个订阅者 z1
routing_key = x2 ==>  有两个订阅者 z2, z3

"""