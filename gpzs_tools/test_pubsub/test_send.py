from QAPUBSUB import producer

c = producer.publisher(exchange='ctp')
while True:
    c.pub('I1111111')
