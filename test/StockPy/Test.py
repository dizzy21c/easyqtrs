

#!委托下单模块示例(python 3.7 32位)

#需要安装pywin32模块，pip install pywin32

#总体说明：调用很简单，载入dll→发出指令→等待结果→解析结果
#需要使用的文件：Stock.dll + Stock.dat + 用户目录（配置文件.ini + 服务器列表.json）
#StockUp.ini，升级配置文件。

import ctypes
import struct
import time
import os
from paho.mqtt import client as mqtt_client
from OemStock import *
import random

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

mqttclt = connect_mqtt()

def Kline(type):  # 是否K线格式
    arr = ["1分钟线", "5分钟线", "15分钟线", "30分钟线", "60分钟线", "日线", "周线", "月线", "季线", "年线", "多日线"]
    x = arr.count(type)
    return x
   
def DoStock(answer):  # 实时全推数据处理量大，建议拷贝数据后，扔到队列去 其它线程去处理
    p_head = cast(answer, POINTER(OEM_DATA_HEAD))
    head  = p_head[0]
    count = head.count
    kind  = head.type
    size  = sizeof(OEM_DATA_HEAD)  # 100 字节

    data = byref(head, size)
    if kind == '代码表':
        # size = sizeof(OEM_STKINFO)
        p_market = cast(data, POINTER(OEM_MARKETINFO))
        market = p_market[0]
        stkInfo = cast(market.stkInfo, POINTER(OEM_STKINFO))  # 转换为指针，方便后续读入
        num = market.num
        mkName = market.name
        for i in range(num):
            s = stkInfo[i]
            label = s.label
            name = s.name
            if i < 2:
                print("%s.%s(%s)" % (mkName, label, name))

        return 1
    elif kind == '实时数据':
        size = sizeof(OEM_REPORT)
        pReport = cast(data, POINTER(OEM_REPORT))
        for i in range(count):
            report = pReport[i]
            tm = time.localtime(report.time)
            tm_str = time.strftime('%Y-%m-%d %H:%M:%S', tm)
            data = dict(
                code=report.label,
                name=report.name,
                open=report.open,
                close=report.last,
                now=report.close,
                price=report.close,
                high=report.high,
                low=report.low,
                buy=report.pricebuy[0],
                sell=report.pricesell[0],
                turnover=report.amount,
                amount=report.amount,
                volume=report.volume,
                bid1_volume=report.volbuy[0],
                bid1=report.pricebuy[0],
                bid2_volume=report.volbuy[1],
                bid2=report.pricebuy[1],
                bid3_volume=report.volbuy[2],
                bid3=report.pricebuy[2],
                bid4_volume=report.volbuy[3],
                bid4=report.pricebuy[3],
                bid5_volume=report.volbuy[4],
                bid5=report.pricebuy[5],
                ask1_volume=report.volsell[0],
                ask1=report.pricesell[0],
                ask2_volume=report.volsell[1],
                ask2=report.pricesell[1],
                ask3_volume=report.volsell[2],
                ask3=report.pricesell[2],
                ask4_volume=report.volsell[3],
                ask4=report.pricesell[3],
                ask5_volume=report.volsell[4],
                ask5=report.pricesell[4],
                date=tm_str[:10],
                time=tm_str[11:],
                datetime=tm_str,
            )
            # print("do mqtt pub", mqtt)
            if mqttclt:
                mqttclt.publish(topic % report.label, str(data))
            # if report.label == 'SH600718' or report.label == 'SZ300950' or report.label == 'SZ300488' or report.label == 'SZ000859':
            #     label = report.label
            #     name = report.name
            #     tm = time.localtime(report.time)
            #     tm_str = time.strftime('%Y-%m-%d %H:%M:%S', tm)
            #     print("\r\n接收到实时数据%s(%s) : time:%s close : %5.2f" % (label, name, tm_str, report.close))
        return 1
    elif kind == '分笔':
        # size = sizeof(OEM_TICK)
        pTrace = cast(data, POINTER(OEM_TICK))
        buf = create_string_buffer(head.len + 1)
        memmove(buf, pTrace, head.len)  # 拷贝到内存

        if head.label == 'SH600000':
            label = head.label
            name = head.name
            print("接收到分时/分笔数据%s(%s) : " % (label, name))
        return 1
    elif Kline(kind):
        size   = sizeof(OEM_KLINE)
        pKline = cast(data, POINTER(OEM_KLINE))
        #buf    = create_string_buffer(head.len + 1)
        #memmove(buf, pKline, head.len)  # 直接拷贝到内存，然后保存，有需要到内存读取

        # 下面的解析非常慢，是否有其它方式更快遍历数据？
        for i in range(count):
            kline = pKline[i]

        label = head.label
        name = head.name
        print("接收到K线(%s)数据%s(%s) 数量 %d : " % (kind, label, name, count))
        return 1
    elif kind == '除权':  # 头部 + 实际内容
        sHead = cast(data, POINTER(OEM_SPLIT_HEAD))
        split = cast(data, POINTER(OEM_SPLIT))
        i = 0
        while i < count:
            h   = sHead[i]  # 取出头部
            num = h.num
            if h.label == 'SH600000':
                label = h.label
                name = h.name
                print("\r\n接收到除权数据%s(%s) : \r\n" % (label, name))
            i += 1
            for j in range(num):
                s = split[i + j]
            i += num

        return 1
    elif kind == '财务':
        pFin = cast(data, POINTER(RCV_FINANCE))
        for i in range(count):
            f = pFin[i]
            if f.label == 'SH600000':
                label = f.label
                name = f.name
                print("\r\n接收到财务数据%s(%s) : \r\n" % (label, name))

        return 1
    elif kind == 'F10资料':  # 代码 + 名称 + 索引 + 文本，是否有更高效的处理方式？
        size = sizeof(OEM_F10INFO)
        h_len = count * size
        h = cast(data, POINTER(OEM_F10INFO))  # 索引
        t = byref(h[0], h_len)
        txt = cast(t, ctypes.c_wchar_p)
        # str = txt.contents.data
        for i in range(count):
            id = h[i]

        if head.label == 'SH600000':
            label = head.label
            name = head.name
            print("\r\n接收到F10数据%s(%s)\r\n" % (label, name))

            # fName = "F10\\" + label + '.f10';  #保存索引备用
            # with open(fName, 'w') as f10:
            #    f10.write(h)

            # fName = "F10\\" + label + '.txt';  #保存文本
            # with open(fName, 'w') as fTxt:
            #    fTxt.write(str)

        return 1
    else:
        print(kind)

