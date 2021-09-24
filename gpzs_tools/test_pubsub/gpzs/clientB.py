# coding=utf-8
'''
@author: zhang
'''
import redis
import json
from StockOrderApi import *

pool=redis.ConnectionPool(host='192.168.3.8',port=6379,db=1)
r = redis.StrictRedis(connection_pool=pool)
p = r.pubsub()
p.subscribe('buypub')
print ('Begin buysubscribe')
for item in p.listen():    
    #print item
    if item['type'] == 'message':  
        data =item['data'] 
        try:
            st = json.loads(data)
            #print st['code'], st['num'], st['p'], st['no'], st['num'] * st['p']
            print ('Data: %s' % data)
            Buy(st['code'], st['num'], st['p'], 1, st['no'])
        except ValueError:
            print ('Data error:', data)

        #print data
        if item['data']=='over':
            break;
p.unsubscribe('buypub')
print ('Cancel Subscribe')
