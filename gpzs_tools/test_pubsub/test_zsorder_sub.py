import zsorder_pb2
from QAPUBSUB import consumer
# import zsorder_pb2

# # @classmethod
# zsorder = zsorder_pb2.zsorder()
# zsorder.code = '000001'
# zsorder.vol = 1000
# zsorder.price = 0.0
# zsorder.bsflg = 1
# zs=zsorder.SerializeToString()
# print(zs)
# odata2 = zsorder_pb2.zsorder
# odata2.ParseFromString(zsorder)
# print(odata2.code)

def ucallback(a,b,c,data):
    odata = zsorder_pb2.zsorder()
    # print(a)
    # print(b)
    # print(data)
    # print(type(data))
    try:
        odata.ParseFromString(data)
        # odata.ParseFromBytes(data)
        # print("ok")
        print(odata.code)
    except Exception as e:
        print("error")
        print(e)


c = consumer.subscriber(exchange='zsorder')
# c.callback = lambda a,b,c,data: print(data)
c.callback = ucallback
c.start()
