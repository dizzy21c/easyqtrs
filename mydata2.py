import easyquotation
import datetime
import json
import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine, MongoIo
from custom.fixedmainengine import FixedMainEngine
from custom.sinadataengine import SinaEngine
#import pymongo
#import redis
# choose = input('1: \n:')

broker = None

need_data = '' #get_broker_need_data(broker)

class DataSinaEngine(SinaEngine):
    EventType = 'data-sina'
    PushInterval = 60
    # config = "stock_list"
    mongo = MongoIo()
    # market = 'sh'  or 'sz'
    codelist = list(mongo.get_stock_list(notST=True, market=None).index)


# class BlockSinaEngine(SinaEngine):
#     EventType = 'block-sina'
#     PushInterval = 8
#     config = "bk_list"

class IndexSinaEngine(SinaEngine):
    EventType = 'index-sina'
    PushInterval = 10
    config = "index2_list"

# quotaton_engine = DefaultQuotationEngine if quotation_choose == '1' else LFEngine

#data_engine = DataSinaEngine
#index_engine = IndexSinaEngine
#worker_engine = WorkerEngine

# quotation_engine = LFEngine

#push_interval = int(input('please input interval(s)\n:'))
#push_interval = 10
#data_engine.PushInterval = push_interval
#index_engine.PushInterval = push_interval
#worker_engine.PushInterval = push_interval

# log_type_choose = '2' #input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录到指定文件\n: ')
log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'

log_filepath = 'logs/data-mainlog.txt' #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''

log_handler = DefaultLogHandler(name='real-data', log_type=log_type, filepath=log_filepath)

#client= pymongo.MongoClient('localhost',27017)
#db = client.quantaxis
#rdb = redis.Redis(host='localhost', port=6379, db=0)
#print(rdb)
#m = easyquant.MainEngine(broker, need_data, quotation_engines=[quotation_engine], log_handler=log_handler)
# qe_list=[data_engine, IndexSinaEngine, WorkerEngine]
qe_list=[DataSinaEngine, IndexSinaEngine]
m = easyquant.MainEngine(broker, need_data, quotation_engines=qe_list, log_handler=log_handler)
# m = FixedMainEngine(broker, need_data, quotation_engines=qe_list, log_handler=log_handler)
m.is_watch_strategy = False #True  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
# names=['save-index-data-disp', 'save-data-disp'] 
# names=['save-index-data-disp', 'save-data-disp', 'save-data-calc-01']
names=['save-index-data-disp', 'save-data-disp']
m.load_strategy(names=names)
m.start()
