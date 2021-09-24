#!/usr/bin/env python

from QAPUBSUB import producer

import zsorder_pb2

# z1= subscriber_routing(exchange='xx',routing_key='x1')
# z2 = subscriber_routing(exchange='xx',routing_key='x2')
# z3 = subscriber_routing(exchange='xx',routing_key='x2')

# z1.callback= lambda a,b,c,x: print('FROM X1 {}'.format(x))
# z2.callback= lambda a,b,c,x: print('FROM X2 {}'.format(x))
# z3.callback= lambda a,b,c,x: print('FROM X3 {}'.format(x))
# p = publisher_routing(exchange='zsorder')
p = producer.publisher(exchange='zsorder')



# threading.Thread(target=z1.start).start()

# threading.Thread(target=z2.start).start()
# threading.Thread(target=z3.start).start()

zsorder = zsorder_pb2.zsorder()
zsorder.code = '000001'
zsorder.vol = 1000
zsorder.price = 0.0
zsorder.bsflg = 1

# p.pub('xxxxx',routing_key='x1')

# p.pub('1',routing_key='x2')
print(zsorder.SerializeToString())

p.pub(zsorder.SerializeToString())

# print("test2")
p.pub('test2')

"""
在exchange为 xx的mq中


routing_key = x1 ==>  有一个订阅者 z1
routing_key = x2 ==>  有两个订阅者 z2, z3

"""