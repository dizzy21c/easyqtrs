from paho.mqtt import client as mqtt_client
import random
import time

broker = '127.0.0.1'  # mqtt代理服务器地址
port = 1883
keepalive = 60     # 与代理通信之间允许的最长时间段（以秒为单位）              
topic = "/stock/%s"  # 消息主题
client_id = f'python-mqtt-pub-{random.randint(0, 1000)}'  # 客户端id不能重复

def connect_mqtt():
    '''连接mqtt代理服务器'''
    def on_connect(client, userdata, flags, rc):
        '''连接回调函数'''
        # 响应状态码为0表示连接成功
        if rc == 0:
            print("Connected to MQTT OK!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # 连接mqtt代理服务器，并获取连接引用
    client = mqtt_client.Client(client_id)
    client.username_pw_set('easyqtrs', '1qaz@WSX')
    client.on_connect = on_connect
    client.connect(broker, port, keepalive)
    return client

def publish(client):
    '''发布消息'''
    i = 0
    while True:
        '''每隔4秒发布一次服务器信息'''
        time.sleep(4)
        #msg = get_info()
        result = client.publish(topic % ('SZ000' + str(i)), 'hello,world %d' % i)
        #result = client.publish(topic, msg)
        status = result[0]
        i = i + 1
        if status == 0:
            # print(f"Send `{msg}` to topic `{topic}`")
            pass
        else:
            print(f"Failed to send message to topic {topic}")

client = connect_mqtt()
client.loop_start()
publish(client)