#定义自己的回调函数
#回调和发出指令是独立的，发出指令后，不需要等待处理结果。
#主程序需要等待回调函数处理完成，请将结果拷贝到内存后，直接返回。

def Answer(answer, form):    #回调函数：answer 返回结果；form 返回格式（文本、JSON、二进制）
    str = ctypes.cast(answer, ctypes.c_wchar_p );
    if form == '股票数据':
        DoStock(answer)
        return 1
    elif form == "内部指令":
        if str.value == "重新载入 Stock.dll":
            win32api.MessageBox(0, "Stock.dll 有升级，需要重启程序后生效。", "提示信息", win32con.MB_YESNO)
            return 0    #返回 0 ，然后重启您的程序。
        if str.value == "内存不足关闭程序 Stock.dat":
            return 0    #返回 0 ，然后关闭您的程序。
        return 1
    elif form == "股票数据":
        DoStock(answer)
    elif form == "无效请求":
        print(str.value)
    elif form =="提示信息":
	    print(str.value)
    else:
	    print(str.value)
    return 1

if __name__ == "__main__":
    # mqttclt = connect_mqtt()
    print("股票接口诊断模式。\r\n\r\n")

    print("按 q + 回车 退出演示。\r\n\r\n")
    print("正在初始化客户端。\r\n\r\n")
    print("参考调用规范，直接输入申请指令。\r\n\r\n")

    dll    = ctypes.windll.LoadLibrary('./Stock.dll')
    Start  = dll.Start    #注册回调函数。参数 ：需要注册的回调函数
    Ask    = dll.Ask      #发出指令，比如 下单?请求=登录&券商=信达证券。参数 ：指令字符串 + 存放结果缓冲区 + 缓冲区大小(字节)
    Stop   = dll.Stop     #注销

    len    = 10 * 1000 * 1024
    INPUT  = ctypes.c_wchar * len
    answer = INPUT()

    CMPFUNC   = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_wchar_p)  #回调函数创建类型
    _callback = CMPFUNC(Answer)
    Start(_callback)                   #初始化
    ask = "股票数据?请求=初始化&分析软件=软件名称&版本=20210701&等待=1000&编号=1"
    ret = Ask(ask, answer, 2 * len)              
    if ret > 0:
        print(answer.value)            #“&等待=毫秒数”，请求后等待服务器返回结果。
                                       #“&等待=0”，     请求后通过回调函数返回。
    ask = "认证?请求=登录&账号=&密码=&模块=股票数据&等待=10000&编号=2"
    ret = Ask(ask, answer, 2 * len)        
    if ret > 0:
        print(answer.value)

    ask = "股票数据?请求=登录&模块=股票备用&账号=&密码=&等待=10000&编号=20"
    ret = Ask(ask, answer, 2 * len)        
    if ret > 0:
        print(answer.value)
    while True:
        ask = input()
        if ask == 'q':
            break
        # time.sleep(3)
        # ask = "股票数据?请求=实时数据&代码=所有股票&等待=2000&编号=123"
        ret = Ask(ask, answer, 2 * len);  #输入下单指令                
        if ret > 0:
            DoStock(answer)           #指令带 “&等待=毫秒数”，请求后等待服务器返回结果，不推荐使用。
                                      #建议使用回调函数方式无需等待，支持连续请求

    print("正在退出……")
    Stop()        #注销
