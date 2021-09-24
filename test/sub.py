import json
import sys
import websocket

codes = {"resample": ["002107","600756","002149"], "real": ["002107","600756","002149"]}


def on_message(ws, message):
    """ 收到消息 """
    pp = json.loads(message)
    if pp["topic"] == "auth_result":
        if pp["code"] == 200:
            print("===> 认证成功")
            [ws.send(json.dumps({"topic": "realtime_sub", "room": f"{x}$*$1min"})) for x in codes["resample"]]
            [ws.send(json.dumps({"topic": "realtime_sub", "room": x})) for x in codes["real"]]
        else:
            sys.exit("未认证成功，退出连接")
    elif pp["topic"] == "NotExist":
        print("===> 资源未存在")
    elif pp["topic"] == "realtime_1min_pub":
        print("实时重采样订阅 ===> ", pp["data"])
    elif pp["topic"] == "realtime_real_pub":
        print("实时行情订阅 ===> ", pp["data"])


def on_error(ws, error):
    print("===> 连接错误")


def on_close(ws):
    print("===> 连接意外关闭")


def on_open(ws):
    """  打开ws连接后发起订阅"""
    print("发起订阅")
    auth = dict(topic="auth", key="000000000")
    ws.send(json.dumps(auth))


if __name__ == '__main__':
    ws = websocket.WebSocketApp("ws://quantaxis.tech:10115/ws/",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
