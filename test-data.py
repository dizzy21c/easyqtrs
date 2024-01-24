
from easyquant  import MongoIo
mongo = MongoIo()
codelist = ['000001']
databuf_mongo = mongo.get_stock_day(codelist, st_start='1990-01-01', st_end='2035-12-31')
print(databuf_mongo.iloc[-1])
