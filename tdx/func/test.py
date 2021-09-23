import sys
from easyquant import MongoIo
from tdx_func import *

print("exam:python test.py <code:123456> <func-name:dqe_test_A01>")

m=MongoIo()
data=m.get_stock_day(sys.argv[1])

print(eval("tdx_%s" % sys.argv[2])(data))
