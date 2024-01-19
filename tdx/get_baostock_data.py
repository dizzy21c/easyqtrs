import os.path
import sys
import time
from datetime import datetime, timedelta
import pandas as pd

from func.tdx_func import *
from func.func_sys import *
from easyquant  import MongoIo

import baostock as bs
import pandas as pd

minutes_field = "date,time,code,open,high,low,close,volume,amount,adjustflag"
day_field = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM"
w_m_field = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"
profile_field = 'code,pubDate,statDate,roeAvg,npMargin,gpMargin,netProfit,epsTTM,MBRevenue,totalShare,liqaShare'
WEEK = 'w'
MONTH = 'm'
QFQ = '2'
HFQ = '1'
BFQ = '3'

def fetch_k_day(code="sh.600606", p_begin_day: str = '2023-01-01', p_end_day: str = None):
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg,
    # 换手率\涨跌幅（百分比）\滚动市盈率\市净率\滚动市销率\滚动市现率\
    # 日周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM

    # frequency：数据类型，默认为d，日k线；d = 日k线、w = 周、m = 月、5 = 5
    # 分钟、15 = 15
    # 分钟、30 = 30
    # 分钟、60 = 60
    # 分钟k线数据，不区分大小写；指数没有分钟线数据；周线每周最后一个交易日才可以获取，月线每月最后一个交易日才可以获取

    # adjustflag：复权类型，默认不复权：3；1：后复权；2：前复权。已支持分钟线、日线、周线、月线前后复权
    if p_end_day is None:
        p_end_day = time.strftime('%Y-%m-%d')
    if p_begin_day is None:
        p_begin_day = '2023-01-01'
    else:
        temp = p_begin_day
        p_begin_day = '%s-01-01' % temp
        p_end_day = '%s-12-31' % temp
#     print(p_begin_day, p_end_day)
    rs = bs.query_history_k_data_plus(code,
                                      day_field,
                                      start_date=p_begin_day, end_date=p_end_day,
                                      frequency="d", adjustflag=QFQ)
    data_list = []
#     if rs is None:
#         return pd.DataFrame()
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    # 添加方式
    # result.to_csv(p_file, index=False, mode='a+', header=True)
    return result

if __name__ == '__main__':
    # 登陆系统
    tblName = 'stock_day_qfq'
    lg = bs.login()
    mongo = MongoIo()
    # 显示登陆返回信息
    if lg.error_code != '0':
        print('login respond error_code:' + lg.error_code)
        print('login respond  error_msg:' + lg.error_msg)
        sys.exit()
    testData = mongo.get_table_data(tblName)
    codelist = getCodeList('all')
    for x in codelist:
        if '0' == x[:1]:
            code = "sz.%s" % x
#             print("sz.%s" % x)
        else:
            code = "sz.%s" % x
        codeData = testData.query(" code == '%s'" % x)
        if len(codeData) == 0:
            for ldate in range(1990,2025):
                tdata = fetch_k_day(code, p_begin_day = ldate)
                if len(tdata) > 0:
                    akey = tdata.columns.values
                    ins_data = []
                    for index, row in tdata.iterrows():
                        monv = {}
                        for x in akey:
                            if x == 'code':
                                monv[x] = row[x][3:]
                            elif x == 'date':
                                monv[x] = row[x]
                            else:
                                try:
                                    monv[x] = float(row[x])
                                except:
                                    monv[x] = 0.0
    #                                 print("conv error", code, row)

                        monv['_id'] = '%s-%s' % (row['code'], row['date'])
                        monv['date_stamp'] = mongo.dateStr2stamp('2022-12-12')
    #                     print(monv)
                        ins_data.append(monv)
                    #     print(row.tolist())
                    mongo.save(tblName, ins_data)
        else:
            for ldate in range(1990,2025):
                tdata = fetch_k_day(code, p_begin_day = ldate)
                if len(tdata) > 0:
                    akey = tdata.columns.values
                    ins_data = []
                    for index, row in tdata.iterrows():
                        monv = {}
                        for x in akey:
                            if x == 'code':
                                monv[x] = row[x][3:]
                            elif x == 'date':
                                monv[x] = row[x]
                            else:
                                try:
                                    monv[x] = float(row[x])
                                except:
                                    monv[x] = 0.0
    #                                 print("conv error", code, row)

                        monv['_id'] = '%s-%s' % (row['code'], row['date'])
                        monv['date_stamp'] = mongo.dateStr2stamp('2022-12-12')
    #                     print(monv)
                        ins_data.append(monv)
                    #     print(row.tolist())
                    mongo.save(tblName, ins_data)
            

#                 print("ok", len(tdata))
#                 print(len(tdata))
#                 break
#     print(codelist[:10])