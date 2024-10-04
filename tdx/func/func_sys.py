# common function
import math
import pandas as pd
from easyquant import MongoIo
import datetime
# from multiprocessing import Process, Pool, cpu_count, Manager
def get_next_date(calcDate, step = 1):
    cDate = datetime.datetime.strptime(calcDate, '%Y-%m-%d')
    cDate = cDate + datetime.timedelta(abs(step))
    if cDate.weekday() < 5:
        return datetime.datetime.strftime(cDate,'%Y-%m-%d')
    elif cDate.weekday() == 5:
        cDate = cDate + datetime.timedelta(2)
        return datetime.datetime.strftime(cDate,'%Y-%m-%d')
    elif cDate.weekday() == 6:
        cDate = cDate + datetime.timedelta(1)
        return datetime.datetime.strftime(cDate,'%Y-%m-%d')

def get_prev_date(calcDate, step = 1):
    cDate = datetime.datetime.strptime(calcDate, '%Y-%m-%d')
    cDate = cDate + datetime.timedelta(-1 * abs(step))
    if cDate.weekday() < 5:
        return datetime.datetime.strftime(cDate,'%Y-%m-%d')
    elif cDate.weekday() == 5:
        cDate = cDate + datetime.timedelta(-1)
        return datetime.datetime.strftime(cDate,'%Y-%m-%d')
    elif cDate.weekday() == 6:
        cDate = cDate + datetime.timedelta(-2)
        return datetime.datetime.strftime(cDate,'%Y-%m-%d')

def getCodeNameList(dataType = 'position'):
    if dataType == 'all':
        dataType = 'stock'
    mongo = MongoIo()
    return mongo.get_stock_list(codeFlg=dataType)

def getCodeList(dataType = 'position', notST = True):
    if dataType == 'stock' or dataType == 'all' or dataType[:3] == 'etf' or dataType[:5]== 'index':
        if dataType == 'all':
            dataType = 'stock'
        mongo = MongoIo()
        return list(mongo.get_stock_list(codeFlg=dataType, notST = notST).index)
#     elif dataType == 'idx':
#         mongo = MongoIo()
#         return list(mongo.get_stock_list(codeFlg='index').index)
#     elif dataType == 'etf':
#         mongo = MongoIo()
#         return list(mongo.get_stock_list(codeFlg='etf').index)
    elif dataType == 'position':
        mongo = MongoIo()
        return list(mongo.get_positions().index)
    elif dataType[:5] == 'days:':
        ## dataType = 'days:2024-01-01:12:tdx_xxxx'
        dts = dataType.split(':')
        mongo = MongoIo()
        date = dts[1]
        nums = dts[2]
        if len(dts) == 4:
            return mongo.day_select_data('day-select-ff',date, int(nums), dts[3])
        else:
            return mongo.day_select_data('day-select-stock',date, int(nums))
#         return list(mongo.get_positions().index)
    else:
        df = pd.read_csv(dataType, sep='\t', encoding='iso-8859-1')
        if len(df) > 1:
            # return list(df['代码'])[:-1]
            return list(df.iloc[:-1,0])
        else:
            return []
#     else:
#         df = pd.read_csv(dataType, sep='\t', encoding='iso-8859-1')
#         if len(df) > 1:
#             # return list(df['代码'])[:-1]
#             return list(df.iloc[:-1,0])
#         else:
#             return []

def getCodelistFromFile(tdxFileName):
  codeDf = pd.read_csv(tdxFileName, sep='\t', encoding='iso-8859-1')
#   return list(codeDf['代码'])[:-1]
  return list(codeDf.iloc[:-1,0])
  
def getCodeListFromMongo(mongo):
#   pool_size = cpu_count()
  return list(mongo.get_stock_list().index)
#   return (pool_size, codelist2dict(codelist, pool_size))
#   subcode_len = math.ceil(len(codelist) / pool_size)
  # executor = ProcessPoolExecutor(max_workers=pool_size * 2)
#   code_dict = {}
#   pool = Pool(cpu_count())
#   for i in range(subcode_len + 1):
#       for j in range(pool_size):
#           x = (i * pool_size + 1) + j
#           if x < len(codelist):
#               if j in code_dict.keys():
#                   # code_dict[j].append(codelist[x])
#                   code_dict[j] = code_dict[j] + [codelist[x]]
#               else:
#                   code_dict[j] = [codelist[x]]

#   return (pool_size, code_dict)

def codelist2dict(codelist, splitNum = 4):
    code_len = len(codelist)
    if splitNum <= 1 or code_len < splitNum :
        return {0: codelist}

    subcode_len = math.ceil(code_len / splitNum)
    code_dict = {}
    for i in range(subcode_len + 1):
        for j in range(splitNum):
            x = (i * splitNum) + j
            if x < code_len:
                if j in code_dict.keys():
                    # code_dict[j].append(codelist[x])
                    code_dict[j] = code_dict[j] + [codelist[x]]
                else:
                    code_dict[j] = [codelist[x]]
    return code_dict

