
import zsorder_pb2
from QAPUBSUB import consumer

# from StockOrderApi import *
def Buy(stkCode, vol, price, formulaNum, ZhuShouHao):
    print("buy code=%s, vol=%d, price=%6.2f, no=%d" % (stkCode, vol, price, ZhuShouHao))
    # api.Buy1(stkCode, vol, price, formulaNum, ZhuShouHao)

def Sell(stkCode, vol, price, formulaNum, ZhuShouHao):
    print("sell code=%s, vol=%d, price=%6.2f, no=%d" % (stkCode, vol, price, ZhuShouHao))
    # api.Sell1(stkCode, vol, price, formulaNum, ZhuShouHao)

def GetPosInfo(stkCode, nType, nZhuShouHao):
    pass
    # return api.GetPosInfo(stkCode, nType, nZhuShouHao)

def GetAccountInfo(stkCode, nType, nZhuShouHao):
    pass
    # return api.GetAccountInfo(stkCode, nType, nZhuShouHao)

def GetAllPositionCode(nZhuShouHao):
    pass
    # return api.GetAllPositionCode(nZhuShouHao)

def ucallback(a,b,c,data):
    odata = zsorder_pb2.zsorder()
    try:
        odata.ParseFromString(data)
        bsflg = odata.bsflg
        # 买单个
        if bsflg == 1:
            Buy(odata.code, odata.vol, odata.price, 1, 0)
            # print("buy:")
        # 卖单个
        elif bsflg == 2:
            Sell(odata.code, odata.vol, odata.price, 1, 0)
        elif bsflg == 99:
            print("sell all")
            # 卖所有

    except Exception as e:
        print(e)

c = consumer.subscriber(exchange='zsorder')
c.callback = ucallback
c.start()
