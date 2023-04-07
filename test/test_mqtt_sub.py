from paho.mqtt import client as mqtt_client
import random

broker = '127.0.0.1'  # mqtt代理服务器地址
port = 1883
keepalive = 60     # 与代理通信之间允许的最长时间段（以秒为单位）              
topic = "/stock/#"  # 消息主题
client_id = f'python-mqtt-pub-{random.randint(0, 1000)}'  # 客户端id不能重复

def connect_mqtt():
    '''连接mqtt代理服务器'''
    def on_connect(client, userdata, flags, rc):
        '''连接回调函数'''
        # 响应状态码为0表示连接成功
        if rc == 0:
            print("Connected to MQTT OK!!!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # 连接mqtt代理服务器，并获取连接引用
    client = mqtt_client.Client(client_id)
    client.username_pw_set('easyqtrs', '1qaz@WSX')
    client.on_connect = on_connect
    client.connect(broker, port, keepalive)
    return client

def subscribe(client: mqtt_client):
    '''订阅主题并接收消息'''
    def on_message(client, userdata, msg):
        '''订阅消息回调函数'''
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    # 订阅指定消息主题
    client.subscribe(topic)
    client.on_message = on_message


def run():
    # 运行订阅者
    client = connect_mqtt()
    subscribe(client)
    #  运行一个线程来自动调用loop()处理网络事件, 阻塞模式
    client.loop_forever()


if __name__ == '__main__':
    run()

