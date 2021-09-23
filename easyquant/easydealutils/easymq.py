
import pika
import json
import random

class EasyMq(object):
  # def __init__(self, , host=host, port=port, user=user, password=password, channel_number=1, queue_name='', routing_key='default',  exchange='', exchange_type='fanout', vhost='/'):
  def __init__(self, host='127.0.0.1', port=5672, user='admin', password='admin', channel_number=1, vhost='/'):
    self.host = host
    self.port = port
    self.user = user
    self.password = password

    # self.queue_name = queue_name
    # self.exchange = exchange
    # self.routing_key = routing_key
    self.vhost = vhost
    # self.exchange_type = exchange_type
    self.channel_number = channel_number
    # fixed: login with other user, pass failure @zhongjy
    credentials = pika.PlainCredentials(
        self.user, self.password, erase_on_connect=True)
    self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost,
                                  credentials=credentials, heartbeat=0, socket_timeout=5,
                                  )
    )

    self.channel = self.connection.channel(
        channel_number=self.channel_number)

  def reconnect(self):
    try:
        self.connection.close()
    except:
        pass

    self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=self.host, port=self.port,
                                  heartbeat=0, virtual_host=self.vhost,
                                  socket_timeout=5,))

    self.channel = self.connection.channel(
        channel_number=self.channel_number)
    return self
    
  
  def init_pub(self, exchange, queue_name = '', exchange_type='direct'):
    self.exchange = exchange
    self.queue_name = queue_name
    # self.routing_key = routing_key
    self.channel.queue_declare(
        self.queue_name, auto_delete=True, exclusive=True)
    self.channel.exchange_declare(exchange=exchange,
                                  exchange_type=exchange_type,
                                  passive=False,
                                  durable=False,
                                  auto_delete=False)
    
  
  def pub(self, text, routing_key):
    # channel.basic_publish向队列中发送信息
    # exchange -- 它使我们能够确切地指定消息应该到哪个队列去。
    # routing_key 指定向哪个队列中发送消息
    # body是要插入的内容, 字符串格式
    if isinstance(text, bytes):
      content_type = 'text/plain'
    elif isinstance(text, str):
      content_type = 'text/plain'
    elif isinstance(text, dict):
      content_type = 'application/json'
    try:
      self.channel.basic_publish(exchange=self.exchange,
        routing_key=routing_key,
        body=text,
        properties=pika.BasicProperties(content_type=content_type,
                                        delivery_mode=1))
    except Exception as e:
        print(e)
        self.reconnect().channel.basic_publish(exchange=self.exchange,
                routing_key=routing_key,
                body=text,
                properties=pika.BasicProperties(content_type=content_type,
                                                delivery_mode=1))

  def exit(self):
      self.connection.close()
      

  def init_receive(self, exchange='', queue='qa_sub.{}'.format(random.randint(0, 1000000)),
                routing_key='default', durable=False):
      # super().__init__(host=host, port=port, user=user, vhost=vhost,
      #                   password=password, exchange=exchange)
      self.exchange = exchange
      self.queue = queue
      self.channel.exchange_declare(exchange=exchange,
                                    exchange_type='direct',
                                    passive=False,
                                    durable=durable,
                                    auto_delete=False)
      self.routing_key = routing_key
      self.queue = self.channel.queue_declare(
          queue='', auto_delete=True, exclusive=True, durable=durable).method.queue
    #   print("queue= %s, self.queue=%s " %(queue, self.queue))
      self.channel.queue_bind(queue=self.queue, exchange=exchange,
                              routing_key=self.routing_key)          # 队列名采用服务端分配的临时队列
      # self.channel.basic_qos(prefetch_count=1)
      self.c = []
  def add_sub_key(self, routing_key):
      # 非常不优雅的多订阅实现
      u = EasyMq()
      u.init_receive(exchange=self.exchange, routing_key=routing_key)
      u.callback = self.callback

      import threading
      self.c.append(threading.Thread(
          target=u.start, daemon=True, group=None))
            
  def add_sub(self, exchange, routing_key):
      # 非常不优雅的多订阅实现
      u = EasyMq()
      u.init_receive(exchange=exchange, routing_key=routing_key)
      u.callback = self.callback

      import threading
      self.c.append(threading.Thread(
          target=u.start, daemon=True, group=None))
      
  def callback(self, chan, method_frame, _header_frame, body, userdata=None):
      print('test ok')
      # print(" [x] %r" % body)

  def subscribe(self):
      if len(self.c) > 0:
          [item.start() for item in self.c]

      self.channel.basic_consume(self.queue, self.callback, auto_ack=True)
      self.channel.start_consuming()

  def start(self):
      try:
          self.subscribe()
      except Exception as e:
          print(e)
          self.start()
    