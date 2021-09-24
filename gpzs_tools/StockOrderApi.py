# encoding: utf-8

#股票自动交易助手 Python 自动下单接口
#把此脚本和 Order.dll 放到你自己编写的脚本同一目录
#如何使用请参考 StockOrder.py

from ctypes import *
 
#加载API库
api = windll.LoadLibrary( 'Order.dll' )

#初始化函数的参数类型
api.Buy1.argtypes=[c_wchar_p, c_int, c_float, c_int, c_int]

api.Sell1.argtypes=[c_wchar_p, c_int, c_float, c_int, c_int]

api.GetPosInfo.restype = c_float
api.GetPosInfo.argtypes=[c_wchar_p, c_int, c_int]

api.GetAccountInfo.restype = c_float
api.GetAccountInfo.argtypes=[c_wchar_p, c_int,  c_int]

api.GetAllPositionCode.restype = c_wchar_p
api.GetAllPositionCode.argtypes=[c_int]

#以下是股票自动交易下单和查持仓等相关函数
def Buy(stkCode, vol, price, formulaNum, ZhuShouHao):
    api.Buy1(stkCode, vol, price, formulaNum, ZhuShouHao)

def Sell(stkCode, vol, price, formulaNum, ZhuShouHao):
    api.Sell1(stkCode, vol, price, formulaNum, ZhuShouHao)

def GetPosInfo(stkCode, nType, nZhuShouHao):
    return api.GetPosInfo(stkCode, nType, nZhuShouHao)

def GetAccountInfo(stkCode, nType, nZhuShouHao):
    return api.GetAccountInfo(stkCode, nType, nZhuShouHao)

def GetAllPositionCode(nZhuShouHao):
    return api.GetAllPositionCode(nZhuShouHao)
