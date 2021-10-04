import sys
from easyquant import MongoIo
from tdx_func import *

print("exam:python test.py <code:123456> <func-name:dqe_test_A01> <stEnd:0:2021-09-13>")

m=MongoIo()
st_end = None
if sys.argv[3] != '0':
    st_end = sys.argv[3]
data=m.get_stock_day(sys.argv[1], st_end = st_end)

out=eval("tdx_%s" % sys.argv[2])(data)
# out.to_csv("test.csv")
print(out)
