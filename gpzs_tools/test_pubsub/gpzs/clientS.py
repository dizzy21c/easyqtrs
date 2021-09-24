# coding=utf-8
'''
@author: zhang
'''
import redis
import json
from StockOrderApi import *

pool=redis.ConnectionPool(host='192.168.56.1',port=6379,db=1)
r = redis.StrictRedis(connection_pool=pool)
p = r.pubsub()
p.subscribe('sellpub')
print 'Begin sellsubscribe'
for item in p.listen():    
    #print item
    if item['type'] == 'message':  
        data =item['data'] 
        st = json.loads(data)
        #print st['code'], st['num'], st['p'], st['no'], st['num'] * st['p']
        print 'Data:', data
        Sell(st['code'], st['num'], st['p'], 1, st['no'])
        #print data
        if item['data']=='over':
            break;
p.unsubscribe('sellpub')
print 'Cancel Subscribe'
