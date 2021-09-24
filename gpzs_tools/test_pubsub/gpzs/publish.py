# coding=utf-8  
''''' 
Created on 2015-9-9 
 
@author: Administrator 
'''  

#{"code":"600718","num":2000,"p":0,"no":1}

import redis  
pool=redis.ConnectionPool(host='192.168.3.8',port=6379,db=0)  
r = redis.StrictRedis(connection_pool=pool)  
while True:  
    input = raw_input("publish:")  
    if input == 'over':  
        print ('stop publish')  
        break;  
    r.publish('buypub', input)  
