from QAPUBSUB import consumer

c = consumer.subscriber(exchange='ctp')
c.callback = lambda a,b,c,data: print(data)
c.start()
