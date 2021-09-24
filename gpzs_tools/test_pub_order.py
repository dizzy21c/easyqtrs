#!/usr/bin/env python

# from QAPUBSUB import producer
#
import gpzs_order_pb2
from easymq import EasyMq

def test_pub_direct():
    # easymq = EasyMq(host='192.168.3.8')
    easymq = EasyMq()
    easymq.init_pub(exchange="zsorder2")

    # easymq.pub(json.dumps(stdata), stcode)


    zsorder = gpzs_order_pb2.gpzs_order()
    zsorder.code = '000001'
    zsorder.vol = 1000
    zsorder.price = 0.0
    zsorder.bsflg = 1
    zsorder.zsno = 0

    # p.pub('xxxxx',routing_key='x1')

    # p.pub('1',routing_key='x2')
    print(zsorder.SerializeToString())

    # p.pub(zsorder.SerializeToString())
    easymq.pub(zsorder.SerializeToString())

def test_pub_fanout():
    # easymq = EasyMq(host='192.168.3.8')
    easymq = EasyMq()
    easymq.init_pub(exchange="zsorder.fanout", exchange_type='fanout')

    # easymq.pub(json.dumps(stdata), stcode)


    zsorder = gpzs_order_pb2.gpzs_order()
    zsorder.code = '002626'
    zsorder.vol = 1000
    zsorder.price = 0.0
    zsorder.bsflg = 1
    zsorder.zsno = 0

    # p.pub('xxxxx',routing_key='x1')

    # p.pub('1',routing_key='x2')
    print(zsorder.SerializeToString())

    # p.pub(zsorder.SerializeToString())
    easymq.pub(zsorder.SerializeToString())

# def test_sub():
#     easymq = EasyMq()
#     easymq.init_pub(exchange="zsorder")

if __name__ == "__main__":
    test_pub_fanout()
    # test_pub_direct()

