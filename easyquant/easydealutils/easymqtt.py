import random
from paho.mqtt import client as mqtt_client

 
class EasyMqtt(object):
    def __init__(self, mqtt_host = '127.0.0.1', mqtt_port = 1883, on_message = None, mqtt_user = 'easyqtrs', mqtt_pass = '1qaz@WSX', mqtt_keepalive = 600):
        super(EasyMqtt, self).__init__()
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_keepalive = mqtt_keepalive
        self.mqtt_host = mqtt_host
        self.client = mqtt_client.Client()
        self.client.on_connect = self.on_connect
        if mqtt_user is None:
            pass
        else:
            self.client.username_pw_set(mqtt_user, mqtt_pass)
        if on_message is None:
            self.client.on_message = self.on_message
        else:
            self.client.on_message = on_message
        # self.client.on_publish = self.on_publish
        # self.client.on_subscribe = self.on_subscribe
        self.client.connect(mqtt_host, mqtt_port, mqtt_keepalive)  # 600为keepalive的时间间隔
        # client.loop_forever()  # 保持连接
        
    def subscribe(self, topic = None):
        self.client.subscribe(topic)
        
    def start(self, topic = None):
        # self.client.connect(self.mqtt_host, self.mqtt_port, self.mqtt_keepalive)  # 600为keepalive的时间间隔
        if topic is None:
            pass
        else:
            self.client.subscribe(topic)
        self.client.loop_forever()  # 保持连接
    
    def on_connect(self, client, userdata, flags, rc):
        # 响应状态码为0表示连接成功
        if rc == 0:
            print("Connected to MQTT OK!")
        else:
            print("Failed to connect, return code %d\n", rc)
        # print("Connected with result code: " + str(rc))
        # 订阅
        # client.subscribe(self.topic)
 
 
    def on_message(self, client, userdata, msg):
        print("on_message topic:" + msg.topic + " message:" + str(msg.payload.decode('utf-8')))
        
 
    #   订阅回调
    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("On Subscribed: qos = %d" % granted_qos)
        pass
 
    #   取消订阅回调
    def on_unsubscribe(self, client, userdata, mid):
        # print("取消订阅")
        print("On unSubscribed: qos = %d" % mid)
        pass
 
    #   发布消息回调
    def on_publish(self, client, userdata, mid):
        # print("发布消息")
        print("On onPublish: qos = %d" % mid)
        pass
 
    #   断开链接回调
    def on_disconnect(self, client, userdata, rc):
        # print("断开链接")
        print("Unexpected disconnection rc = " + str(rc))
        pass
 
 
if __name__ == '__main__':
    # //'easyqtrs', '1qaz@WSX'
    q = EasyMqtt() #mqtt_user='easyqtrs',mqtt_pass='1qaz@WSX')
    # q.setAuth(username='easyqtrs',password='1qaz@WSX')
    q.subscribe('/stock/SZ000859')
    q.subscribe('/stock/SZ002400')
    # q.start('/stock/#')
    q.start()
