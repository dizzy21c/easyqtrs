from QAPUBSUB import consumer


c = consumer.subscriber_routing(user='admin',password='admin',host='192.168.2.116',routing_key='100002', exchange='QAACCOUNT')
c.callback = lambda x, y, body, z: print(z)
c.start()
