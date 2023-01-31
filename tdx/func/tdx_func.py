import pandas as pd
import numpy as np
import math
from easyquant.indicator.base import *
from easyquant.indicator.talib_indicators import CCI
def new_df(df_day, data, now_price):
    code = data['code']
    # now_vol = data['volume']
    last_time = pd.to_datetime(data['datetime'][0:10])
    # print("code=%s, data=%s" % (self.code, self._data['datetime']))
    # df_day = data_buf_day[code]
    # df_day.loc[last_time]=[0 for x in range(len(df_day.columns))]
    df_day.at[(last_time, code), 'open'] = data['open']
    df_day.at[(last_time, code), 'high'] = data['high']
    df_day.at[(last_time, code), 'low'] = data['low']
    df_day.at[(last_time, code), 'close'] = now_price
    df_day.at[(last_time, code), 'volume'] = data['amount'] / 100
    df_day.at[(last_time, code), 'amount'] = data['volume']
    return df_day

# 彩钻花神
def tdx_czhs(data):
    if len(data) < 10:
        data = data.copy()
        data['bflg'] = 0
        data['sflg'] = 0
        return data

    CLOSE=data.close
    C=data.close
    # df_macd = MACD(C,12,26,9)
    # mtj1 = IFAND(df_macd.DIFF < 0, df_macd.DEA < 0, 1, 0)
    # mtj2 = IFAND(mtj1, df_macd.MACD < 0, 1, 0)
    花 = SLOPE(EMA(C, 3), 3)
    神 = SLOPE(EMA(C, 7), 7)
    买 = IFAND(COUNT(花 < 神, 5)==4 , 花 >= 神,1,0)
    卖 = IFAND(COUNT(花 >= 神, 5)==4, 花 < 神,1,0)
    钻石 = IFAND(CROSS(花, 神), CLOSE / REF(CLOSE, 1) > 1.03, 1, 0)
    买股 = IFAND(买, 钻石,1,0)
    return 买股, -1, False

def tdx_hm(data):
    # A1 := ABS(((3.48 * CLOSE + HIGH + LOW) / 4 - EMA(CLOSE, 23)) / EMA(CLOSE, 23));
    # A2 := DMA(((2.15 * CLOSE + LOW + HIGH) / 4), A1);
    # 金线王 := EMA(A2, 200) * 1.118;
    # 条件 := (C - REF(C, 1)) / REF(C, 1) * 100 > 8;
    # 金K线: CROSS(C, 金线王) AND 条件;
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    C = data.close
    H = data.high
    O = data.open

    A1 = ABS(((3.48 * CLOSE + HIGH + LOW) / 4 - EMA(CLOSE, 23)) / EMA(CLOSE, 23))
    A2 = DMA(((2.15 * CLOSE + LOW + HIGH) / 4), A1)
    金线王 = EMA(A2, 200) * 1.118
    条件 = (C - REF(C, 1)) / REF(C, 1) * 100 > 8
    金K线 = IFAND(CROSS(C, 金线王), 条件, True, False)
    return 金K线, -1, False
# 大黑马出笼
def tdx_dhmcl(data):
    CLOSE = data.close
    OPEN = data.open
    C = data.close
    H = data.high
    O = data.open
    # TDX-FUNC
    # QQ := ABS(MA(C, 10) / MA(C, 20) - 1) < 0.01;
    # DD := ABS(MA(C, 5) / MA(C, 10) - 1) < 0.01;
    # QD := ABS(MA(C, 5) / MA(C, 20) - 1) < 0.01;
    # DQ := MA(C, 5) > REF(MA(C, 5), 1) and QQ and DD and QD;
    # QQ1 := (MA(C, 3) + MA(C, 6) + MA(C, 12) + MA(C, 24)) / 4;
    # QQ2 := QQ1 + 6 * STD(QQ1, 11);
    # QQ3 := QQ1 - 6 * STD(QQ1, 11);
    # DD1 := MAX(MAX(MA(C, 5), MA(C, 10)), MAX(MA(C, 10), MA(C, 20)));
    # DD2 := MIN(MIN(MA(C, 5), MA(C, 10)), MIN(MA(C, 10), MA(C, 20)));
    # B: EVERY(OPEN > CLOSE, 3);
    # B9 := "MACD.MACD" > 0;
    # B1 := C / REF(C, 1) > 1.03;
    # ZZ: O <= DD2 and C >= DD1 and REF(C < O, 1) and C > QQ2 and C > QQ1 and QQ1 > O and O / QQ3 < 1.005 and DQ;
    # B2 := SMA(MAX(CLOSE - REF(C, 1), 0), 2, 1) * C * 102;
    # B3 := SMA(ABS(CLOSE - REF(C, 1)), 2, 1) * C * 100;
    # B4 := B2 / B3 * 100 < 10;
    # B5 := B and B4;
    # B6 := MA(C, 5) < REF(MA(C, 5), 1);
    # B7 := REF(MA(C, 5), 4) > REF(MA(C, 5), 5);
    # B8 := (H - C) / C * 100 < 1 and REF((O - C) / C * 100 > 1, 1) and KDJ.J > 25;
    # 大黑马出笼: C > O and B1 and B6 and B7 and B8 and REF(B5, 1) and B9 or ZZ;
    # python
    QQ = ABS(MA(C, 10) / MA(C, 20) - 1) < 0.01
    DD = ABS(MA(C, 5) / MA(C, 10) - 1) < 0.01
    QD = ABS(MA(C, 5) / MA(C, 20) - 1) < 0.01
    DQ = IFAND4(MA(C, 5) > REF(MA(C, 5), 1), QQ, DD, QD, True, False)
    QQ1 = (MA(C, 3) + MA(C, 6) + MA(C, 12) + MA(C, 24)) / 4
    QQ2 = QQ1 + 6 * STD(QQ1, 11)
    QQ3 = QQ1 - 6 * STD(QQ1, 11)
    DD1 = MAX(MAX(MA(C, 5), MA(C, 10)), MAX(MA(C, 10), MA(C, 20)))
    DD2 = MIN(MIN(MA(C, 5), MA(C, 10)), MIN(MA(C, 10), MA(C, 20)))
    # BT1=IFAND3(REF(OPEN,1)>REF(CLOSE,1),REF(OPEN,2)>REF(CLOSE,2),True,False)
    # B = EVERY(OPEN > CLOSE, 3)
    B = IFAND3(O > C, REF(OPEN, 1) > REF(CLOSE, 1), REF(OPEN, 2) > REF(CLOSE, 2), True, False)
    # B9=MACD(C,12,26,9)
    B9 = MACD(C).MACD > 0
    B1 = C / REF(C, 1) > 1.03
    # ZZ = O <= DD2 and C >= DD1 and REF(C < O, 1) and C > QQ2 and C > QQ1 and QQ1 > O and O / QQ3 < 1.005 and DQ
    ZZ1 = IFAND6(O <= DD2, C >= DD1, REF(IF(C < O, 1, 0), 1) > 0, C > QQ2, C > QQ1, QQ1 > O, True, False)
    ZZ = IFAND3(ZZ1, O / QQ3 < 1.005, DQ, True, False)
    B2 = SMA(MAX(CLOSE - REF(C, 1), 0), 2, 1) * C * 102
    B3 = SMA(ABS(CLOSE - REF(C, 1)), 2, 1) * C * 100
    B4 = B2 / B3 * 100 < 10
    # B5 = B and B4
    B5 = IFAND(B, B4, True, False)
    B6 = MA(C, 5) < REF(MA(C, 5), 1)
    B7 = REF(MA(C, 5), 4) > REF(MA(C, 5), 5)
    # B8 = (H - C) / C * 100 < 1 and REF((O - C) / C * 100 > 1, 1) and KDJ.J > 25
    B81 = IFAND((H - C) / C * 100 < 1, REF(IF((O - C) / C * 100 > 1, 1, 0), 1), True, False)
    B8 = IFAND(B81, KDJ(data).KDJ_J > 25, True, False)
    HMTJ1 = IFAND5(C > O, B1, B6, B7, B8, True, False)
    HMTJ2 = IFAND3(HMTJ1, REF(IF(B5, 1, 0), 1) > 0, B9, True, False)
    # 大黑马出笼= C > O and B1 and B6 and B7 and B8 and REF(B5, 1) and B9 OR ZZ
    大黑马出笼 = IFOR(HMTJ2, ZZ, 1, 0)
    return 大黑马出笼, -1, False

def tdx_sxp(data, refFlg = True):
    CLOSE=data.close
    C=data.close
    前炮 = CLOSE > REF(CLOSE, 1) * 1.099
    小阴小阳 = HHV(ABS(C - REF(C, 1)) / REF(C, 1) * 100, BARSLAST(前炮)) < 9
    小阴小阳1 = ABS(C - REF(C, 1)) / REF(C, 1) * 100 < 9
    时间限制 = IFAND(COUNT(前炮, 30) == 1, BARSLAST(前炮) > 5, True, False)
    后炮 = IFAND(REF(IFAND(小阴小阳, 时间限制, 1, 0), 1) , 前炮, 1, 0)
    #return 后炮, -1, True
    if refFlg:
        return REF(后炮,1), -1, True
    else:
        return 后炮, -1, True

# 黑马大肉
def tdx_hmdr(data):
    # C1 := C / REF(C, 1);
    # MX := EMA(SLOPE(C, N2) * 20 + C, N1), LINETHICK1, COLORWHITE;
    # MXR := MX / REF(MX, 1);
    # MR := SLOPE(MX, 2);
    # MRD := CROSS(0, MR);
    # TMR := BARSLAST(MRD);
    # MRR := REF(MX, TMR);
    # MN3 := HHV(MRR, N3);
    # 有肉肉 := CROSS(MX, MRR) and MX / LLV(MX, 55) < 1.35;
    # 大肉1 := CROSS(C, MN3) and C1 > 1.035);
    # 大肉 := CROSS(C, MN3) and C1 > 1.035) and MXR > 1.004;
    #
    # {黑马}
    #
    # A1 := ABS(((3.48 * CLOSE + HIGH + LOW) / 4 - EMA(CLOSE, 23)) / EMA(CLOSE, 23));
    # A2 := DMA(((2.15 * CLOSE + LOW + HIGH) / 4), A1);
    # 金线王 := EMA(A2, 200) * 1.118;
    # 条件 := (C - REF(C, 1)) / REF(C, 1) * 100 > 8;
    # 金K线: CROSS(C, 金线王) and 条件 and 大肉;

    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    C = data.close
    H = data.high
    O = data.open
    N1 = 42
    N2 = 21
    N3 = 89

    C1 = C / REF(C, 1)
    MX = EMA(SLOPE(C, N2) * 20 + C, N1)
    MXR = MX / REF(MX, 1)
    MR = SLOPE(MX, 2)
    MRD = CROSS(0, MR)
    TMR = BARSLAST(MRD)
    MRR = REF(MX, TMR)
    MN3 = HHV(MRR, N3)
    有肉肉 = IFAND(CROSS(MX, MRR) , MX / LLV(MX, 55) < 1.35, True, False);
    # 大肉1 := CROSS(C, MN3) and C1 > 1.035);
    大肉 = IFAND(CROSS(C, MN3), C1 > 1.035, True, False)

    A1 = ABS(((3.48 * CLOSE + HIGH + LOW) / 4 - EMA(CLOSE, 23)) / EMA(CLOSE, 23))
    A2 = DMA(((2.15 * CLOSE + LOW + HIGH) / 4), A1)
    金线王 = EMA(A2, 200) * 1.118
    条件 = (C - REF(C, 1)) / REF(C, 1) * 100 > 8
    金K线 = IFAND3(CROSS(C, 金线王), 条件, 有肉肉, 1, 0)
    # return 金K线, False
    return 大肉, -1, False

def tdx_tpcqpz(data, N = 55, M = 34):
    C = data.close
    CLOSE = data.close
    H = data.high
    HIGH = data.high
    # L = data.low
    HCV = (HHV(C, N) - LLV(C, N)) / LLV(C, N) * 100
    TJN = REF(H, 1) < REF(HHV(H, N), 1)
    XG = IFAND3(REF(HCV, 1) <= M, CLOSE > REF(HHV(HIGH, N), 1), TJN, 1, 0)
    return XG, -1, False

def tdx_A01(data):
    C = data.close
    L = data.low
    H = data.high
    O = data.open
    V = data.volume
    X01 = MA(C, 10) / C > 1.055
    X02 = MA(C, 10) / C < 1.1
    X03 = MA(C, 60) / C > 1.28
    X04 = C / REF(C, 1) > 1.028
    X05 = IFAND(H > L * 1.05 , COUNT(H > L * 1.05, 5) > 3, True, False)
    X06 = O / HHV(C, 30) < 0.78
    X07 = IFAND(V < MA(V, 5) , MA(V, 5) < MA(V, 55), True, False)
    X08 = IF(O == LLV(O, 30), True, False)
    XG1 = IFAND6(X01 , X02 , X03 , X04 , X05 , X06, True, False)
    率土之滨XG = IFAND3(XG1, X07, X08, 1, 0)
    return 率土之滨XG, -1, False

def tdx_jmmm(data):
    # 今买明卖
    C = data.close
    CLOSE = data.close
    LOW = data.low
    HIGH = data.high
    VOL = data.volume
    AMOUNT = data.amount
    ZXNH = True
    M2 = EMA(C,2)
    M18=EMA(C,18)
    # 买点=IF(CROSS(M18,M2),5,0* 10000)
    买点=IF(CROSS(M18,M2),5,0)
    RSVV=(CLOSE-LLV(LOW,10))/(HHV(HIGH,10)-LLV(LOW,10))*100
    VARB2=(RSVV/2+22)
    Q=EMA(VOL,13)
    Y=EMA(AMOUNT,13)
    S=((Y /Q) / 100)
    X=(((CLOSE -S) / S) * 100)
    # F= IFAND(X < (0) , ZXNH, True, False)
    F = X < (0)
    XQ=IFAND(F , RSVV<VARB2-2, True, False)
    XG =IFAND(买点 , XQ, 1, 0)
    return XG, -1, False

# {诺曼底登陆}
def tdx_nmddl(data):
    H = data.high
    L = data.low
    C = data.close
    VAR1=(HHV(H,13)-LLV(L,13))
    VAR2=(HHV(H,13)-C)
    VAR3=(C-LLV(L,13))
    VAR4=VAR2/VAR1*100-70
    VAR5=(C-LLV(L,55))/(HHV(H,55)-LLV(L,55))*100
    VAR6=(2*C+H+L)/4
    VAR7=SMA((VAR3/VAR1*100),3,1)
    VAR8=LLV(L,34)
    VAR9=SMA(VAR7,3,1)-SMA(VAR4,9,1)
    VAR10=IF(VAR9>100,VAR9-100,0)
    VARA=HHV(H,34)
    诺曼底防线=EMA((VAR6-VAR8)/(VARA-VAR8)*100,8)
    BB=EMA(诺曼底防线,5)
    # Q:BB < 20 AND REF(诺曼底防线-BB<0,5) AND REF(诺曼底防线-BB<0,4) AND REF(诺曼底防线-BB<0,3) AND REF(诺曼底防线-BB<0,2) AND REF(诺曼底防线-BB<0,1) {AND 诺曼底防线<30} AND CROSS(诺曼底防线>BB,0.5),LINETHICK0;
    建仓=IF(诺曼底防线-BB>0,1,0)
    # 离场:STICKLINE(诺曼底防线-BB<0,诺曼底防线,BB,3,0),COLORGREEN;
    # 乐滋滋炒股:STICKLINE(诺曼底防线>0 AND 诺曼底防线-BB>=0,2,8,2,0),COLORFF00FF;
    # 休息:STICKLINE(诺曼底防线>0 AND 诺曼底防线-BB<0,2,8,2,0),COLORFFFF00;
    # 警:88,LINETHICK3,COLORRED;
    # 戒:20,LINETHICK3,COLORGREEN;
    # W:0,LINETHICK2,COLORBLUE;
    # 抄吧:STICKLINE(Q,诺曼底防线,Q,3,0),COLOR0066BB;
    # STICKLINE(Q,诺曼底防线,Q,2,0),COLOR0099CC;
    # STICKLINE(Q,诺曼底防线,Q,1,0),COLOR00CCEE;
    # STICKLINE(Q,诺曼底防线,Q,0.1,0),COLOR00FFFF;
    # DRAWTEXT(Q,诺曼底防线,'建'),COLOR0000FF;
    return 建仓, -1, False

def tdx_swl(data):
    # {A42.耍无赖}
    H = data.high
    L = data.low
    C = data.close
    BIAS0 = (C - MA(C, 3)) / MA(C, 3) * 100
    # HXL = V / CAPITAL * 100
    D1 = INDEXC(data)
    # D1 = C
    D2 = MA(D1, 13)
    DR2 = D2 > 1.050 * D1
    # E1 = (C - HHV(C, 13)) / HHV(C, 13) * 10
    E2 = (C - REF(C, 21)) / REF(C, 21) * 10
    # E3 = MA(C, 3)
    SJ1 = DR2
    SJ2 = E2 < -2.30
    SJ3 = BIAS0 < -2.7
    SJ5 = IFAND3(SJ1, SJ2, SJ3, True, False)
    SJ6 = CROSS(0.5, SJ5)
    JS1 = CROSS(SJ6, 0.5)
    JS2 = BARSLAST(JS1==1)
    JS3 = IFAND(JS2 <= 5, C < REF(C, JS2), True, False)
    TJ = IFOR(SJ6, JS3, True, False)
    耍无赖XG = IFAND(TJ == 0,   REF(TJ==1, 1), 1, 0)
    return 耍无赖XG, -1, False

def tdx_func1(data):
    C = data.close
    CLOSE = data.close
    HIGH = data.high
    LOW = data.low
    AA = MA(C, 20)
    BB = MA(C, 60)
    CC = MA(C, 30)
    DIF = EMA(CLOSE, 6) - EMA(CLOSE, 13)
    DEA = EMA(DIF, 5)
    VAR1 = (2 * CLOSE + HIGH + LOW) / 4
    VAR2 = LLV(LOW, 5)
    VAR3 = HHV(HIGH, 5)
    VAR4 = EMA((VAR1 - VAR2) / (VAR3 - VAR2) * 100, 5)
    MA1 = MA(VAR4, 2)
    XG1 = IFOR(CROSS(22.50, MA1), CROSS(24.5, MA1), True, False)
    XG2 = IFAND5(XG1, COUNT(CROSS(0, DEA), 6) == 1 , AA > BB ,  BB > REF(BB, 1) , C / REF(C, 1) < 1.016, True, False)
    XG = IFAND3(XG2, C / REF(C, 1) > 0.993, AA > CC, 1, 0)
    return XG, -1, False

def tdx_yaogu(data):
    ##妖股公式
    C = data.close
    OPEN = data.open
    # CLOSE = data.close
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    VAR0 = (3 * (SMA(((C - LLV(LOW,21)) / (HHV(HIGH,34) - LLV(LOW,21))) * 100,5,1))) - (2 * (SMA(SMA(((C - LLV(LOW,21)) / (HHV(HIGH,13) - LLV(LOW,8))) * 100,5,1),3,1)))
    VAR1 = 10
    VAR2 = MA(C,5)
    VAR3 = MA(C,10)
    VAR4 = VAR2 > VAR3
    VAR5 = ((OPEN + HIGH) + LOW) / 3
    VAR6 = EMA(VAR5,4)
    VAR7 = C * VOL
    VAR8 = EMA(((((EMA(VAR7,3) / EMA(VOL,3)) + (EMA(VAR7,6) / EMA(VOL,6))) + (EMA(VAR7,12) / EMA(VOL,12))) + (EMA(VAR7,24) / EMA(VOL,24))) / 4,13)
    VAR9 = VAR6 > VAR8
    # FLCS = CROSS(VAR0,VAR1) AND VAR4,COLORMAGENTA
    XG1 = IFAND(CROSS(VAR0, VAR1), VAR4, True, False)
    # result=pd.DataFrame({"cross":CROSS(VAR0, VAR1), "var4":VAR4, "var9": VAR9})
    # FLCS = CROSS(VAR0,VAR1) AND VAR4,COLORMAGENTA
    # result['FLCS'] = result.apply(lambda x : x['cross'] > 0 and x['var4'], axis=1)
    # FLTP = (CROSS(VAR0,VAR1) AND VAR4) AND VAR9,COLORRED,LINETHICK2
    # result['FLTP'] = result.apply(lambda x : x['cross'] > 0 and x['var4'] and x['var9'], axis=1)
    XG2 = IFAND3(CROSS(VAR0, VAR1), VAR4, VAR9, True, False)
    return IFOR(XG1, XG2, 1, 0), -1, False

def tdx_niugu(data, n1 = 36, n2 = 30, n3 = 25):
    C = data.close
    H = data.high
    L = data.low
    VOL = data.volume
    AMOUNT = data.amount
    # C, H, L, VOL, AMOUNT
    # if len(C) > n1:
    #     return False

    # L = data_df.low
    # H = data_df.high
    # C=data_df.close
    # VOL=data_df.volume
    VARR24=LLV(L,n1)
    VARR25=HHV(H,n2)
    VARR26=EMA((C-VARR24)/(VARR25-VARR24)*4,4)*n3
    VARB27=(((C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100)/2+22)*1
    VARB28=(((C -(((EMA(AMOUNT*100,13) /EMA(VOL,13)) / 100))) / (((EMA(AMOUNT*100,13) /EMA(VOL,13)) / 100))) * 100)
    # JD=((VARB28 < (0)) AND ((C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100)<VARB27-2 AND VARR26<10
    # JD1 = (VARB28 < (0))
    # JD2 = ((C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100)<VARB27-2
    # JD3 = VARR26<10
    # JD4=IFAND(JD1,JD2,JD1,False)
    JD=IFAND3((VARB28 < (0)),((C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100)<VARB27-2,VARR26<10,True, False)
    CD=IF(JD,20,0)
    AAA=REF(CD,1)>0
    # BBB=CD=0
    # DR=AAA AND BBB
    # return JD OR DR
    RTN=IFOR(JD, AAA, 1, 0)
    # lrtn = len(RTN)
    return RTN, -1, False

# 不二法门
def tdx_buerfameng(data):
    C = data.close
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount
    X_1=VOL/((HIGH-LOW)*2-ABS(CLOSE-OPEN))*(CLOSE-OPEN)
    X_2=X_1/20/1.15
    X_3=X_2*0.55+REF(X_2,1)*0.33+REF(X_2,2)*0.22
    X_4=EMA(X_3,3)
    X_5=X_4*1/10000
    X_6=EMA(X_5,5)
    X_7=CROSS(X_5,X_6)
    X_8=FILTER(X_7,5)
    X_9 = REF(HIGH,BARSLAST(X_8==1))
    X_10 = REF(LOW,BARSLAST(X_8==1))
    #STICKLINE(CLOSE>0,REF(HIGH,BARSLAST(X_8==1)),REF(LOW,BARSLAST(X_8==1)),4,N),COLORGRAY
    # DRAWKLINE(HIGH,OPEN,LOW,CLOSE)
    罪恶滔天=MA((LOW+HIGH+CLOSE)/3,4) #,COLORRED,DOTLINE
    # DRAWICON(CROSS(C,罪恶滔天) ,L*0.988,1)
    # XG = CROSS(C,罪恶滔天)
    XG = IFAND(CROSS(C, 罪恶滔天), (X_6 + 1) > 0.9, 1, 0)
    return XG, -1, False

def tdx_a06_zsd(data):
    # {A06.钻石底}
    C = data.close
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount

    VBR = C < REF(C, 4)
    # NT0 = BARSLASTCOUNT(VBR)
    NT0 = BARSLAST(VBR)
    TJ21 = NT0 == 6
    底6 = COUNT(NT0==6, 5) == 1
    VBR1 = DMA(CLOSE, VOL / SUM(VOL, 34))
    VBR2 = DMA(CLOSE, VOL / SUM(VOL, 13))
    VBR3 = (CLOSE - VBR1) / VBR1 * 100
    VBR4 = (CLOSE - VBR2) / VBR2 * 100
    Y1 = IFAND(VBR4 <= -17, VBR3 <= -25, True, False)
    # 去除ST = IF(NAMELIKE('ST') or NAMELIKE('*ST'), 0, 1)
    # 去除停牌 = DYNAINFO(4) > 0
    # 去除 = 去除ST and 去除停牌
    # Q10 = 底6 and Y1 and 去除
    Q1 = IFAND(底6, Y1, True, False)
    超卖区 = MA((CLOSE - MA(CLOSE, 40)) / MA(CLOSE, 40) * 100, 2)
    Q2 = 超卖区 < -20
    钻石底XG = IFAND4(Q1, Q2, C > REF(C, 1) * 0.91, C < REF(C, 1), True, False)
    XG = IFAND3(钻石底XG, INDEXC(data) < REF(INDEXC(data), 1) ,  REF(C > REF(C, 1), 1), 1, 0)
    return XG, -1, False

def tdx_a12_zsd(data):
    # {A12.短线黑马}
    C = data.close
    O = data.open
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount
    VAR1C=DMA(C,VOL/MA(VOL,4)/4)
    VAR2C=DMA(C,VOL/MA(VOL,33)/33)
    VAR3C=(C-VAR1C)/VAR1C*100<-11
    VAR4C=(VAR1C-VAR2C)/VAR2C*100<-22.3
    VAR5C=IFAND3(VAR3C, VAR4C, COUNT(C != O,7), True, False)
    VAR6C=DMA(C,VOL/MA(VOL,3)/3)
    VAR7C=DMA(C,VOL/MA(VOL,33)/33)
    VAR8C=(C-VAR6C)/VAR6C*100<-5
    VAR9C=(VAR6C-VAR7C)/VAR7C*100<-18
    VARDC=IFAND3(VAR8C , VAR9C , (O-REF(C,1))/REF(C,1)>-0.05, True, False)
    VAREC=IFAND(VARDC , COUNT(VARDC,2)==1, True, False)
    DXHM=IFOR(VAR5C, VAREC, True, False)
    趋势=SMA(MAX(C-REF(C,1),0),8,1)/SMA(ABS(C-REF(C,1)),8,1)
    HMA=CROSS(趋势,0.15)
    X_21=(C-MA(C,25))/MA(C,45)*123
    BAME=IFAND(CROSS(X_21,(-25)), C>REF(C,1), True, False)
    HJ_1=C/MA(C,40)
    HJ_2=C/MA(C,60)*100<71
    MOGU=CROSS(HJ_1,HJ_2)
    短线黑马XG = IFOR(IFAND(DXHM ,HMA, True, False), IFAND(BAME, MOGU, True, False), 1, 0)
    return 短线黑马XG, -1, False

def tdx_a13_zsd(data):
    # {A12.短线黑马}
    C = data.close
    O = data.open
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount

def tdx_a16_zsd(data):
    # {A12.短线黑马}
    C = data.close
    O = data.open
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount

def tdx_a20_zsd(data):
    # {A12.短线黑马}
    C = data.close
    O = data.open
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount

def tdx_a28_fscd(data):
    # {A28.福树抄底}
    C = data.close
    CLOSE = data.close
    DIF = EMA(CLOSE, 12) - EMA(CLOSE, 26)
    DEA = EMA(DIF, 9)
    MACD = (DIF - DEA) * 2
    MACD_TJ = IFAND(MACD > 0, COUNT(CROSS(DIF, DEA), 5) > 0 , True, False)
    A1 = C * 1.2 < MA(C, 60)
    A2 = C / REF(C, 1) > 1.03
    福树抄底XG = IFAND3(A1, A2, MACD_TJ, 1, 0)
    return 福树抄底XG, False

def tdx_a29_zsd(data):
    # {A12.短线黑马}
    C = data.close
    O = data.open
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount

def tdx_a34_zsd(data):
    # {A12.短线黑马}
    C = data.close
    O = data.open
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount


def tdx_a38_zsd(data):
    # {A12.短线黑马}
    C = data.close
    O = data.open
    CLOSE = data.close
    OPEN = data.open
    HIGH = data.high
    LOW = data.low
    VOL = data.volume
    # AMOUNT = data.amount

def tdx_yaoguqidong(data):
    # {妖股启动}
    C = data.close
    H = data.high
    L = data.low

    VAR1 = (C - REF(C, 1)) / REF(C, 1)
    VAR2 = (INDEXC(data) - REF(INDEXC(data), 1)) / REF(INDEXC(data), 1)
    个股 = EMA(SUM(VAR1, 20), 5)
    大盘 = EMA(SUM(VAR2, 20), 5)
    领涨 = (个股 - 大盘) >= 0
    VAR3 = (C - LLV(L, 125)) / (HHV(H, 125) - LLV(L, 125)) * 100
    VAR4 = SMA(VAR3, 72, 1)
    VAR5 = SMA(VAR4, 34, 1)
    中线趋势 = 3 * VAR4 - 2 * VAR5
    中线趋势升 = (中线趋势 - REF(中线趋势, 1)) >= 0
    均五升 = (MA(C, 5) - REF(MA(C, 5), 1)) >= 0
    均十升 = (MA(C, 10) - REF(MA(C, 10), 1)) >= 0
    强势 = IFAND4(均五升 , 均十升 , 中线趋势升 , 领涨, 10, 0)
    VAR6 = (2 * C + H + L) / 4
    VAR7 = LLV(L, 27)
    VAR8 = HHV(H, 27)
    操作 = EMA((VAR6 - VAR7) / (VAR8 - VAR7) * 100, 13) - 50
    趋势 = EMA(0.618 * REF(操作, 1) + 0.382 * 操作, 3)
    运动 = IFAND5(操作 >= 趋势 , 均五升 , 均十升 , 中线趋势升 , 趋势 < 0, 1, 0)
    买进 = IFAND(运动==1 , COUNT(运动==1, 5) == 1, 8, 0)
    BIAS1 = (C - MA(C, 6)) / MA(C, 6) * 100
    BIAS2 = (C - MA(C, 12)) / MA(C, 12) * 100
    BIAS3 = (C - MA(C, 24)) / MA(C, 24) * 100
    BIAS = (BIAS1 + 2 * BIAS2 + 3 * BIAS3) / 6
    乖离 = MA(BIAS, 3)
    妖股启动 = IFAND(买进==8 , COUNT(乖离 < -12, 10) >= 1, 1, 0)
    return 妖股启动, -1, False

def tdx_zyyj_5min(data):
    # {自用的5分钟预警}
    C = data.close
    H = data.high
    L = data.low
    O = data.open
    VOL = data.volume

    DP = INDEX(data).volume
    LB1 = VOL / REF(SUM(VOL, 5), 1)
    LB2 = DP / REF(SUM(DP, 5), 1)
    ST = EXIST(C / REF(C, 1) > 1.06, 60)
    # LT = (CAPITAL / 100) / 10000 <= 10
    LT = True
    # AA = O / DYNAINFO(3)
    AA = O / C
    A1 = LB1 / LB2
    JD1 = ATAN((MA(C, 5) / REF(MA(C, 5), 1) - 1) * 100) * 57.3
    JD2 = ATAN((MA(C, 15) / REF(MA(C, 15), 1) - 1) * 100) * 57.3
    PX = JD1 > 45, JD2 > 17
    Z2 = AA > 1, AA < 1.05
    # XG: ST = 0, LT, Z2, PX, A1 > 3.5

def tdx_ygqd_test(data):
    # {妖股启动}
    C = data.close
    CLOSE = data.close
    HIGH = data.high
    H = data.high
    L = data.low
    LOW = data.low
    OPEN = data.open
    O = data.open
    VOL = data.volume

    # VAR1 = EMA(SMA((CLOSE - LLV(LOW, 19)) / (HHV(HIGH, 19) - LLV(LOW, 19)) * 100, 8, 1), 3)
    # STICKLINE(VAR1 > 20, VAR1 < 80, VAR1, VAR1, 10, 1), COLORRED
    # STICKLINE(VAR1 < REF(VAR1, 1), VAR1, VAR1, 10, 1), COLORFFCC66
    # STICKLINE(VAR1 > 80, VAR1, VAR1, 8, 1)
    # STICKLINE(VAR1 < 20, VAR1, VAR1, 8, 1), COLORYELLOW
    ABV = MA(SUM(IF(CLOSE > REF(CLOSE, 1), VOL, IF(CLOSE < REF(CLOSE, 1), -VOL, 0)), 0) / 25000, 2)
    # M1 = EMA(ABV, 12)
    M2 = EMA(ABV, 26)
    MTM = CLOSE - REF(CLOSE, 1)
    MMS = ((100) * (EMA(EMA(MTM, 6), 6))) / (EMA(EMA(ABS(MTM), 6), 6))
    MMM = ((100) * (EMA(EMA(MTM, 12), 12))) / (EMA(EMA(ABS(MTM), 12), 12))
    MML = ((100) * (EMA(EMA(MTM, 26), 26))) / (EMA(EMA(ABS(MTM), 26), 26))
    MMA = C - REF(C, 1)
    MMB = 100 * EMA(EMA(MMA, 9), 9) / EMA(EMA(ABS(MMA), 9), 9)
    MMC = MA(MMB, 5)
    # A = ((VOL) / (CAPITAL(data))) * (100)
    # S = ((MA(A, 30)) / (MA(INDEX(data).amount, 10))) * (MA(INDEX(data).amount, 60))
    # Y = ((MA(A, 120)) / (MA(INDEX(data).amount, 10))) * (MA(INDEX(data).amount, 60))
    # X = 1
    V1 = (HIGH + OPEN + LOW + (2) * (CLOSE)) / (5)
    V2 = REF(V1, 1)
    V3 = MAX(V1 - V2, 0)
    V4 = ABS(V1 - V2)
    V5 = SMA(V3, 10, 1)
    V6 = SMA(V4, 10, 1)
    V8 = COUNT(((V5) / (V6) < 0.2), 5)
    V9 = COUNT((LLV(V1, 10)==V1), 10)
    # 主力进出 = IFAND6(MMS > REF(MMS, 1), MMB > REF(MMB, 1), CROSS(ABV, M2), ABV > REF(ABV, 1)
    #               , M1 > REF(M1, 1), M2 > REF(M2, 1), True, False)
    # 主进主轨 = IFAND3(ABV > M2, CROSS(ABV, M1), CROSS(MMB, MMC), True, False)
    精准买卖1 = IFAND5(V8 >= 1, V9 >= 1, CLOSE > OPEN, REF(CLOSE, 1) > REF(OPEN, 1), (VOL > REF(VOL, 1)), True, False)
    精准买卖 = IFAND3(精准买卖1, MMS > MML, CROSS(ABV, M2), True, False)
    短线买点1 = IFAND5(V8 >= 1, V9 >= 1, CLOSE > OPEN, REF(CLOSE, 1) > REF(OPEN, 1), (VOL > REF(VOL, 1)), True, False)
    短线买点 = IFAND3(短线买点1, CROSS(MMS, MML), ABV > REF(ABV,1), True, False)
    中线买点1 = IFAND6(V8 >= 1, V9 >= 1, CLOSE > OPEN, REF(CLOSE, 1) > REF(OPEN, 1), (VOL > REF(VOL, 1)), ABV > REF(ABV, 1), True, False)
    中线买点 = IFAND6(中线买点1, MMS > MML, CROSS(MMM, MML), MMS > REF(MMS, 1), MMM > REF(MMM, 1), MML > REF(MML, 1), True, False)
    主进主买 = IFAND6(ABV > M2, MMB > MMC, CROSS(MMS, MML), MMS > REF(MMS, 1), MMM > REF(MMM, 1), MML > REF(MML, 1), True, False)
    短中精 = IFOR4(精准买卖, 短线买点, 中线买点, 主进主买, True, False)
    主力买卖 = IF(短中精, 1, 0)
    主力轨迹 = IFAND5(ABV > M2, MMS > MML, CROSS(MMB, MMC), MMB > REF(MMB, 1), MMC > REF(MMC, 1), 1, 0)
    # 拉升在即 = IFAND5(S < X, Y < X, MMS > MML, ABV > M1, CROSS(S, Y), 1, 0)
    底部构成1 = IFAND5(V8 >= 1, V9 >= 1, CLOSE > OPEN, REF(CLOSE, 1) > REF(OPEN, 1), VOL > REF(VOL, 1), True, False)
    # 底部构成 = IFAND3(底部构成1, ABV > M2, MMB > MMC, 1, 0)
    ROC = (CLOSE - REF(CLOSE, 12)) / REF(CLOSE, 12) * 100
    HSL = 100 * VOL / CAPITAL(data)
    冲击波 = IFAND(CROSS(ROC, 16), HSL > 3.5, 1, 0)
    macdV=MACD(data.close)
    CONF1 = IFOR(CROSS(macdV.DIFF, macdV.DEA), IFAND(macdV.MACD > 0, macdV.MACD < 0.5, True, False), True, False)
    CONF2 = IF(主力买卖 > 0, True, False)
    # CONF3 = IF(主力进出 > 0, True, False)
    CONF4 = IF(主力轨迹 > 0, True, False)
    CONF5 = IF(冲击波 > 0, True, False)
    CONF11 = IFAND(EXIST(CONF2, 5), BARSLAST(CONF2) > BARSLAST(CONF5), True, False)
    # CONF12 = IFAND(EXIST(CONF3, 5), BARSLAST(CONF3) > BARSLAST(CONF5), True, False)
    CONF13 = IFAND(EXIST(CONF4, 5), BARSLAST(CONF4) > BARSLAST(CONF5), True, False)
    CONF21 = IFAND(MA(C, 5) > MA(C, 10), MA(C, 5) > MA(C, 60), True, False)
    CONF22 = FINANCE(data, 40) / 100000000 < 60
    CONF23 = IFAND3(L > MA(C, 5), ABS((H - MAX(C, O)) / (O - C)) < 0.5, ABS((MIN(O, C) - L) / (C - O)) < 0.5, True, False)
    BS1 = IFOR(CONF11, CONF13, True, False)
    BS2 = IFAND3(CONF21, CONF22, CONF23, True, False)
    XG = IFAND4(EXIST(CONF1, 5), EXIST(CONF5, 3), BS1, BS2, 1, 0)
    return XG, -1, True

def tdx_blftxg(data):
    # 暴利副图选股
    C = data.close
    CLOSE = data.close
    HIGH = data.high
    H = data.high
    L = data.low
    LOW = data.low
    OPEN = data.open
    VOL = data.volume
    # X_1 = MA(CLOSE, 5)
    # X_2 = MA(CLOSE, 10)
    # X_3 = MA(CLOSE, 20)
    # X_4 = MA(CLOSE, 30)
    # X_5 = MA(CLOSE, 60)
    # X_6 = MA(CLOSE, 120)
    # X_7 = MA(CLOSE, 240)
    X_8 = (REF(CLOSE, 3) - CLOSE) / REF(CLOSE, 3) * 100 > 5
    X_9 = FILTER(X_8, 10)
    X_10 = BARSLAST(X_9)
    X_11 = REF(HIGH, X_10 + 2)
    X_12 = REF(HIGH, X_10 + 1)
    X_13 = REF(HIGH, X_10)
    X_14 = MAX(X_11, X_12)
    X_15 = MAX(X_14, X_13)
    X_16 = (CLOSE - REF(CLOSE, 1)) / REF(CLOSE, 1) * 100 > 5
    X_17 = X_10 < 150
    X_18 = (OPEN - X_15) / X_15 * 100 < 30
    X_19 = (CLOSE - LLV(LOW, X_10)) / LLV(LOW, X_10) * 100 < 50
    X_20 = (CLOSE - REF(OPEN, 5)) / REF(OPEN, 5) * 100 < 30
    X_21 = VOL / MA(VOL, 5) < 3.5
    X_22 = (CLOSE - REF(CLOSE, 89)) / REF(CLOSE, 89) * 100 < 80
    # X_23 = (CLOSE - REF(CLOSE, 1)) / REF(CLOSE, 1) * 100 >= 5, (CLOSE - OPEN) / (HIGH - CLOSE) > 3, VOL / MA(VOL, 5) > 1.3

    X_25 = X_16, X_17, X_18, X_19, X_20, X_21, X_22
    # 暴利 = IFAND(FILTER(X_25, 15), 主力买卖, 1, 0)
    暴利 = IF(FILTER(X_25, 15), True, False)

    BL = MA(CLOSE, 125)
    HL = BL + 2 * STD(CLOSE, 170)
    ZL = BL - 2 * STD(CLOSE, 145)
    # QL = SAR(125, 1, 7)
    VAR2 = HHV(HIGH, 70)
    VAR3 = HHV(HIGH, 20)
    KL = VAR2 * 0.83
    LL = VAR3 * 0.91
    # 见龙 = IFAND(CROSS(LL, HL), 主力买卖, 1, 0)
    见龙 = IF(CROSS(LL, HL), True, False)
    return IFOR(暴利, 见龙, 1, 0), -1, False

def tdx_cptlzt(data):
    # 操盘铁律主图
    # pass
    C = data.close
    CLOSE = data.close
    HIGH = data.high
    H = data.high
    L = data.low
    LOW = data.low
    OPEN = data.open
    O = data.open
    VOL = data.volume
    AMOUNT = data.amount

    MID = (3 * CLOSE + LOW + OPEN + HIGH) / 6
    牛线 = (20 * MID + 19 * REF(MID, 1) + 18 * REF(MID, 2) + 17 * REF(MID, 3) + 16 * REF(MID, 4) + 15 * REF(MID, 5)
          + 14 * REF(MID, 6) + 13 * REF(MID, 7) + 12 * REF(MID, 8) + 11 * REF(MID, 9) + 10 * REF(MID, 10)
          + 9 * REF(MID, 11) + 8 * REF(MID, 12) + 7 * REF(MID, 13) + 6 * REF(MID, 14) + 5 * REF(MID, 15)
          + 4 * REF(MID, 16) + 3 * REF(MID, 17) + 2 * REF(MID, 18) + REF(MID, 20)) / 210
    马线 = MA(牛线, 6)
    乖离率 = (C - 牛线) / C * 100
    涨停=IF((C-REF(C,1))/REF(C,1)>0.097,1,0)
    跌停 = IF((REF(C, 1) - C) / C > 0.097, 1, 0)
    KP = SMA(AMOUNT, 10, 1) / 10000
    VAR11 = REF(KP, 1)
    VAR21 = REF(KP, 2)
    VAR31 = REF(KP, 3)
    涨停复制1= IFAND6(C >= 牛线, 牛线 > 马线, 乖离率 >= 0, 乖离率 <= 4, COUNT(KP > VAR11, 1), VAR11 > VAR21, True, False)
    涨停复制= IFAND3(涨停复制1, VAR21 > VAR31,  COUNT(((CLOSE - REF(CLOSE, 1)) / REF(CLOSE, 1)) > 0.099, 13) >= 1, True, False)
    VAR0 = SMA(MAX(CLOSE - REF(C, 1), 0), 12, 1) / SMA(ABS(CLOSE - REF(C, 1)), 15, 1) * 100
    快卖 = CROSS(82, VAR0)
    S = C - REF(C,1)
    DX = 100*EMA(EMA(S,6),6)/EMA(EMA(ABS(S),6),6)
    买 = IFAND3(LLV(DX,2)==LLV(DX,7) , COUNT(DX<0,2) , CROSS(DX,MA(DX,2)),1,0)
    拉升 = FILTER(买==1,5)
    DA=(EMA(C,1)+EMA(C,2)+EMA(C,3)+EMA(C,4))/4
    DB=(EMA(C,10)+EMA(C,20)+EMA(C,40)+EMA(C,80))/4
    ICON7 = CROSS(DA-DB,0)
    JH=SMA(MAX(C-REF(C,1),0),5,1)/SMA(ABS(C-REF(C,1)),5,1)*100
    ICON7 = CROSS(84,JH)
    E = (HIGH + LOW + OPEN + 2 * CLOSE) / 5
    明日阻力 = 2 * E - LOW
    明日支撑 = 2 * E - HIGH
    明日突破 = E + (HIGH - LOW)
    明日反转 = E - (HIGH - LOW)
    今日阻力 = REF(明日阻力, 1)
    今日支撑 = REF(明日支撑, 1)
    A = IFAND(HHV(HIGH, 13) == HIGH, HIGH > REF(HIGH, 1), True, False)
    A1 = FILTER(A, 12)
    B = IFAND(LLV(LOW, 13) == LOW, LOW < REF(LOW, 1), True, False)
    B1 = FILTER(B, 12)
    TS1 = BARSLAST(A1)
    箱顶 = REF(HIGH, TS1)
    TS2 = BARSLAST(B1)
    箱底 = REF(LOW, TS2)
    箱高 = 100 * (箱顶 - 箱底) / 箱底
    均价 = (3 * C + H + L + O) / 6
    VAR1 = (8 * 均价 + 7 * REF(均价, 1) + 6 * REF(均价, 2) + 5 * REF(均价, 3) +
            4 * REF(均价, 4) + 3 * REF(均价, 5) + 2 * REF(均价, 6) + REF(均价, 8)) / 36
    VAR2 = (LLV(VAR1, 2) + LLV(VAR1, 4) + LLV(VAR1, 6)) / 3
    SZ1 = IFAND3(REF(VAR1, 1) == REF(VAR2, 1), VAR1 > VAR2, CLOSE > VAR1, True, False)
    SZ2 = IFAND6(VAR1 > VAR2, VAR1 > REF(VAR1, 1), VAR2 > REF(VAR2, 1), H / VAR1 < 1.1, L > VAR2, CLOSE > VAR1, True, False)
    SZ3 = IFAND4(VAR1 > VAR2, VAR1 > REF(VAR1, 1), VAR2 >= REF(VAR2, 1), H / VAR1 > 1.1, True, False)
    SZ4 = IFAND5(VAR1 > VAR2, VAR1 > REF(VAR1, 1), VAR2 > REF(VAR2, 1), CLOSE > VAR2, CLOSE < VAR1, True, False)
    
    SZ51 = IFAND4(VAR1 > VAR2, VAR2 > REF(VAR2, 1), VAR1 != REF(VAR1, 1), CLOSE < VAR2, True, False)
    SZ52 = IFAND4(VAR1 > VAR2, VAR1 < REF(VAR1, 1), VAR2 < REF(VAR2, 1), CLOSE < VAR2, True, False)
    SZ5 = IFOR(SZ51, SZ52, True, False)
    # OR(VAR1 > VAR2, VAR1 < REF(VAR1, 1), VAR2 < REF(VAR2, 1), CLOSE < VAR2)
    SZ6 = IFAND3(REF(VAR1, 1) > REF(VAR2, 1), VAR1 == VAR2, CLOSE < VAR2, True, False)
    XD11 = IFAND4(VAR1 < REF(VAR1, 1), VAR2 < REF(VAR2, 1), REF(VAR1, 1) == REF(VAR2, 1), CLOSE < VAR2, True, False)
    XD1 = IFAND(VAR1 == VAR2, IFOR(CLOSE < VAR2, XD11, True, False), True, False)
    XD2 = IFAND(VAR1 == VAR2, CLOSE > VAR1, True, False)
    
    SAT = (AMOUNT / C) / (HHV(AMOUNT, 20) / HHV(C, 20))
    量能饱和度 = IF(SAT > 1, 1, SAT) * 100
#     return 量能饱和度, -1, False
    return (SZ1, SZ2, SZ3, SZ4, SZ5, SZ6, XD11, XD1, XD2)
    # DRAWTEXT_FIX(BARSTATUS=2 AND SZ1,0.8,0.05,0,'调整结束短线介入'),COLORRED;
    # DRAWTEXT_FIX(BARSTATUS=2 AND SZ2,0.8,0.05,0,'上升通道走势良好'),COLORRED;
    # DRAWTEXT_FIX(BARSTATUS=2 AND SZ3,0.8,0.05,0,'股价偏离注意调整'),COLORRED;
    # DRAWTEXT_FIX(BARSTATUS=2 AND SZ4,0.8,0.05,0,'上升通道调整洗盘'),COLORGREEN;

def tdx_yhzc(data):
    # 用户注册
    # pass
    # C = data.close
    CLOSE = data.close
    # HIGH = data.high
    # H = data.high
    # L = data.low
    # LOW = data.low
    # OPEN = data.open
    # O = data.open
    VOL = data.volume
    # AMOUNT = data.amount

    # 除业绩后退股 := FINANCE(30) >= REF(FINANCE(30), 130);
    # D0 := 除业绩后退股;
    # D2 := IF(NAMELIKE('S'), 0, 1);
    # D3 := IF(NAMELIKE('*'), 0, 1);
    # D4 := DYNAINFO(17) > 0;
    # 去除大盘股 := CAPITAL / 1000000 < 20;
    # 去高价 := C <= 60;
    # 去掉 := D0 and D2 and D3 and D4 and 去除大盘股 and 去高价 and NOT(C >= REF(C, 1) * 1.097 and C = O and H = L);

    去掉 = True
    DIF1 = (EMA(CLOSE, 12) - EMA(CLOSE, 26)) / EMA(CLOSE, 26) * 100
    DEA1 = EMA(DIF1, 9)
    AAA1 = (DIF1 - DEA1) * 100
    # MA120 = REF(MA(C,120),1)
    # MA5 = REF(MA(C, 120),1)
    # MA10 = REF(MA(C, 120),1)
    # PTGD = REF(HHV(C,120),1)
    # XIN_GAO = IFAND(C > PTGD, C > MA120, True, False)
    用 = 45
    户 = AAA1 - REF(AAA1, 1)
    注册 = CROSS(户, 用)
    DIF = (EMA(CLOSE, 10) - EMA(CLOSE, 72)) / EMA(CLOSE, 72) * 100
    DEA = EMA(DIF, 17)
    AAA = (DIF - DEA) * 100
    用户 = CROSS(AAA - REF(AAA, 1), 45)
    # 用户注册 = IFAND4(注册 , 用户, TJ_V, XIN_GAO, 1, 0) #and 去掉;

    TJ_V = VOL > 3 * MA(VOL,89)

    用户注册 = IFAND3(注册 , 用户, 去掉, 1, 0) #and 去掉;
    return 用户注册, -1, False


def tdx_yhzc_macd(data):
    # 用户注册
    # pass
    # C = data.close
    CLOSE = data.close
    # HIGH = data.high
    # H = data.high
    # L = data.low
    # LOW = data.low
    # OPEN = data.open
    # O = data.open
    VOL = data.volume
    # AMOUNT = data.amount

    # 除业绩后退股 := FINANCE(30) >= REF(FINANCE(30), 130);
    # D0 := 除业绩后退股;
    # D2 := IF(NAMELIKE('S'), 0, 1);
    # D3 := IF(NAMELIKE('*'), 0, 1);
    # D4 := DYNAINFO(17) > 0;
    # 去除大盘股 := CAPITAL / 1000000 < 20;
    # 去高价 := C <= 60;
    # 去掉 := D0 and D2 and D3 and D4 and 去除大盘股 and 去高价 and NOT(C >= REF(C, 1) * 1.097 and C = O and H = L);

    去掉 = True
    # MACD
    SHORT =12
    LONG = 26
    MID = 9
    EMASHORT = EMA(CLOSE, SHORT)
    EMALONG = EMA(CLOSE, LONG)
    DIF = EMASHORT - EMALONG
    DEA = EMA(DIF, MID)
    MACD = (DIF-DEA) * 2
    MACDTJ = IFAND4(MACD>0, DIF > 0, DEA > 0, CROSS(DIF, DEA), True, False)

    # MACD2
    DIF1 = (EMA(CLOSE, SHORT) - EMA(CLOSE, LONG)) / EMA(CLOSE, LONG) * 100
    DEA1 = EMA(DIF1, MID)
    AAA1 = (DIF1 - DEA1) * 100
    # MA120 = REF(MA(C,120),1)
    # MA5 = REF(MA(C, 120),1)
    # MA10 = REF(MA(C, 120),1)
    # PTGD = REF(HHV(C,120),1)
    # XIN_GAO = IFAND(C > PTGD, C > MA120, True, False)
    用 = 45
    户 = AAA1 - REF(AAA1, 1)
    注册 = CROSS(户, 用)
    DIF = (EMA(CLOSE, 10) - EMA(CLOSE, 72)) / EMA(CLOSE, 72) * 100
    DEA = EMA(DIF, 17)
    AAA = (DIF - DEA) * 100
    用户 = CROSS(AAA - REF(AAA, 1), 45)
    # 用户注册 = IFAND4(注册 , 用户, TJ_V, XIN_GAO, 1, 0) #and 去掉;

    TJ_V = True # VOL > 2 * MA(VOL,89)

    # 用户注册 = IFAND4(注册 , 用户, MACDTJ, TJ_V, 1, 0) #and 去掉;
    用户注册 = IFAND3(注册, 用户, MACDTJ, 1, 0)
    return 用户注册, -1, False

def tdx_yhzc_kdj(data):
    # 用户注册
    # pass
    # C = data.close
    CLOSE = data.close
    C = data.close

    # HIGH = data.high
    H = data.high
    L = data.low
    # LOW = data.low
    # OPEN = data.open
    # O = data.open
    VOL = data.volume
    # AMOUNT = data.amount

    # 除业绩后退股 := FINANCE(30) >= REF(FINANCE(30), 130);
    # D0 := 除业绩后退股;
    # D2 := IF(NAMELIKE('S'), 0, 1);
    # D3 := IF(NAMELIKE('*'), 0, 1);
    # D4 := DYNAINFO(17) > 0;
    # 去除大盘股 := CAPITAL / 1000000 < 20;
    # 去高价 := C <= 60;
    # 去掉 := D0 and D2 and D3 and D4 and 去除大盘股 and 去高价 and NOT(C >= REF(C, 1) * 1.097 and C = O and H = L);

    去掉 = True
    # MACD
    SHORT =12
    LONG = 26
    MID = 9
    EMASHORT = EMA(CLOSE, SHORT)
    EMALONG = EMA(CLOSE, LONG)
    DIF = EMASHORT - EMALONG
    DEA = EMA(DIF, MID)
    MACD = (DIF-DEA) * 2
    MACDTJ = IFAND4(MACD>0, DIF > 0, DEA > 0, CROSS(DIF, DEA), True, False)

    #KDJ
    N = 19
    M1 = 3
    M2 = 3
    RSV = (CLOSE - LLV(L, N)) / (HHV(H, N) - LLV(L, N)) * 100
    K = SMA(RSV, M1)
    D = SMA(K, M2)
    J = 3 * K - 2 * D
    KDJTJ = IF(J > 50, True, False)
    # MACD2
    DIF1 = (EMA(CLOSE, SHORT) - EMA(CLOSE, LONG)) / EMA(CLOSE, LONG) * 100
    DEA1 = EMA(DIF1, MID)
    AAA1 = (DIF1 - DEA1) * 100
    # MA120 = REF(MA(C,120),1)
    # MA5 = REF(MA(C, 120),1)
    # MA10 = REF(MA(C, 120),1)
    # PTGD = REF(HHV(C,120),1)
    # XIN_GAO = IFAND(C > PTGD, C > MA120, True, False)
    用 = 45
    户 = AAA1 - REF(AAA1, 1)
    注册 = CROSS(户, 用)
    DIF = (EMA(CLOSE, 10) - EMA(CLOSE, 72)) / EMA(CLOSE, 72) * 100
    DEA = EMA(DIF, 17)
    AAA = (DIF - DEA) * 100
    用户 = CROSS(AAA - REF(AAA, 1), 45)
    # 用户注册 = IFAND4(注册 , 用户, TJ_V, XIN_GAO, 1, 0) #and 去掉;

    TJ_V = True # VOL > 2 * MA(VOL,89)

    # 用户注册 = IFAND4(注册 , 用户, MACDTJ, TJ_V, 1, 0) #and 去掉;
    # 用户注册 = IFAND3(注册, 用户, MACDTJ, 1, 0)
    用户注册 = IFAND3(注册, 用户, KDJTJ, 1, 0)
    return 用户注册, -1, False

def tdx_dqe_cfc_A1(data, sort=False):
    # 选择／排序
    C = data.close
    O = data.open
    JC =IF(ISLASTBAR(C), O, C)
    MC = (0.3609454219 * JC - 0.03309329629 * REF(C, 1) - 0.04241822779 * REF(C, 2) - 0.026737249 * REF(C, 3) \
           - 0.007010041271 * REF(C, 4) - 0.002652859952 * REF(C, 5) - 0.0008415042966 * REF(C, 6) \
           - 0.0002891931964 * REF(C, 7) - 0.0000956265934 * REF(C, 8) - 0.0000321286052 * REF(C, 9) \
           - 0.0000106773454 * REF(C, 10) - 0.0000035457562 * REF(C, 11) -- 0.0000011670713 * REF(C, 12)) / (1 - 0.7522406533)
    # 竞价涨幅 := (DYNAINFO(4) / DYNAINFO(3) - 1) * 100;
    竞价涨幅 = (C / REF(C, 1) - 1) * 100
    # ST := STRFIND(stkname, 'ST', 1) > 0;
    # S := STRFIND(stkname, 'S', 1) > 0;
    # 停牌 := (DYNAINFO(4)=0);
    #
    # 附加条件 := (not (ST) and not (S) and NOT(停牌)) * (竞价涨幅 < 9.85) * (竞价涨幅 > (0));
    附加条件 = IFAND(竞价涨幅 < 9.85, 竞价涨幅 > 0, 1, 0)
    if sort:
        刀 = (MC - JC) / JC * 1000
    else:
        # 刀 = (MC - JC) / JC * 1000 * 附加条件
        刀 = (MC - JC) / JC * 1000

    return 刀, -1, False

def tdx_dqe_cfc_A11(data, sort=False):
    # 选择／排序
    C = data.close
    O = data.open
    V = data.volume
    JC =IF(ISLASTBAR(C), O, C)
    MC = (0.3609454219 * JC - 0.03309329629 * REF(C, 1) - 0.04241822779 * REF(C, 2) - 0.026737249 * REF(C, 3) \
           - 0.007010041271 * REF(C, 4) - 0.002652859952 * REF(C, 5) - 0.0008415042966 * REF(C, 6) \
           - 0.0002891931964 * REF(C, 7) - 0.0000956265934 * REF(C, 8) - 0.0000321286052 * REF(C, 9) \
           - 0.0000106773454 * REF(C, 10) - 0.0000035457562 * REF(C, 11) -- 0.0000011670713 * REF(C, 12)) / (1 - 0.7522406533)
    # 竞价涨幅 := (DYNAINFO(4) / DYNAINFO(3) - 1) * 100;
    竞价涨幅 = (C / REF(C, 1) - 1) * 100
    # ST := STRFIND(stkname, 'ST', 1) > 0;
    # S := STRFIND(stkname, 'S', 1) > 0;
    # 停牌 := (DYNAINFO(4)=0);
    #
    # 附加条件 := (not (ST) and not (S) and NOT(停牌)) * (竞价涨幅 < 9.85) * (竞价涨幅 > (0));
    附加条件 = IFAND(竞价涨幅 < 9.85, 竞价涨幅 > 0, 1, 0)
    限量 = IF(COUNT(REF(V, 1) / REF(V, 2) > 6, 10) == 0, 1, 0)
    多头 = IFAND(O > REF(MA(C, 5), 1), O > REF(MA(C, 10), 1), 1, 0)
    if sort:
        刀 = (MC - JC) / JC * 1000
    else:
        刀 = (MC - JC) / JC * 1000 * 附加条件 * 限量 * 多头

    return 刀, -1, False

def tdx_dqe_cfc_A2(data, zf1=6, zf2=-3, lbzf1=0.95, lbzf2=1.097):
    C = data.close
    O = data.open
    V = data.volume
    H = data.high
    L = data.low
    # 去ST := STRFIND(STKNAME, 'S', 1) = 0
    # 去停牌 := DYNAINFO(4) > 0;
    # 大小 := IF(BARSCOUNT(C) < 90, CAPITAL / 1000000 < 0.5, CAPITAL / 1000000 < 8.8) and C < 88;
    # 上市天数 := BARSCOUNT(C) > 8;
    # 涨幅 := (DYNAINFO(4) - DYNAINFO(3)) / DYNAINFO(3) * 100 < 6 and (DYNAINFO(4) - DYNAINFO(3)) / DYNAINFO(3) * 100 > -3;
    涨幅T = (O - REF(C,1)) / REF(C,1)
    涨幅T2 = REF(C, 1) / REF(C, 2)
    涨幅 = IFAND(涨幅T * 100 < zf1, 涨幅T * 100 > zf2, True, False)
    跳空 = COUNT(IFAND(O > REF(H, 1), L > REF(H, 1), 1, 0), 10) > 0
    # 去连板 := NOT((REF(O, 1) < REF(C, 1) OR REF(L, 1) / REF(O, 1) > 0.95) and REF(C, 1) / REF(C, 2) >= 1.097 and (
    #             REF(C, 2) / REF(C, 3) >= 1.097));
    去连板 = IFAND3(IFOR(REF(O, 1) < REF(C, 1) , REF(L, 1) / REF(O, 1) > lbzf1, True, False),  涨幅T2 >= lbzf2, \
            REF(涨幅T2,1) >= lbzf2, False, True)
    限量 = COUNT(REF(V, 1) / REF(V, 2) > 6, 10) == 0
    多头 = IFAND(O > REF(MA(C, 5), 1),  O > REF(MA(C, 10), 1), True, False)
    # 去ST and 去停牌 and 大小 and 上市天数 and 涨幅 and 跳空 and 去连板 and 限量 and 多头;
    # pass
    return IFAND4(涨幅, 跳空, 限量, 多头, 1, 0), -1, False

def tdx_dqe_cfc_A(data, zf1=6, zf2=-3, lbzf1=0.95, lbzf2=1.097):
    C = data.close
    O = data.open
    # C = data.close
    # O = data.open
    V = data.volume
    H = data.high
    L = data.low
    
    JC =IF(ISLASTBAR(C), O, C)
    MC = (0.3609454219 * JC - 0.03309329629 * REF(C, 1) - 0.04241822779 * REF(C, 2) - 0.026737249 * REF(C, 3) \
           - 0.007010041271 * REF(C, 4) - 0.002652859952 * REF(C, 5) - 0.0008415042966 * REF(C, 6) \
           - 0.0002891931964 * REF(C, 7) - 0.0000956265934 * REF(C, 8) - 0.0000321286052 * REF(C, 9) \
           - 0.0000106773454 * REF(C, 10) - 0.0000035457562 * REF(C, 11) -- 0.0000011670713 * REF(C, 12)) / (1 - 0.7522406533)
    # 竞价涨幅 := (DYNAINFO(4) / DYNAINFO(3) - 1) * 100;
    竞价涨幅 = (JC / REF(C, 1) - 1) * 100
    # ST := STRFIND(stkname, 'ST', 1) > 0;
    # S := STRFIND(stkname, 'S', 1) > 0;
    # 停牌 := (DYNAINFO(4)=0);
    #
    # 附加条件 := (not (ST) and not (S) and NOT(停牌)) * (竞价涨幅 < 9.85) * (竞价涨幅 > (0));
    附加条件 = IFAND(竞价涨幅 < 9.85, 竞价涨幅 > 0, 1, 0)
    # if sort:
    #     刀 = (MC - JC) / JC * 1000
    # else:
    刀 = (MC - JC) / JC * 1000 * 附加条件

    dao = 刀[-1]
    if dao <= 0:
        return 刀, -1, False

    涨幅T = 竞价涨幅/100 #(O - REF(C,1)) / REF(C,1)
    涨幅T2 = REF(C, 1) / REF(C, 2)
    涨幅 = IFAND(涨幅T * 100 < zf1, 涨幅T * 100 > zf2, True, False)
    跳空 = COUNT(IFAND(O > REF(H, 1), L > REF(H, 1), 1, 0), 10) > 0
    # 去连板 := NOT((REF(O, 1) < REF(C, 1) OR REF(L, 1) / REF(O, 1) > 0.95) and REF(C, 1) / REF(C, 2) >= 1.097 and (
    #             REF(C, 2) / REF(C, 3) >= 1.097));
    去连板 = IFAND3(IFOR(REF(O, 1) < REF(C, 1) , REF(L, 1) / REF(O, 1) > lbzf1, True, False),  涨幅T2 >= lbzf2, \
            REF(涨幅T2,1) >= lbzf2, False, True)
    限量 = COUNT(REF(V, 1) / REF(V, 2) > 6, 10) == 0
    多头 = IFAND(O > REF(MA(C, 5), 1),  O > REF(MA(C, 10), 1), True, False)
    TJ1 = IFAND4(涨幅, 跳空, 限量, 多头, dao, 0)        

    return TJ1, -1, False


def tdx_dqe_cfc_KA(data, zf1=6, zf2=-3, lbzf1=0.95, lbzf2=1.097):
    C = data.close
    O = data.open
    # C = data.close
    # O = data.open
    V = data.volume
    H = data.high
    L = data.low

    JC = IF(ISLASTBAR(C), O, C)
    MC = (0.3609454219 * JC - 0.03309329629 * REF(C, 1) - 0.04241822779 * REF(C, 2) - 0.026737249 * REF(C, 3) \
          - 0.007010041271 * REF(C, 4) - 0.002652859952 * REF(C, 5) - 0.0008415042966 * REF(C, 6) \
          - 0.0002891931964 * REF(C, 7) - 0.0000956265934 * REF(C, 8) - 0.0000321286052 * REF(C, 9) \
          - 0.0000106773454 * REF(C, 10) - 0.0000035457562 * REF(C, 11) - - 0.0000011670713 * REF(C, 12)) / (
                     1 - 0.7522406533)
    # 竞价涨幅 := (DYNAINFO(4) / DYNAINFO(3) - 1) * 100;
    竞价涨幅 = (JC / REF(C, 1) - 1) * 100
    # ST := STRFIND(stkname, 'ST', 1) > 0;
    # S := STRFIND(stkname, 'S', 1) > 0;
    # 停牌 := (DYNAINFO(4)=0);
    #
    # 附加条件 := (not (ST) and not (S) and NOT(停牌)) * (竞价涨幅 < 9.85) * (竞价涨幅 > (0));
    附加条件 = IFAND(竞价涨幅 < 9.85, 竞价涨幅 > 0, 1, 0)
    # if sort:
    #     刀 = (MC - JC) / JC * 1000
    # else:
    刀 = (MC - JC) / JC * 1000 * 附加条件

    dao = 刀[-1]
    if dao <= 0:
        return 刀, -1, False

    涨幅T = 竞价涨幅 / 100  # (O - REF(C,1)) / REF(C,1)
    涨幅T2 = REF(C, 1) / REF(C, 2)
    涨幅 = IFAND(涨幅T * 100 < zf1, 涨幅T * 100 > zf2, True, False)
    跳空 = COUNT(IFAND(O > REF(H, 1), L > REF(H, 1), 1, 0), 10) > 0
    # 去连板 := NOT((REF(O, 1) < REF(C, 1) OR REF(L, 1) / REF(O, 1) > 0.95) and REF(C, 1) / REF(C, 2) >= 1.097 and (
    #             REF(C, 2) / REF(C, 3) >= 1.097));
    去连板 = IFAND3(IFOR(REF(O, 1) < REF(C, 1), REF(L, 1) / REF(O, 1) > lbzf1, True, False), 涨幅T2 >= lbzf2, \
                 REF(涨幅T2, 1) >= lbzf2, False, True)
    限量 = COUNT(REF(V, 1) / REF(V, 2) > 6, 10) == 0
    多头 = IFAND(O > REF(MA(C, 5), 1), O > REF(MA(C, 10), 1), True, False)

    LOWV = LLV(L, 9)
    HIGHV = HHV(H, 9)
    RSV = EMA((C - LOWV) / (HIGHV - LOWV) * 100, 3)
    K1 = EMA(RSV, 3)
    D1 = MA(K1, 3)
    TJ10 = REF(IFAND(CROSS(K1,D1), K1 < 50, True, False), 1)

    TJ1 = IFAND5(涨幅, 跳空, 限量, 多头, TJ10, dao, 0)


    return TJ1, -1, False

def tdx_dqe_cfc_AM(data, zf1=6, zf2=-3, lbzf1=0.95, lbzf2=1.097):
    C = data.close
    CLOSE = data.close
    O = data.open
    # C = data.close
    # O = data.open
    V = data.volume
    H = data.high
    L = data.low
    
    JC =IF(ISLASTBAR(C), O, C)
    MC = (0.3609454219 * JC - 0.03309329629 * REF(C, 1) - 0.04241822779 * REF(C, 2) - 0.026737249 * REF(C, 3) \
           - 0.007010041271 * REF(C, 4) - 0.002652859952 * REF(C, 5) - 0.0008415042966 * REF(C, 6) \
           - 0.0002891931964 * REF(C, 7) - 0.0000956265934 * REF(C, 8) - 0.0000321286052 * REF(C, 9) \
           - 0.0000106773454 * REF(C, 10) - 0.0000035457562 * REF(C, 11) -- 0.0000011670713 * REF(C, 12)) / (1 - 0.7522406533)
    # 竞价涨幅 := (DYNAINFO(4) / DYNAINFO(3) - 1) * 100;
    竞价涨幅 = (JC / REF(C, 1) - 1) * 100
    # ST := STRFIND(stkname, 'ST', 1) > 0;
    # S := STRFIND(stkname, 'S', 1) > 0;
    # 停牌 := (DYNAINFO(4)=0);
    #
    # 附加条件 := (not (ST) and not (S) and NOT(停牌)) * (竞价涨幅 < 9.85) * (竞价涨幅 > (0));
    附加条件 = IFAND(竞价涨幅 < 9.85, 竞价涨幅 > 0, 1, 0)
    # if sort:
    #     刀 = (MC - JC) / JC * 1000
    # else:
    刀 = (MC - JC) / JC * 1000 * 附加条件

    dao = 刀[-1]
    if dao <= 0:
        return 刀, -1, False
    
    # 经典MACD
    MACD2 = (EXPMA(CLOSE,55)-REF(EXPMA(CLOSE,55),1))/REF(EXPMA(CLOSE,55),1)*100
    DIF2 = EMA(SUM(MACD2,2),5)
    # 入1 = IF(DIF2>REF(DIF2,1),DIF2,0)
    # 入2 = IF(DIF2<REF(DIF2,1),DIF2,0)
    DEA2 = MA(DIF2,10)
    MACDJC = IF(CROSS(DIF2,DEA2), True, False) 
    if MACDJC[-1] == False:
        return 刀, -1, False
    
    涨幅T = 竞价涨幅/100 #(O - REF(C,1)) / REF(C,1)
    涨幅T2 = REF(C, 1) / REF(C, 2)
    涨幅 = IFAND(涨幅T * 100 < zf1, 涨幅T * 100 > zf2, True, False)
    跳空 = COUNT(IFAND(O > REF(H, 1), L > REF(H, 1), 1, 0), 10) > 0
    # 去连板 := NOT((REF(O, 1) < REF(C, 1) OR REF(L, 1) / REF(O, 1) > 0.95) and REF(C, 1) / REF(C, 2) >= 1.097 and (
    #             REF(C, 2) / REF(C, 3) >= 1.097));
    去连板 = IFAND3(IFOR(REF(O, 1) < REF(C, 1) , REF(L, 1) / REF(O, 1) > lbzf1, True, False),  涨幅T2 >= lbzf2, \
            REF(涨幅T2,1) >= lbzf2, False, True)
    限量 = COUNT(REF(V, 1) / REF(V, 2) > 6, 10) == 0
    多头 = IFAND(O > REF(MA(C, 5), 1),  O > REF(MA(C, 10), 1), True, False)
    TJ1 = IFAND4(涨幅, 跳空, 限量, 多头, dao, 0)        

    return TJ1, -1, False

def tdx_pool_qsfb(data, zf1=6, zf2=-3, lbzf1=0.95, lbzf2=1.097):
    CLOSE = data.close
    C = data.close
    OPEN = data.open
    # C = data.close
    O = data.open
    V = data.volume
    HIGH = data.high
    H = data.high
    L = data.low

    # {强势反包}
    MA30=MA(CLOSE,30)
    MA60=MA(CLOSE,60)
    ABT=IFAND4(MA30>MA60, MA30>REF(MA30,1), MA60>REF(MA60,1), CLOSE>MA30, True, False)
    
    XG1=IFAND5(COUNT(CLOSE<OPEN,2)==1, CLOSE>OPEN, CLOSE>REF(HIGH,1), REF(CLOSE,2)>REF(OPEN,2), ABT, True, False)
    XG2=IFAND5(COUNT(CLOSE<OPEN,3)==2, CLOSE>OPEN, CLOSE>REF(HIGH,2), REF(CLOSE,3)>REF(OPEN,3), ABT, True, False)
    XG3=IFAND5(COUNT(CLOSE<OPEN,4)==3, CLOSE>OPEN, CLOSE>REF(HIGH,3), REF(CLOSE,4)>REF(OPEN,4), ABT, True, False)
    XG4=IFAND5(COUNT(CLOSE<OPEN,5)==4, CLOSE>OPEN, CLOSE>REF(HIGH,4), REF(CLOSE,5)>REF(OPEN,5), ABT, True, False)
    XG5=IFAND5(COUNT(CLOSE<OPEN,6)==5, CLOSE>OPEN, CLOSE>REF(HIGH,5), REF(CLOSE,6)>REF(OPEN,6), ABT, True, False)

    TJ0=IFOR4(XG1, XG2, XG3, XG4, True, False)
    TJ2=IFOR(TJ0, XG5, 1, 0)
    if TJ2[-1] == 0:
        return [0], -1, False
    
    JC =IF(ISLASTBAR(C), O, C)
    MC = (0.3609454219 * JC - 0.03309329629 * REF(C, 1) - 0.04241822779 * REF(C, 2) - 0.026737249 * REF(C, 3) \
           - 0.007010041271 * REF(C, 4) - 0.002652859952 * REF(C, 5) - 0.0008415042966 * REF(C, 6) \
           - 0.0002891931964 * REF(C, 7) - 0.0000956265934 * REF(C, 8) - 0.0000321286052 * REF(C, 9) \
           - 0.0000106773454 * REF(C, 10) - 0.0000035457562 * REF(C, 11) -- 0.0000011670713 * REF(C, 12)) / (1 - 0.7522406533)
    # # 竞价涨幅 := (DYNAINFO(4) / DYNAINFO(3) - 1) * 100;
    竞价涨幅 = (JC / REF(C, 1) - 1) * 100
    # # ST := STRFIND(stkname, 'ST', 1) > 0;
    # # S := STRFIND(stkname, 'S', 1) > 0;
    # # 停牌 := (DYNAINFO(4)=0);
    # #
    # # 附加条件 := (not (ST) and not (S) and NOT(停牌)) * (竞价涨幅 < 9.85) * (竞价涨幅 > (0));
    # 附加条件 = IFAND(竞价涨幅 < 9.85, 竞价涨幅 > 0, 1, 0)
    附加条件 = IFAND(竞价涨幅 < zf1, 竞价涨幅 > zf2, 1, 0)
    # # if sort:
    # #     刀 = (MC - JC) / JC * 1000
    # # else:
    刀 = (MC - JC) / JC * 1000 * 附加条件

    dao = 刀[-1]
    # if dao <= 0:
    #     return 0

    涨幅T = 竞价涨幅/100 #(O - REF(C,1)) / REF(C,1)
    涨幅T2 = REF(C, 1) / REF(C, 2)
    涨幅 = IFAND(涨幅T * 100 < zf1, 涨幅T * 100 > zf2, True, False)
    跳空 = COUNT(IFAND(O > REF(H, 1), L > REF(H, 1), 1, 0), 10) > 0
    # 去连板 := NOT((REF(O, 1) < REF(C, 1) OR REF(L, 1) / REF(O, 1) > 0.95) and REF(C, 1) / REF(C, 2) >= 1.097 and (
    #             REF(C, 2) / REF(C, 3) >= 1.097));
    去连板 = IFAND3(IFOR(REF(O, 1) < REF(C, 1) , REF(L, 1) / REF(O, 1) > lbzf1, True, False),  涨幅T2 >= lbzf2, \
            REF(涨幅T2,1) >= lbzf2, False, True)
    限量 = COUNT(REF(V, 1) / REF(V, 2) > 6, 10) == 0
    多头 = IFAND(O > REF(MA(C, 5), 1),  O > REF(MA(C, 10), 1), True, False)
    TJ1 = IFAND4(涨幅, 跳空, 限量, 多头, dao, 0)        

    return TJ1, -1, False
    
    
def tdx_dqe_cfc_A3(data):
    # {竞价委托    逸飞    分笔周期}
    # T := TIME >= 92500   AND    TIME < 93000;
    VOL = data.volume
    # 竞价量 = REF(SUM(VOL, 0), BARSLAST(T))
    竞价量 = VOL[-1]
    竞价换手 = 竞价量 / CAPITAL(data) * 100
    # pass



def tdx_dqe_cfc_B1(data, sort=False):
    # 停牌 := (DYNAINFO(4)=0);
    # not (停牌);
    pass

def tdx_dqe_cfc_B2(data, sort=False):
    # 停牌 := (DYNAINFO(4)=0);
    # not (停牌);
    return tdx_dqe_cfc_A2(data, zf2=-3.5, lbzf1=0.9, lbzf2=1.09)

def tdx_sxp_yhzc(data):
    CLOSE=data.close
    C=data.close
    前炮 = CLOSE > REF(CLOSE, 1) * 1.095
    小阴小阳 = HHV(ABS(C - REF(C, 1)) / REF(C, 1) * 100, BARSLAST(前炮)) < 6
    小阴小阳1 = ABS(C - REF(C, 1)) / REF(C, 1) * 100 < 9
    时间限制 = IFAND(COUNT(前炮, 30) == 1, BARSLAST(前炮) > 5, True, False)
    后炮 = IFAND(REF(IFAND(小阴小阳, 时间限制, 1, 0), 1) , 前炮, 1, 0)
    return 后炮, -1, True
    # # 用户注册
    # # pass
    # # C = data.close
    # # CLOSE = data.close
    # # HIGH = data.high
    # # H = data.high
    # # L = data.low
    # # LOW = data.low
    # # OPEN = data.open
    # # O = data.open
    # VOL = data.volume
    # # AMOUNT = data.amount
    #
    # # 除业绩后退股 := FINANCE(30) >= REF(FINANCE(30), 130);
    # # D0 := 除业绩后退股;
    # # D2 := IF(NAMELIKE('S'), 0, 1);
    # # D3 := IF(NAMELIKE('*'), 0, 1);
    # # D4 := DYNAINFO(17) > 0;
    # # 去除大盘股 := CAPITAL / 1000000 < 20;
    # # 去高价 := C <= 60;
    # # 去掉 := D0 and D2 and D3 and D4 and 去除大盘股 and 去高价 and NOT(C >= REF(C, 1) * 1.097 and C = O and H = L);
    # TJ_V = VOL > 3 * MA(VOL,89)
    # DIF1 = (EMA(CLOSE, 12) - EMA(CLOSE, 26)) / EMA(CLOSE, 26) * 100
    # DEA1 = EMA(DIF1, 9)
    # AAA1 = (DIF1 - DEA1) * 100
    # # MA120 = REF(MA(C,120),1)
    # # MA5 = REF(MA(C, 120),1)
    # # MA10 = REF(MA(C, 120),1)
    # # PTGD = REF(HHV(C,120),1)
    # # XIN_GAO = IFAND(C > PTGD, C > MA120, True, False)
    # 用 = 45
    # 户 = AAA1 - REF(AAA1, 1)
    # 注册 = CROSS(户, 用)
    # DIF = (EMA(CLOSE, 10) - EMA(CLOSE, 72)) / EMA(CLOSE, 72) * 100
    # DEA = EMA(DIF, 17)
    # AAA = (DIF - DEA) * 100
    # 用户 = CROSS(AAA - REF(AAA, 1), 45)
    # # 用户注册 = IFAND4(注册 , 用户, TJ_V, XIN_GAO, 1, 0) #and 去掉;
    # 用户注册 = IFAND4(注册 , 用户, TJ_V, 后炮, 1, 0) #and 去掉;
    # return 用户注册, False
#
# def tdx_mssyjz(data):
#     CLOSE=data.close
#     C=data.close
#     HIGH = data.high
#     LOW = data.low
#
#     XA_1 = (HHV(HIGH, 9) - CLOSE) / (HHV(HIGH, 9) - LLV(LOW, 9)) * 100 - 70
#     XA_2 = SMA(XA_1, 9, 1) + 100
#     XA_3 = (CLOSE - LLV(LOW, 9)) / (HHV(HIGH, 9) - LLV(LOW, 9)) * 100
#     XA_4 = SMA(XA_3, 3, 1)
#     XA_5 = SMA(XA_4, 3, 1) + 100
#     XA_6 = XA_5 - XA_2
#     趋势1 = IF(XA_6 > 45, XA_6 - 45, 0)
#     XA_7 = REF(LOW, 1)
#     XA_8 = SMA(ABS(LOW - XA_7), 3, 1) / SMA(MAX(LOW - XA_7, 0), 3, 1) * 100
#     XA_9 = EMA(IF(CLOSE * 1.3, XA_8 * 10, XA_8 / 10), 3)
#     XA_10 = LLV(LOW, 30)
#     VAR1 = C / REF(C, 1) < 0.95
#     # buy(C / refx(C, 1) < 0.95, LOW)
#     # sell(REF(VAR1, 1), HIGH)
#
#     # DRAWTEXT_FIX(CURRBARSCOUNT=1, 0, 0.18, 0, 2), COLORFF75FF
#     # DRAWTEXT_FIX(CURRBARSCOUNT=1, 0, 0.28, 0, 27), COLORRED
#     # DRAWTEXT_FIX(CURRBARSCOUNT=1, 0, 0.08, 0, 26), COLORGREEN
#     # DRAWTEXT_FIX(CURRBARSCOUNT=1, 0, 0.13, 0, 2), COLORYELLOW
# 白金买卖
def tdx_bjmm(data):
    # AMOUNT = data.amount
    VOL = data.volume
    CLOSE = data.close
    C = data.close
    H = data.high
    L = data.low
    O = data.open
    VAR2 = CLOSE * VOL
    VAR3 = EMA((EMA(VAR2, 3) / EMA(VOL, 3) + EMA(VAR2, 6) / EMA(VOL, 6)
                + EMA(VAR2, 12) / EMA(VOL, 12) + EMA(VAR2, 24) / EMA(VOL, 24)) / 4, 13)
    白线 = 1.06 * VAR3
    MA4 = MA(C, 4)
    MA24 = MA(C, 24)
    # C1 = C >= MA4
    # C2 = C < MA4
    #
    # # IF(MA4 >= REF(MA4, 1), MA4, DRAWNULL), COLORRED, LINETHICK2;
    JJ = (3 * C + H + L + O) / 6
    VAR1 = (8 * JJ + 7 * REF(JJ, 1) + 6 * REF(JJ, 2) + 5 * REF(JJ, 3) + 4 * REF(JJ, 4)
            + 3 * REF(JJ, 5) + 2 * REF(JJ, 6) + REF(JJ, 8)) / 36
    TJ2 = IFAND4(VOL == HHV(VOL, 10), VOL > 2 * REF(VOL, 1), CLOSE > VAR1, C > REF(C, 1), True, False)
    # LJL = FILTER(TJ2, 5)
    TJ1 = (JJ-白线) /白线 * 100

    # MACDTJ
    SHORT =12
    LONG = 26
    MID = 9
    EMASHORT = EMA(CLOSE, SHORT)
    EMALONG = EMA(CLOSE, LONG)
    DIF = EMASHORT - EMALONG
    DEA = EMA(DIF, MID)
    MACD = (DIF-DEA) * 2
    # MACDTJ = IFAND4(MACD>0, DIF > 0, DEA > 0, CROSS(DIF, DEA), True, False)
    MACDTJ = IFAND3(MACD > 0, DIF > 0, DEA > 0, True, False)

    # B_1 = IFAND3(TJ1 >= 0, REF(TJ1,1) < 0, MACDTJ, 1, 0)
    # B_1 = IFAND(TJ1 >= 0, REF(TJ1, 1) < 0, 1, 0)
    # B_1 = IFAND4(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, MACDTJ, 1, 0)
    B_1 = IFAND3(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, 1, 0)
    S_1 = IFAND(TJ1 < 0, REF(TJ1, 1) > 0, 1, -1)
    # S_1 = IFAND(C < MA24, REF(C,1) > REF(MA24,1), 1, -1)
    # return B_1, B_1, False
    # return B_1, -1, False
    return B_1, S_1, False

def tdx_bjmm_jzmd(data):
    # AMOUNT = data.amount
    VOL = data.volume
    CLOSE = data.close
    C = data.close
    H = data.high
    L = data.low
    O = data.open
    VAR2 = CLOSE * VOL
    VAR3 = EMA((EMA(VAR2, 3) / EMA(VOL, 3) + EMA(VAR2, 6) / EMA(VOL, 6)
                + EMA(VAR2, 12) / EMA(VOL, 12) + EMA(VAR2, 24) / EMA(VOL, 24)) / 4, 13)
    白线 = 1.06 * VAR3
    MA4 = MA(C, 4)
    MA24 = MA(C, 24)
    # C1 = C >= MA4
    # C2 = C < MA4
    #
    # # IF(MA4 >= REF(MA4, 1), MA4, DRAWNULL), COLORRED, LINETHICK2;
    JJ = (3 * C + H + L + O) / 6
    VAR1 = (8 * JJ + 7 * REF(JJ, 1) + 6 * REF(JJ, 2) + 5 * REF(JJ, 3) + 4 * REF(JJ, 4)
            + 3 * REF(JJ, 5) + 2 * REF(JJ, 6) + REF(JJ, 8)) / 36
    TJ2 = IFAND4(VOL == HHV(VOL, 10), VOL > 2 * REF(VOL, 1), CLOSE > VAR1, C > REF(C, 1), True, False)
    # LJL = FILTER(TJ2, 5)
    TJ1 = (JJ-白线) /白线 * 100

    HVOL = HHV(VOL, 34)
    HNUM = BARSLAST(HVOL == VOL)
    HH = REF(H, HNUM)
    HL = REF(L, HNUM)
    JZBD = IFAND4(HNUM > 10, C > HL, H > HH, C < HH * 1.06, True, False)
    JZBD_S = IFAND3(HNUM > 10, C > HL, H > HH, True, False)
    # # MACDTJ
    # SHORT =12
    # LONG = 26
    # MID = 9
    # EMASHORT = EMA(CLOSE, SHORT)
    # EMALONG = EMA(CLOSE, LONG)
    # DIF = EMASHORT - EMALONG
    # DEA = EMA(DIF, MID)
    # MACD = (DIF-DEA) * 2
    # # MACDTJ = IFAND4(MACD>0, DIF > 0, DEA > 0, CROSS(DIF, DEA), True, False)
    # MACDTJ = IFAND3(MACD > 0, DIF > 0, DEA > 0, True, False)

    # B_1 = IFAND3(TJ1 >= 0, REF(TJ1,1) < 0, MACDTJ, 1, 0)
    # B_1 = IFAND(TJ1 >= 0, REF(TJ1, 1) < 0, 1, 0)
    # B_1 = IFAND4(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, MACDTJ, 1, 0)
    # B_1 = IFAND3(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, 1, 0)
    B_1 = IFAND4(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, JZBD, 1, 0)
    S_1 = IFAND(TJ1 < 0, REF(TJ1, 1) > 0, 1, -1)
    # S_1 = IFAND(C < MA24, REF(C,1) > REF(MA24,1), 1, -1)
    # return B_1, B_1, False
    # return B_1, -1, False
    return B_1, S_1, False

def tdx_bjmm_yhzc(data):
    # AMOUNT = data.amount
    VOL = data.volume
    CLOSE = data.close
    C = data.close
    H = data.high
    L = data.low
    O = data.open
    VAR2 = CLOSE * VOL
    VAR3 = EMA((EMA(VAR2, 3) / EMA(VOL, 3) + EMA(VAR2, 6) / EMA(VOL, 6)
                + EMA(VAR2, 12) / EMA(VOL, 12) + EMA(VAR2, 24) / EMA(VOL, 24)) / 4, 13)
    白线 = 1.06 * VAR3
    MA4 = MA(C, 4)
    # MA24 = MA(C, 24)
    # C1 = C >= MA4
    # C2 = C < MA4
    #
    # # IF(MA4 >= REF(MA4, 1), MA4, DRAWNULL), COLORRED, LINETHICK2;
    JJ = (3 * C + H + L + O) / 6
    VAR1 = (8 * JJ + 7 * REF(JJ, 1) + 6 * REF(JJ, 2) + 5 * REF(JJ, 3) + 4 * REF(JJ, 4)
            + 3 * REF(JJ, 5) + 2 * REF(JJ, 6) + REF(JJ, 8)) / 36
    TJ2 = IFAND4(VOL == HHV(VOL, 10), VOL > 2 * REF(VOL, 1), CLOSE > VAR1, C > REF(C, 1), True, False)
    # LJL = FILTER(TJ2, 5)
    TJ1 = (JJ-白线) /白线 * 100

    # MACDTJ
    SHORT =12
    LONG = 26
    MID = 9
    EMASHORT = EMA(CLOSE, SHORT)
    EMALONG = EMA(CLOSE, LONG)
    DIF = EMASHORT - EMALONG
    DEA = EMA(DIF, MID)
    MACD = (DIF-DEA) * 2
    # MACDTJ = IFAND4(MACD>0, DIF > 0, DEA > 0, CROSS(DIF, DEA), True, False)
    # MACDTJ = IFAND3(MACD > 0, DIF > 0, DEA > 0, True, False)
    MACDTJ = IFAND5(MACD > 0, DIF > 0, DEA > 0, REF(MACD,1) >= 0, REF(MACD,2) >= 0, True, False)

    # B_1 = IFAND3(TJ1 >= 0, REF(TJ1,1) < 0, MACDTJ, 1, 0)
    # B_1 = IFAND(TJ1 >= 0, REF(TJ1, 1) < 0, 1, 0)
    # B_1 = IFAND4(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, MACDTJ, 1, 0)
    # B_1 = IFAND3(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, 1, 0)
    S_1 = IFAND(TJ1 < 0, REF(TJ1, 1) > 0, 1, -1)
    # return B_1, B_1, False
    # return B_1, -1, False

    # # 用户注册
    # CLOSE = data.close
    # VOL = data.volume
    去掉 = True
    DIF1 = (EMA(CLOSE, 12) - EMA(CLOSE, 26)) / EMA(CLOSE, 26) * 100
    DEA1 = EMA(DIF1, 9)
    AAA1 = (DIF1 - DEA1) * 100
    用 = 45
    户 = AAA1 - REF(AAA1, 1)
    注册 = CROSS(户, 用)
    DIF = (EMA(CLOSE, 10) - EMA(CLOSE, 72)) / EMA(CLOSE, 72) * 100
    DEA = EMA(DIF, 17)
    AAA = (DIF - DEA) * 100
    用户 = CROSS(AAA - REF(AAA, 1), 45)
    # # 用户注册 = IFAND4(注册 , 用户, TJ_V, XIN_GAO, 1, 0) #and 去掉;
    #
    # TJ_V = VOL > 3 * MA(VOL,89)
    #
    用户注册 = IFAND3(注册 , 用户, 去掉, True, False) #and 去掉;

    B_1 = IFAND5(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, 用户注册, MACDTJ, 1, 0)
    return B_1, S_1, False


def tdx_bjmm_new(data):
    # AMOUNT = data.amount
    VOL = data.volume
    CLOSE = data.close
    C = data.close
    H = data.high
    L = data.low
    O = data.open
    VAR2 = CLOSE * VOL
    VAR3 = EMA((EMA(VAR2, 3) / EMA(VOL, 3) + EMA(VAR2, 6) / EMA(VOL, 6)
                + EMA(VAR2, 12) / EMA(VOL, 12) + EMA(VAR2, 24) / EMA(VOL, 24)) / 4, 13)
    白线 = 1.06 * VAR3
    MA4 = MA(C, 4)
    MA24 = MA(C, 24)
    # C1 = C >= MA4
    # C2 = C < MA4
    #
    # # IF(MA4 >= REF(MA4, 1), MA4, DRAWNULL), COLORRED, LINETHICK2;
    JJ = (3 * C + H + L + O) / 6
    VAR1 = (8 * JJ + 7 * REF(JJ, 1) + 6 * REF(JJ, 2) + 5 * REF(JJ, 3) + 4 * REF(JJ, 4)
            + 3 * REF(JJ, 5) + 2 * REF(JJ, 6) + REF(JJ, 8)) / 36
    TJ2 = IFAND4(VOL == HHV(VOL, 10), VOL > 2 * REF(VOL, 1), CLOSE > VAR1, C > REF(C, 1), True, False)
    # LJL = FILTER(TJ2, 5)
    TJ1 = (JJ-白线) /白线 * 100

    # MACDTJ
    SHORT =12
    LONG = 26
    MID = 9
    EMASHORT = EMA(CLOSE, SHORT)
    EMALONG = EMA(CLOSE, LONG)
    DIF = EMASHORT - EMALONG
    DEA = EMA(DIF, MID)
    MACD = (DIF-DEA) * 2
    # MACDTJ = IFAND4(MACD>0, DIF > 0, DEA > 0, CROSS(DIF, DEA), True, False)
    MACDTJ = IFAND3(MACD > 0, DIF > 0, DEA > 0, True, False)
    TJ3 = IFAND4(C>白线, C>MA24, REF(C,1) < REF(白线,1), REF(C,1) < REF(MA24,1), True, False)
    # B_1 = IFAND3(TJ1 >= 0, REF(TJ1,1) < 0, MACDTJ, 1, 0)
    # B_1 = IFAND(TJ1 >= 0, REF(TJ1, 1) < 0, 1, 0)
    # B_1 = IFAND4(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, MACDTJ, 1, 0)
    B_1 = IFAND4(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, TJ3, 1, 0)
    S_1 = IFAND(TJ1 < 0, REF(TJ1, 1) > 0, 1, -1)
    # return B_1, B_1, False
    # return B_1, -1, False
    return B_1, S_1, False

def tdx_sxjm(data):
    # AMOUNT = data.amount
    # VOL = data.volume
    # CLOSE = data.close
    C = data.close
    # H = data.high
    # L = data.low
    # O = data.open
    A1 = EMA(C, 20) - EMA(C, 60)
    A2 = C - EMA(C, 60)
    A3 = EMA(A2, 5)
    A4 = EMA(A3, 3)
    MA24 = MA(C, 24)
    # XG = A1 > 0 and REF(A3, 1) < REF(A3, 2) and A3 > REF(A3, 1)
    XG1 = IFAND3(A1 > 0, REF(A3, 1) < REF(A3, 2), A3 > REF(A3, 1), 1, 0)
    # XG1 = IFAND3(A1 > 0, REF(A3, 1) > REF(A3, 2), A3 > REF(A3, 1), 1, 0)
    XG2 = IFAND4(XG1 > 0, A4 > REF(A4, 1), C > MA24, REF(C,1) < REF(MA24,1), 1, 0)

    return XG2, -1, False

def tdx_ltt(data, N=120):## 龙抬头
    C=data.close
    W1=C=HHV(C,N)
    W2=BARSLAST(W1)
    W3=IF(W2>0,REF(C,W2),REF(C,W2))
    W4=CROSS(C,REF(W3,1))
    W5=C/REF(C,1)>1.05
    XG=IFAND3(W4, W5, COUNT(W4,5)==1, 1, 0)
    return XG, -1, False 

def tdx_blft(data):
    CLOSE = data.close
    HIGH = data.high
    LOW = data.low
    OPEN = data.open
    VOL = data.volume
    
    X_1=MA(CLOSE,5)
    X_2=MA(CLOSE,10)
    X_3=MA(CLOSE,20)
    X_4=MA(CLOSE,30)
    X_5=MA(CLOSE,60)
    X_6=MA(CLOSE,120)
    X_7=MA(CLOSE,240)
    X_8=(REF(CLOSE,3)-CLOSE)/REF(CLOSE,3)*100>5
    X_9=FILTER(X_8,10)
    X_10=BARSLAST(X_9)
    X_11=REF(HIGH,X_10+2)
    X_12=REF(HIGH,X_10+1)
    X_13=REF(HIGH,X_10)
    X_14=MAX(X_11,X_12)
    X_15=MAX(X_14,X_13)
    X_16=(CLOSE-REF(CLOSE,1))/REF(CLOSE,1)*100>5
    X_17=X_10<150
    X_18=(OPEN-X_15)/X_15*100<30
    X_19=(CLOSE-LLV(LOW,X_10))/LLV(LOW,X_10)*100<50
    X_20=(CLOSE-REF(OPEN,5))/REF(OPEN,5)*100<30
    X_21=VOL/MA(VOL,5)<3.5
    X_22=(CLOSE-REF(CLOSE,89))/REF(CLOSE,89)*100<80
    X_23=(CLOSE-REF(CLOSE,1))/REF(CLOSE,1)*100>=5, (CLOSE-OPEN)/(HIGH-CLOSE)>3, VOL/MA(VOL,5)>1.3

    X_251 =IFAND5(X_16, X_17, X_18, X_19, X_20, True, False)
    X_25 = IFAND3(X_251, X_21, X_22, True, False) 
    暴利=IF(FILTER(X_25, 15), 1, 0)
    return 暴利, -1, False

def tdx_cci_xg(data):
    # {改CCI选股}
    CLOSE = data.close
    C = data.close
    HIGH = data.high
    LOW = data.low
    OPEN = data.open
    VOL = data.volume

    中线 = 0.00
    CC88 = CCI(data, 88).CCI
    # X_14 = IFAND(COUNT(REF(EMA(CLOSE, 3), 1) < REF(EMA(CLOSE, 3), 2), 5) == 5 , EMA(CLOSE, 3) > REF(EMA(CLOSE, 3), 1), 1, 0)
    # TJ1 = IFAND(X_14 > 0, REF(X_14,1) > 0, True, False)
    平均CC883 = EMA(CC88, 3)
    平均CC889 = EMA(CC88, 9)

    浮平线1 = CC88 - 平均CC883

    # 浮平线2 = CC88 - 平均CC889
    # 鉴真线 = EMA(浮平线1, 20)
    # MB1 = HHV(浮平线1, 20)
    MB2 = LLV(浮平线1, 20)
    # 上平台 = REF(MB1, 1)

    下平台 = REF(MB2, 1)

    # CBL1 = LLV(CC88, 2) > LLV(CC88, 14)

    AA = CROSS(浮平线1, 中线)
    # {强势金叉条件}
    BB = CROSS(浮平线1, 下平台)
    # {底部金叉条件}
    CC = CROSS(CC88, 平均CC889)
    # {强势金叉条件}
    PPCT = IF(REF(C, 1) / MA(C, 20) < 1.3, True, False)
    AAN = IF(AA, 1, 0)
    BBN = IF(BB, 1, 0)
    CCN = IF(CC, 1, 0)
    # XG0: (AAN + BBN + CCN) > 1
    XG = IFAND((AAN + BBN + CCN) > 1, PPCT, 1, 0)
    return XG, -1, False

def tdx_macd_sykt(data):
    CLOSE = data.close
    C = data.close
    HIGH = data.high
    LOW = data.low
    OPEN = data.open
    VOL = data.volume

    WY1001=(2*CLOSE+HIGH+LOW)/4
    WY1002=EMA(WY1001,4)
    WY1003=EMA(WY1002,4)
    WY1004=EMA(WY1003,4)
    DQXY=(WY1004-REF(WY1004,1))/REF(WY1004,1)*100
    WY1005=EMA(WY1003,20)
    ZQXY=(WY1005-REF(WY1005,1))/REF(WY1005,1)*100
    WY1006=EMA(WY1003,80)
    CQXY=(WY1006-REF(WY1006,1))/REF(WY1006,1)*100
    
    return 0

def tdx_macd_shjd(data):
    CLOSE = data.close
    C = data.close
    HIGH = data.high
    LOW = data.low
    OPEN = data.open
    VOL = data.volume

    YDIF=EMA(CLOSE,240)-EMA(CLOSE,520)
    YDEA=EMA(YDIF,180)
    MACD2=YDIF*2-YDEA
    Y平滑=SMA(MACD2,3,1)
    SHORT=60
    LONG=130
    MID=45
    DIF=EMA(CLOSE,SHORT)-EMA(CLOSE,LONG)
    DEA=EMA(DIF,MID)
    MACD=DIF*2-DEA
    平滑=SMA(MACD,3,1)
    ZDIF=EMA(CLOSE,12)-EMA(CLOSE,26)
    ZDEA=EMA(ZDIF,9)
    MACD1=ZDIF*2-ZDEA
    平滑1=SMA(MACD1,3,1)
    三花选股=IFAND3(MACD1>平滑1 ,  MACD>平滑 ,  MACD2>Y平滑,1,0)
    MCD走强选股=IFAND(CROSS(平滑1,平滑),  MACD>平滑,0.2,0)
    
    return 0

def tjS(data):
    C = data.close
    C1 = C < REF(C,1)
    C2 = C < REF(C,2)
    C3 = C < REF(C,3)
    ma5=MA(C,3)
    C4 = C < ma5
    J=KDJ(data, N = 19)['KDJ_J'] < 80
    TJ = IFAND5(C1,C2,C3,C4,J, 1, 0)
    return TJ

def tjB(data):
    CLOSE = data.close
    C = data.close
    # HIGH = data.high
    # LOW = data.low
    # OPEN = data.open
    # VOL = data.volume
    DIF=EMA(CLOSE,8)-EMA(CLOSE,21)
    DEA=EMA(DIF,5)
    MACD=(DIF-DEA)*2

    TJ11 = IFAND5( C >= MA(C,5),  C >= MA(C,10) , C >= MA(C,20),  C >= MA(C,30), C >= MA(C,60), True, False)
    # TJ12 = IFAND3(DIF>=0 , DEA>=0,  MACD>=0, True, False)
    TJ1 = TJ11 #IFAND(TJ11, TJ12, True, False)
    TJ2 = IFAND6( C>MA(C,90), C>MA(C,120), C>MA(C,180), C>MA(C,240), C>MA(C,500), C>MA(C,360), True, False)
    TJ3 = IFAND3(C>MA(C,750), C>MA(C,1000), C>MA(C,1500), True, False)
    TJ4 = IFAND3(C>MA(C,2000), C>MA(C,3000), C>MA(C,5000), True, False)
    #     XG:TJ1 AND TJ2 AND TJ3 AND TJ4;
    #     XG1:TJ1 AND TJ2 AND TJ3;
    #     XG2:TJ1 AND TJ2;
    C1 = C > REF(C,1)
    C2 = C > REF(C,2)
    C3 = C > REF(C,3)
    J = KDJ(data, N = 19)['KDJ_J'] > 50
    TJ5 = IFAND4(C1,C2,C3, J, True, False)

    TJ6 = IFAND4(TJ1, TJ2, MACD >= 0, TJ5, 1, 0)
    return TJ6

def tdx_WYZBUY(data, refFlg = False):
#     CLOSE = data.close
    C = data.close
#     # HIGH = data.high
#     # LOW = data.low
#     # OPEN = data.open
#     # VOL = data.volume
#     DIF=EMA(CLOSE,8)-EMA(CLOSE,21)
#     DEA=EMA(DIF,5)
#     MACD=(DIF-DEA)*2

#     TJ11 = IFAND5( C >= MA(C,5),  C >= MA(C,10) , C >= MA(C,20),  C >= MA(C,30), C >= MA(C,60), True, False)
#     # TJ12 = IFAND3(DIF>=0 , DEA>=0,  MACD>=0, True, False)
#     TJ1 = TJ11 #IFAND(TJ11, TJ12, True, False)
#     TJ2 = IFAND6( C>MA(C,90), C>MA(C,120), C>MA(C,180), C>MA(C,240), C>MA(C,500), C>MA(C,360), True, False)
#     TJ3 = IFAND3(C>MA(C,750), C>MA(C,1000), C>MA(C,1500), True, False)
#     TJ4 = IFAND3(C>MA(C,2000), C>MA(C,3000), C>MA(C,5000), True, False)
#     #     XG:TJ1 AND TJ2 AND TJ3 AND TJ4;
#     #     XG1:TJ1 AND TJ2 AND TJ3;
#     #     XG2:TJ1 AND TJ2;
#     C1 = C > REF(C,1)
#     C2 = C > REF(C,2)
#     C3 = C > REF(C,3)
#     J = KDJ(data, N = 19)['KDJ_J'] > 50
#     TJ5 = IFAND4(C1,C2,C3, J, True, False)

#     TJ6 = IFAND4(TJ1, TJ2, MACD >= 0, TJ5, 1, 0)
    TJ6 = tjB(data)
    XG = IFAND(TJ6 == 1, C < MA(C,5) * 1.05, True, False)
    if refFlg:
        return REF(XG, 1), -1, False
    else:
        return XG, -1, False

def tdx_wyzbs(data):
    # CLOSE = data.close
    # C = data.close
    # HIGH = data.high
    # LOW = data.low
    # OPEN = data.open
    # VOL = data.volume
    XG = tjB(data)
    MG = tjS(data)
    return XG, MG, False

def tdx_bdzh(data):
    L = data.low
    C = data.close
    H = data.high
    Y1 = LLV(L, 17)
    Y2 = SMA(ABS(L-REF(L,1)),17,1)
    Y3 = SMA(MAX(L-REF(L,1),0),17,2)
    Q = -(EMA(IF(L<=Y1,Y2/Y3,-3),2)) ## EMA(x,1) : error
    强拉升 = IF(CROSS(Q,0),1,0)
    D1 = (C+L+H)/3
    D2 = EMA(D1,6)
    D3 = EMA(D2,5)
    BBUY = CROSS(D2,D3)
    XG = IFAND(EXIST(强拉升, 5), BBUY, 1, 0)
    return XG, -1, False

def tdx_skdj_lstd(data):
    LOW = data.low
    CLOSE = data.close
    HIGH = data.high

    N=9
    M=3
    LOWV=LLV(LOW,N)
    HIGHV=HHV(HIGH,N)
    RSV=EMA((CLOSE-LOWV)/(HIGHV-LOWV)*100,M)
    K=EMA(RSV,M)
    D=MA(K,M)
    JC1=CROSS(K,D)
    
    MC=CROSS(D,K)
    
    # VAR1=(HIGH+LOW+CLOSE*2)/4
    # VAR2=EMA(VAR1,21)
    # VAR3=STD(VAR1,21)
    # VAR4=((VAR1-VAR2)/VAR3*100+200)/4
    # VAR5=(EMA(VAR4,89)-25)*1.56
    # VAR6=EMA(VAR5,5)*1.22
    # VAR7=EMA(VAR6,3)
    # VAR8=3*VAR6-2*VAR7
    
    # VAR1A=IFAND3(CROSS(VAR6,VAR8), CROSS(VAR7,VAR8), CROSS(VAR7,VAR6),1,0)
    VAR1B=EMA(CLOSE,3)-EMA(CLOSE,89)
    VAR1C=EMA(VAR1B,21)
    VAR1D=(VAR1B-VAR1C)*10
    VAR1F=POW(VAR1D,3)*0.1+POW(VAR1D,2)
    游资=IF(VAR1D>0.015,VAR1F,0)/45
    # STICKLINE(VAR1D>0.015,VAR1F/45,0,1,0),COLORRED,
    VAR9=EMA(CLOSE,2)-EMA(CLOSE,55)
    VAR10=EMA(VAR9,13)
    VAR11=2*(VAR9-VAR10)
    资金=POW(VAR11,3)*0.1+POW(VAR11,1)
    
    JC2 = IFAND(游资 > 0, REF(游资, 1) == 0, 1, 0)
    JC3 = CROSS(资金, 0)
    # 强弱分界:0,COLORGREEN
    SSS=9 
    LLL=34 
    DIF=EMA(CLOSE,12)-EMA(CLOSE,26)
    DEA=EMA(DIF,200)
    AA=(DIF-DEA)*2
    黄金钻信号=IF(AA<0,0,AA*AA)
    # {WWW.GUHAI.COM.CN}
    DIF1=EMA(CLOSE,9)-EMA(CLOSE,34)
    DEA1=EMA(DIF1,200)
    AAA=(DIF1-DEA1)*2
    启动引导线=IF(AA<0,0,AAA*AAA)
    红码=MA(CLOSE,15)+2*STD(CLOSE,15)
    XX=EMA(CLOSE,5)
    
    # DRAWICON(C>红码 AND C>=O ,资金,26)
    
    # XG = IFAND(JC1, JC2, 1, 0)
    # XG = IFAND3(IFOR(JC1, REF(JC1,1), True, False), JC2, JC3, 1, 0)
    XG = IFAND3(JC1, JC2, JC3, 1, 0)
    return XG, -1, False

def tdx_dqe_xqc_A1(data, sort=False):
    # 选择／排序
    C = data.close
    O = data.open
    JC =IF(ISLASTBAR(C), O, C)
    MC = (0.3609454219 * JC - 0.03309329629 * REF(C, 1) - 0.04241822779 * REF(C, 2) - 0.026737249 * REF(C, 3) \
           - 0.007010041271 * REF(C, 4) - 0.002652859952 * REF(C, 5) - 0.0008415042966 * REF(C, 6) \
           - 0.0002891931964 * REF(C, 7) - 0.0000956265934 * REF(C, 8) - 0.0000321286052 * REF(C, 9) \
           - 0.0000106773454 * REF(C, 10) - 0.0000035457562 * REF(C, 11) - 0.0000011670713 * REF(C, 12)) / (1 - 0.7522406533)
    # 竞价涨幅 := (DYNAINFO(4) / DYNAINFO(3) - 1) * 100;
    竞价涨幅 = (C / REF(C, 1) - 1) * 100
    # ST := STRFIND(stkname, 'ST', 1) > 0;
    # S := STRFIND(stkname, 'S', 1) > 0;
    # 停牌 := (DYNAINFO(4)=0);
    #
    # 附加条件 := (not (ST) and not (S) and NOT(停牌)) * (竞价涨幅 < 9.85) * (竞价涨幅 > (0));
    pctZL = CAPITAL(data)/1000000
    WB = BIDASK5VOL(data)[0] - BIDASK5VOL(data)[1]
    附加条件 = IFAND4(竞价涨幅 < 6, 竞价涨幅 > -8, pctZL < 1000, WB > 0, 1, 0)
    if sort:
        刀 = (MC - JC) / JC * 1000
    else:
        刀 = (MC - JC) / JC * 1000 * 附加条件
        # 刀 = (MC - JC) / JC * 1000
    #刀 = 刀* data.volume / CAPITAL(data) * 100

    return 刀, -1, False

def tdx_sxzsl(data):
    CLOSE = data.close
    VOL = data.volume
    OPEN = data.open
    
    # # X_1=((COST(85)+COST(15))/2+COST(50))/1.985
    # # X_2=SMA(COST(87),2,1)
    # X_3=MA(CLOSE,26)
    # # X_4=CLOSE>X_1 AND CLOSE>X_3 AND CROSS(CLOSE,X_2) AND CLOSE>X_2 AND (CLOSE-REF(CLOSE,1))/REF(CLOSE,1)*100>5
    # # X_41 = CLOSE > X_1
    # X_42 = CLOSE>X_3
    # # X_43 = CLOSE > X_2
    # X_44 = (CLOSE - REF(CLOSE, 1)) / REF(CLOSE, 1) * 100 > 5
    # X_5=MA(VOL,135)
    # X_6=VOL=HHV(VOL,10) AND VOL>1.9*REF(VOL,1) AND CLOSE>=REF(CLOSE,1) AND CLOSE>=OPEN AND VOL<=X_5*3.5
    # XG=CROSS(SMA(MAX(CLOSE-REF(CLOSE,1),0),4,1)/SMA(ABS(CLOSE-REF(CLOSE,1)),4,1)*100,80) OR FILTER(X_6,3) AND X_4

def tdx_dqe_test_A01(data):
    CLOSE = data.close
    VOL = data.volume
    C = data.close
    H = data.high
    L = data.low
    O = data.open
    # ST =STRFIND(stkname,'ST',1)>0
    # S =STRFIND(stkname,'S',1)>0
    # 停牌 =(DYNAINFO(4)=0)
    一字板 = IFAND3(C/REF(C,1)>1.095,  H==O ,  L==H, True, False)
    # not(ST) and not(S)  and not(停牌) AND 
    # XG=IFAND4( CAPITAL(data) / 1000000 < 10, CLOSE <80, 一字板, REF(VOL,1)/CAPITAL(data)>0.05, 1, 0) 
    # data['cap'] = CAPITAL(data) / 1000000 < 10
    # XG=IFAND4( data['cap'], CLOSE <80, 一字板 == False, REF(VOL,1)/CAPITAL(data)>0.05, 1, 0) 
    XG=IFAND3(CLOSE < 100, 一字板 == False, REF(VOL,1)/CAPITAL(data)>0.05, 1, 0) 
    return XG, -1, False

def tdx_dqe_test_A01_N(data):
    CLOSE = data.close
    VOL = data.volume
    C = data.close
    H = data.high
    L = data.low
    O = data.open
    # ST =STRFIND(stkname,'ST',1)>0
    # S =STRFIND(stkname,'S',1)>0
    # 停牌 =(DYNAINFO(4)=0)
    一字板 = IFAND3(C/REF(C,1)>1.095,  H==O ,  L==H, True, False)
    # not(ST) and not(S)  and not(停牌) AND
    # XG=IFAND4( CAPITAL(data) / 1000000 < 10, CLOSE <80, 一字板, REF(VOL,1)/CAPITAL(data)>0.05, 1, 0)
    A1 = 6.3 / 10000
    B1 = 522
    BZ1 = CAPITAL(data) * A1 + B1
    # data['cap'] = CAPITAL(data) / 1000000 < 10
    # XG=IFAND4( data['cap'], CLOSE <80, 一字板 == False, REF(VOL,1)/CAPITAL(data)>0.05, 1, 0)
    XG = IFAND(一字板 == False, REF(VOL,1)/CAPITAL(data)>0.05, 1, 0)
    return XG, -1, False

def tdx_dqe_test_A02(data):
    CLOSE = data.close
    C = data.close
    VOL = data.volume
    LOW = data.low
    HIGH = data.high
    OPEN = data.open
    N1=3
    N2=5
    N3=9
    N4=13
    N5=21
    N6=34
    N7=76
    DIFF=EMA(CLOSE,N3)-EMA(CLOSE,N4)
    DEA=EMA(DIFF,N2)
    A1=DIFF>DEA
    RSV1=(CLOSE-LLV(LOW,N3))/(HHV(HIGH,N3)-LLV(LOW,N3))*100
    K0=SMA(RSV1,N1,1)
    D0=SMA(K0,N1,1)
    A2=K0>D0
    LC0=REF(CLOSE,1)
    RSI1=(SMA(MAX(CLOSE-LC0,0),N2,1))/(SMA(ABS(CLOSE-LC0),N2,1))*100
    RSI2=(SMA(MAX(CLOSE-LC0,0),N4,1))/(SMA(ABS(CLOSE-LC0),N4,1))*100
    A3=RSI1>RSI2
    RSV0=-(HHV(HIGH,N4)-CLOSE)/(HHV(HIGH,N4)-LLV(LOW,N4))*100
    LWR1=SMA(RSV0,N1,1)
    LWR2=SMA(LWR1,N1,1)
    A4=LWR1>LWR2
    BBI=(MA(CLOSE,N1)+MA(CLOSE,N2)+MA(CLOSE,N3)+MA(CLOSE,N4))/4
    A5=CLOSE>BBI
    MTM=CLOSE-REF(CLOSE,1)
    MMS=100*EMA(EMA(MTM,N2),N1)/EMA(EMA(ABS(MTM),N2),N1)
    MMM=100*EMA(EMA(MTM,N4),N3)/EMA(EMA(ABS(MTM),N4),N3)
    A6=MMS>MMM
    BIAS=(C-MA(C,N2))/MA(C,N2)
    DIF=(BIAS-REF(BIAS,16))
    DBCD=SMA(DIF,76,1)
    MM1=MA(DBCD,5)
    A7=DBCD>MM1
    RRA=3*SMA((CLOSE-LLV(LOW,27))/(HHV(HIGH,27)-LLV(LOW,27))*100,5,1)-2*SMA(SMA((CLOSE-LLV(LOW,27))/(HHV(HIGH,27)-LLV(LOW,27))*100,5,1),3,1)
    RRC=MA(RRA,12)
    A8=RRA>RRC
    MT=C-REF(C,1)
    ZLGJ=100*EMA(EMA(MT,N3),N3)/EMA(EMA(ABS(MT),N3),N3)
    MAZL=MA(ZLGJ,5)
    A9=ZLGJ>MAZL
    QJJ=VOL/((HIGH-LOW)*2-ABS(CLOSE-OPEN))
    XVL=IF(CLOSE>OPEN,QJJ*(HIGH-LOW),IF(CLOSE<OPEN,QJJ*(HIGH-OPEN+CLOSE-LOW),VOL/2))+IF(CLOSE>OPEN,0-QJJ*(HIGH-CLOSE+OPEN-LOW),IF(CLOSE<OPEN,0-QJJ*(HIGH-LOW),0-VOL/2))
    HSL=(XVL/20)/1.15
    VRA=((HSL*0.55+(REF(HSL,1)*0.33))+(REF(HSL,2)*0.22))
    LLJX=EMA(VRA,3)
    VRB=LLJX
    A10=VRB>0
    VRC=A1&A2&A3&A4&A5&A6&A7&A8&A9&A10
    return IF(VRC,1,0), -1, False

def tdx_dqe_test_A03(data):
    (VAR0, VAR00) = BIDASK5VOL(data)
    VAR = (VAR0-VAR00)/5
    CD = CAPITAL(data)
    if CD == 0:
        XG = 0
    else:
        XG = VAR/CAPITAL(data)*100
    return [XG,XG,XG], -1, False

def tdx_dqe_test_A04(data):
    CLOSE = data.close
    # C = data.close
    # VOL = data.volume
    LOW = data.low
    HIGH = data.high
    # OPEN = data.open

    V1 = (CLOSE*2+HIGH+LOW)/4*10
    V2 = EMA(V1,13)-EMA(V1,34);
    V3 = EMA(V2,5);
    # V4 = (EMA((WINNERB(CLOSE) * 70),3) / (EMA((WINNERB(CLOSE) * 70),3) + EMA(((WINNERB((CLOSE * 1.1)) - WINNERB((CLOSE * 0.9))) * 80),3))) * 100;
    VW1 = EMA((WINNER(data, CLOSE) * 70),3)
    VW2 = EMA(((WINNER(data, (CLOSE * 1.1)) - WINNER(data, (CLOSE * 0.9))) * 80),3)
    V4 = VW1 / (VW1 + VW2) * 100
    VM3 = 2*(V2 - V3)*5.5
    # XG = ((DYNAINFO(18)-DYNAINFO(19)-(2*(V2-V3)*5.5)-INTPART(V4))/(DYNAINFO(18)+DYNAINFO(19)+(2*(V2-V3)*5.5)+INTPART(V4))+1)*16/10
    (VARBUY, VARSELL) = BIDASK5VOL(data)
    XG = ((VARBUY-VARSELL-VM3-V4)/(VARBUY+VARSELL+VM3+V4)+1)*16/10
    # (VAR0, VAR00) = BIDASK5VOL(data)
    # VAR = (VAR0-VAR00)/5
    # XG = VAR/CAPITAL(data)*100
    return IF(XG>0,XG,0), -1, False

def tdx_dqe_test_A05(data):
    CLOSE = data.close
    # C = data.close
    VOL = data.volume
    LOW = data.low
    HIGH = data.high
    OPEN = data.open

def tdx_dqe_test_A06(data):
    CLOSE = data.close
    # C = data.close
    VOL = data.volume
    LOW = data.low
    HIGH = data.high
    OPEN = data.open

    LOW=IF(HIGH==LOW,LOW-0.01,LOW)

    jj = (HIGH+LOW+CLOSE) / 3
#     qj0 = VOL/IF(HIGH==LOW,4,HIGH-LOW)
    qj0 = VOL/(HIGH-LOW)
    qj1 = qj0*(MIN(OPEN,CLOSE)-LOW)
    qj2 = qj0*(jj-MIN(CLOSE,OPEN))
    qj3 = qj0*(HIGH-MAX(OPEN,CLOSE))
    qj4 = qj0*(MAX(CLOSE,OPEN)-jj)
#     DDX = IF(HIGH==LOW,4*qj0,((qj1+qj2)-(qj3+qj4)))/SUM(VOL,10)*100
    DDX = ((qj1+qj2)-(qj3+qj4))/SUM(VOL,10)*100
    DDY = ((qj2+qj4)-(qj1+qj3))/SUM(VOL,10)*100
    DDZ = ((qj1+qj2)-(qj3+qj4))/((qj1+qj2)+(qj3+qj4))*100*17
    return ((DDX+DDY+DDZ)/3), -1, False

def tdx_dqe_test_A07(data):
#     CLOSE = data.close
    # C = data.close
    VOL = data.volume
#     LOW = data.low
#     HIGH = data.high
#     OPEN = data.open
#     VAR = data.volume
    VAR1 = CAPITAL(data)
    XG = VOL * 10 / VAR1
    return XG, -1, False

def tdx_lyqd(data, refFlg = True):
    # 龙妖启动
    CLOSE = data.close
    # C = data.close
    VOL = data.volume
    LOW = data.low
    HIGH = data.high
    OPEN = data.open
    VAR14 = IF(CLOSE>REF(CLOSE,1),1,0)
    VAR141=LOW<REF(HIGH,1)
    VAR142=REF(LOW,1)<REF(HIGH,2)
    VAR15 = IFAND5(CLOSE/REF(CLOSE,1)>1.095, HIGH/CLOSE<1.035, VAR14>0,VAR141, VAR142, 1,0)
    # XG = FILTER(VAR15>0,30)
    # return REF(XG,1), -1, False
    if refFlg:
        return REF(VAR15,1), -1, False
    else:
        return VAR15, -1, False
    #return XG, -1, False


def tdx_sl5560(data, refFlg = True):
    VOL = data.volume
    CLOSE = data.close
    HIGH = data.high
    LOW = data.low
    OPEN = data.open
    AMOUNT = data.amount
    # {森林55560}
    X_1 = SUM(IF(CLOSE>REF(CLOSE,1),VOL,IF(CLOSE<REF(CLOSE,1),0-VOL,0)),0)
    X_2 = SUMBARS(VOL,CAPITAL(data))
    X_3 = IF(CLOSE>LLV(CLOSE,X_2),1,0-1)*IF(X_1>LLV(X_1,X_2),1,0-1)
    X_4 = COUNT(IF(X_3==0-1,1,0)==1,8)>2
    X_5= (CLOSE-DMA((3*HIGH+LOW+OPEN+2*CLOSE)/7, VOL/SUM(AMOUNT,13) / AMOUNT/VOL/100/100))/DMA((3*HIGH+LOW+OPEN+2*CLOSE)/7,VOL/SUM(AMOUNT,13)/AMOUNT/VOL/100/100)*100<0-18
    X_6=(CLOSE-MIN(REF(CLOSE,5)*0.865,REF(CLOSE,21)*0.772))/CLOSE<0.009
    X_7= IFAND3(X_4,  X_5,   X_6, True, False)
    X_8= IFAND5(OPEN<EMA(CLOSE,5), CLOSE==HIGH , CLOSE/OPEN >=1.105 , VOL/CAPITAL(data)>=0.019 , VOL/CAPITAL(data)<=0.2, True, False)
    X_9= IFAND(X_8 ,COUNT(X_8,5)==1, True, False)
    X_10_1 = IFAND6(MA(CLOSE,3)>REF(MA(CLOSE,3),1) , MA(CLOSE,5)>REF(MA(CLOSE,5),1) , MA(CLOSE,10)>REF(MA(CLOSE,10),1) , VOL/240>REF(VOL,30)*1.2/240*1.5 , CLOSE>LOW*1.059 , CLOSE>REF(MA(CLOSE,3),1) ,True, False)
    X_10_2 = IFAND6(REF(CLOSE,1) , MA(CLOSE,5)>REF(MA(CLOSE,5),1) , MA(CLOSE,10)>REF(MA(CLOSE,10),1) , MA(CLOSE,20)>REF(MA(CLOSE,20),1) , MA(VOL,5)>REF(MA(VOL,5),1) , MA(CLOSE,5)-MA(CLOSE,10)<=0.579, True, False)
    X_10 = IFAND(X_10_1, X_10_2, True, False)
    X_11 = FILTER(X_10,5)
    XG = IFAND(IFOR(X_7, X_8, True, False) , X_11, 1, 0)
    if refFlg:
        return REF(XG,1), -1, False
    else:
        return XG, -1, False
    
def tdx_lbqs(data):
#     {趋势多空线XG}
    CLOSE = data.close
    C = data.close
    VOL = data.volume
    LOW = data.low
    HIGH = data.high
    OPEN = data.open

    N=13
    M=34
    P=55
    趋势=5*SMA((CLOSE-LLV(LOW,M))/(HHV(HIGH,M)-LLV(LOW,M))*100,5,1)-3*SMA(SMA((CLOSE-LLV(LOW,M))/(HHV(HIGH,M)-LLV(LOW,M))*100,5,1),3,1)-SMA(SMA(SMA((CLOSE-LLV(LOW,M))/(HHV(HIGH,M)-LLV(LOW,M))*100,5,1),3,1),2,1)
    底部=5
    XG0=IF(CROSS(趋势,底部),60,0)
#     {底底抬高}
    M3=MA(C,3)
    M10=MA(C,10)
    M60=MA(C,60)
    第一底=C<=LLV(C,10)
    天数1=BARSLAST(第一底)
    最小=C<=LLV(C,5)
    天数2=BARSLAST(最小)
#     底底抬高A=天数1>5 AND C> 第一底 AND M3<M10 AND REF(M3,天数1)<REF(M10,天数1) AND ((C<=LLV(C,5)) OR ( C> 第一底 AND 天数2>=1)) AND 天数1<=20
#     底底抬高 =天数1>5 AND C> 第一底 AND M3<M10 AND REF(M3,天数1)<REF(M10,天数1) AND
#         ((C<=LLV(C,5)) OR ( C> 第一底 AND 天数2>=1))
#         AND 天数1<=30 AND (VOL/REF(VOL,1)>0.5)
#     底底抬高 = 1
    底底抬高1 =IFAND4(天数1>5 , C> 第一底 , M3<M10 , REF(M3,天数1)<REF(M10,天数1), True, False)
    XG1=底底抬高1 * 30
    A30=EMA(C,34)>REF(EMA(C,34),1)
    A50=COST(data, 50) #,COLORRED,LINETHICK2
    A70=WINNER(data, C)*100>50
    A90=CROSS(C,A50)
    突破密集=IFAND4(A30, A50, A70, A90, True, False)
    XG2 = IFAND4(突破密集, REF(XG0,1), REF(XG1,1), C/REF(C,1) < 1.05, True, False)
#     XG2=突破密集 * 90 AND REF(XG0,1) AND REF(XG1,1) AND C/REF(C,1) < 1.05
    return XG2

def tdx_zttj(data):
    CLOSE = data.close
    C = data.close
    VOL = data.volume
    LOW = data.low
    HIGH = data.high
    OPEN = data.open

    VAR1 = MA(100*(CLOSE-LLV(CLOSE,34))/(HHV(HIGH,34)-LLV(LOW,34)),5)-20
    VAR2 =2*ABS(VAR1)
    VAR3 = 100-3*SMA((CLOSE-LLV(LOW,75))/(HHV(HIGH,75)-LLV(LOW,75))*100,20,1)+2*SMA(SMA((CLOSE-LLV(LOW,75))/(HHV(HIGH,75)-LLV(LOW,75))*100,20,1),15,1)
    VAR4 = 100-3*SMA((OPEN-LLV(LOW,75))/(HHV(HIGH,75)-LLV(LOW,75))*100,20,1)+2*SMA(SMA((OPEN-LLV(LOW,75))/(HHV(HIGH,75)-LLV(LOW,75))*100,20,1),15,1)
    情报 = ABS(100-VAR3)
    红军 = IF(VAR1>0,VAR1,0)
    绿军 = IF(VAR1<0,VAR2,0)
    VAR27 = IFAND3(VAR3<REF(VAR4,1), VOL>REF(VOL,1), CLOSE>REF(CLOSE,1), True, False)
    买入 = IFAND(VAR27, COUNT(VAR27,30)==1,1,0)
    XG = COUNT(买入>0,21) == 1
    return REF(XG,1), -1, False

def tdx_zttj1(data):
    CLOSE = data.close
    C = data.close
    VOL = data.volume
    LOW = data.low
    HIGH = data.high
    OPEN = data.open

    VAR1 = MA(100*(CLOSE-LLV(CLOSE,34))/(HHV(HIGH,34)-LLV(LOW,34)),5)-20
    VAR2 =2*ABS(VAR1)
    VAR3 = 100-3*SMA((CLOSE-LLV(LOW,75))/(HHV(HIGH,75)-LLV(LOW,75))*100,20,1)+2*SMA(SMA((CLOSE-LLV(LOW,75))/(HHV(HIGH,75)-LLV(LOW,75))*100,20,1),15,1)
    VAR4 = 100-3*SMA((OPEN-LLV(LOW,75))/(HHV(HIGH,75)-LLV(LOW,75))*100,20,1)+2*SMA(SMA((OPEN-LLV(LOW,75))/(HHV(HIGH,75)-LLV(LOW,75))*100,20,1),15,1)
    情报 = ABS(100-VAR3)
    红军 = IF(VAR1>0,VAR1,0)
    绿军 = IF(VAR1<0,VAR2,0)
    VAR27 = IFAND3(VAR3<REF(VAR4,1), VOL>REF(VOL,1), CLOSE>REF(CLOSE,1), True, False)
    买入 = IFAND(VAR27, COUNT(VAR27,30)==1,1,0)
    XG = COUNT(买入>0,21) == 1
    XG = 买入
    return REF(XG,1), -1, False

def tdx_cmfx(data):
    CLOSE = data.close
    C = data.close
    VOL = data.volume
    LOW = data.low
    HIGH = data.high
    OPEN = data.open

    HSL=EMA(VOL/CAPITAL(data),3)
    ZDL=HHV(HSL,240)
    ZXL=LLV(HSL,240)
    XS=MA(C,33)
    锁定筹码=EMA((HSL-ZXL)/ZXL*XS,13)
    浮动筹码=EMA((ZDL-HSL)/HSL*XS,13)
    力量对比=锁定筹码/浮动筹码
    XLV=(锁定筹码 - REF(锁定筹码,1)) / REF(锁定筹码,1) * 100
    XLV2=(力量对比 - REF(力量对比,1)) / REF(力量对比,1) * 100
    HL=13
    A1=CROSS(XLV,HL)
    A2=CROSS(XLV2,HL)
    A11=IFOR(A1>00,A2>0,True,False)
    # XG=(A1 OR A2) AND (C>REF(C,1) AND C>O AND REF(C,1) / REF(C,2) < 1.09)* 50;
    XG=IFAND5(A11, C>REF(C,1), C>OPEN, REF(C,1) / REF(C,2) < 1.09, HHV(C,5) / LLV(C,5) < 1.3, True, False)
    return REF(XG,1), -1, False
    # return A11

def tdx_TLBXX(data):
    #天冷不下雪
    CLOSE = data.close
    V1=COUNT(REF(EMA(CLOSE,3),1)<REF(EMA(CLOSE,3),2),5)==5
    V2=EMA(CLOSE,3)>REF(EMA(CLOSE,3),1)
    XG=IFAND(V1,V2,True,False)
    return XG, -1, False

def tdx_LDX(data):
    #流动性
    CLOSE = data.close
    OPEN = data.open
    AM = data.amount
    V1=ABS(np.log(CLOSE) - np.log(OPEN))
    V2=ABS(np.log(CLOSE) - np.log(REF(CLOSE,1)))
    #V3=MA(MAX(V1,V2)/AM * CAPITAL(data),10)
    V3=MA(MAX(V1,V2)/AM * 10000000000,10)
    V4=REF(V3,1)
    return V4, -1, False

def tdx_TLBXXF(data):
    #天冷不下雪
    CLOSE = data.close
    V1=COUNT(REF(EMA(CLOSE,3),1)<REF(EMA(CLOSE,3),2),5)==5
    V2=EMA(CLOSE,3)>REF(EMA(CLOSE,3),1)
    V3=IFAND(V1,V2,True,False)
    V4=V3[V3==True].index
    if len(V4) <= 1:
        data['A'] = False
        #XG=IFAND3(data['A'], CLOSE[V4[-1]] < CLOSE[V4[-1]], CLOSE.index[-1] == V4[-1], True, False)
        XG=data['A']
    else:
        V5=(V4[-1][0] - V4[-2][0]).days
        data['A']=V5<15
        XG=IFAND3(data['A'], CLOSE[V4[-1]] < CLOSE[V4[-2]], CLOSE.index[-1] == V4[-1], True, False)
    return XG, -1, False

def tdx_CTLJJ(data, refFlg = False):
    #朝天龙竞价
    CLOSE = data.close
    VOL = data.volume
    data['JEBZ'] = CAPITAL(data) * 100 / 100000000
    竞价量 = VOL > 45000
    竞价金额 = data.amount > 20000000
    竞量比 = 竞价金额 / CLOSE / 100 / REF(MA(CLOSE, 5),1);
    data['tj1']=IFAND(data['JEBZ'] > 0.6, data['JEBZ'] < 50, True, False)
    JLTJ = IFAND(竞量比 > 15, 竞量比 < 500000000, True, False)
    TJ1 = data['tj1']
    XG = IFAND4(竞价量,竞价金额,TJ1,JLTJ, True, False)
    if refFlg:
        return REF(XG,1), -1, False
    else:
        return XG, -1, False

def tdx_ZSMA(data):
    C = data.close
    M5 = MA(C, 5)
    M55 = MA(C, 55)
    XG = CROSS(M5,M55)
    return REF(XG, 1), -1, False
    


# def tdx_cmfxbl(data):
# {机构筹码分析}
# XA_32:=(CLOSE-LLV(LOW,27))/(HHV(HIGH,27)-LLV(LOW,27))*100;
# XA_34:=SMA(XA_32,3,1);
# 趋势:=SMA(XA_34,3,1),COLORRED,LINETHICK2;
# 人气:=SMA(趋势,3,1),COLORYELLOW,LINETHICK2;
# XGL:=IF(CROSS(趋势,人气),1,0);

# {筹码分析2}
# HSL:=EMA(VOL/CAPITAL,3);
# ZDL:=HHV(HSL,240);
# ZXL:=LLV(HSL,240);
# XS:=MA(C,33);
# 锁定筹码:=EMA((HSL-ZXL)/ZXL*XS,13);
# 浮动筹码:=EMA((ZDL-HSL)/HSL*XS,13);
# 力量对比:=锁定筹码/浮动筹码 ,COLORSTICK;
# XLV:=(锁定筹码 - REF(锁定筹码,1)) / REF(锁定筹码,1) * 100;
# XLV2:=(力量对比 - REF(力量对比,1)) / REF(力量对比,1) * 100;
# HL:=13;
# A1:=CROSS(XLV,HL);
# A2:=CROSS(XLV2,HL);
# A11:=(A1 OR A2) AND (C>REF(C,1) AND C>O AND REF(C,1) / REF(C,2) < 1.09)* 50;
# XG_CM:=XGL AND A11;






# X_8:=(REF(CLOSE,3)-CLOSE)/REF(CLOSE,3)*100>5;
# X_9:=FILTER(X_8,10);
# X_10:=BARSLAST(X_9);
# X_11:=REF(HIGH,X_10+2);
# X_12:=REF(HIGH,X_10+1);
# X_13:=REF(HIGH,X_10);
# X_14:=MAX(X_11,X_12);
# X_15:=MAX(X_14,X_13);
# X_16:=(CLOSE-REF(CLOSE,1))/REF(CLOSE,1)*100>5;
# X_17:=X_10<150;
# X_18:=(OPEN-X_15)/X_15*100<30;
# X_19:=(CLOSE-LLV(LOW,X_10))/LLV(LOW,X_10)*100<50;
# X_20:=(CLOSE-REF(OPEN,5))/REF(OPEN,5)*100<30;
# X_21:=VOL/MA(VOL,5)<3.5;
# X_22:=(CLOSE-REF(CLOSE,89))/REF(CLOSE,89)*100<80;

# X_25:=X_16 AND X_17 AND X_18 AND X_19 AND X_20 AND X_21 AND X_22 ;
# BL:=FILTER(X_25,15),COLORYELLOW;

# XG:XG_CM AND BL;

def tdx_WYZ17MA(data, refFlg = True):
    CLOSE = data.close
    C = data.close
    # HIGH = data.high
    # LOW = data.low
    # OPEN = data.open
    # VOL = data.volume
    DIF=EMA(CLOSE,8)-EMA(CLOSE,21)
    DEA=EMA(DIF,5)
    MACD=(DIF-DEA)*2

    TJ11 = IFAND6(C>=MA(C,5), C>MA(C,10) , MA(C, 5)>MA(C,10), C>MA(C,20),  C>MA(C,30), C>MA(C,60), True, False)
    TJ12 = IFAND3(DIF>=0 , DEA>=0,  MACD>=0, True, False)
    TJ1 = IFAND(TJ11, TJ12, True, False)
    TJ2 = IFAND6(C>MA(C,90), C>MA(C,120), C>MA(C,180), C>MA(C,240), C>MA(C,500), C>MA(C,360), True, False)
    TJ3 = IFAND3(C>MA(C,750), C>MA(C,1000), C>MA(C,1500), True, False)
    TJ4 = IFAND3(C>MA(C,2000), C>MA(C,3000), C>MA(C,5000), True, False)
#     XG:TJ1 AND TJ2 AND TJ3 AND TJ4;
#     XG1:TJ1 AND TJ2 AND TJ3;
#     XG2:TJ1 AND TJ2;
    XG = IF(TJ1, 1, 0)
    
#     XG = tjB(data)
    MG = tjS(data)
    return XG, MG, False
    if refFlg:
        return REF(XG,1), -1, False
    else:
        return XG, -1, False
# 趋势智能选股
def tdx_qszn(data, refFlg = True):
    H = data.high
    L = data.low
    CLOSE = data.close
    HIGH = data.high
    LOW = data.low
    C = data.close    
    PL5=HHV(H,18)
    AA=ABS((2*CLOSE+HIGH+LOW)/4-MA(CLOSE,30))/MA(CLOSE,30)
    长期趋势线=DMA((2*CLOSE+LOW+HIGH)/4,AA)
    CC=(CLOSE/长期趋势线);
    MA1=MA(CC*(2*CLOSE+HIGH+LOW)/4,3)
    MAAA=((MA1-长期趋势线)/长期趋势线)/3
    TMP=MA1-MAAA*MA1
    长期趋势上升=IF(TMP>长期趋势线 ,长期趋势线,0)
    长期趋势下降=IF(TMP<=长期趋势线,长期趋势线,0)
    HZS=CROSS(TMP,长期趋势线)
    LZS=CROSS(长期趋势线,TMP)
    JZ1=IFOR(HZS, REF(HZS,1), True, False)

    MAH=(H*18+REF(H,1)*17+REF(H,2)*16+REF(H,3)*15+REF(H,4)*14+REF(H,5)*13+REF(H,6)*12+REF(H,7)*11+REF(H,8)*10+REF(H,9)*9+REF(H,10)*8+REF(H,11)*7+REF(H,12)*6+REF(H,13)*5+REF(H,14)*4+REF(H,15)*3+REF(H,16)*2+REF(H,17)*1)/171
    MAL=(L*18+REF(L,1)*17+REF(L,2)*16+REF(L,3)*15+REF(L,4)*14+REF(L,5)*13+REF(L,6)*12+REF(L,7)*11+REF(L,8)*10+REF(L,9)*9+REF(L,10)*8+REF(L,11)*7+REF(L,12)*6+REF(L,13)*5+REF(L,14)*4+REF(L,15)*3+REF(L,16)*2+REF(L,17)*1)/171
    MA5=MA(CLOSE,5)
    MA10=MA(CLOSE,10)
    MA20=MA(CLOSE,20)
    MA60=MA(CLOSE,60)
    DK= IFOR(CLOSE>=MAH , IFAND4(C>MA5 , C>MA10 , C>MA20 , C>MA60, True, False), True, False)
    KK= IFOR(MAL>CLOSE , IFAND4(C<MA5 , C<MA10 , C<MA20 , C<MA60, True, False), True, False)
    DK1=BARSLAST(DK)
    KK1=BARSLAST(KK)
    DK2=BARSLAST(CROSS(KK1,DK1))
    KK2=BARSLAST(CROSS(DK1,KK1))
    HS=DK2<KK2
    LS=KK2<DK2

    趋势线=(MAH+MAL)/2

    TJB=IFAND3(JZ1 , HS , REF(HS,1) == 0, True, False)
    TJS=IFAND(LS , REF(LS,1) == 0, True, False)

#     N=14
#     TYP=(HIGH+LOW+CLOSE)/3
#     CCI=(TYP-MA(TYP,N))*1000/(15*AVEDEV(TYP,N))
    
#     XG=IFAND(REF(TJS,1) , CCI > REF(CCI,1), REF(CCI,1) < 0, CCI > 0, True, False)
    XG=IFOR(TJS, TJB, 1, 0)
#     return XG, -1, False
    if refFlg:
        return REF(XG,1), -1, True
    else:
        return XG, -1, True

# 趋势智能选股
def tdx_cci(data, refFlg = True):
    H = data.high
    L = data.low
    CLOSE = data.close
    HIGH = data.high
    LOW = data.low
    C = data.close    
    N=14
    TYP=(HIGH+LOW+CLOSE)/3
    CCI=(TYP-MA(TYP,N))*1000/(15*AVEDEV(TYP,N))
    XG=IFAND3(CCI > REF(CCI,1), CCI < 150, REF(CCI,1) < 0, 1, 0)
    if refFlg:
        return REF(XG,1), -1, True
    else:
        return XG, -1, True

# 趋势智能选股
def tdx_ngqd(data, refFlg = True):
    CLOSE = data.close
    C = data.close    
    黄线=MA(CLOSE,25)+MA(CLOSE,25)*6/100
    白轨=MA(CLOSE,25)+MA(CLOSE,25)*20/100
    影子线=MA(CLOSE,25)+MA(CLOSE,25)*13/100

    角度黄线=ATAN((黄线/REF(黄线,1)-1)*100)*180/3.1416


    XG10=IFAND(CROSS(C,影子线), C/REF(C,1)>1.03, True, False)
    XG11=IFAND3(CROSS(C,黄线), C/REF(C,1)>1.05, 角度黄线>0, True,False) ;
    XG12=CROSS(C,白轨)
    突破牛=IFOR(XG10, XG12, 1, 0)
    if refFlg:
        return REF(突破牛,1), -1, True
    else:
        return 突破牛, -1, True

# 趋势智能选股
def tdx_bollxg(data, refFlg = True):
    CLOSE = data.close
    C = data.close    
    N = 20
    N2 = 21
    MID = MA(C,N)
    VART1 = POW((C-MID),2)
    VART2 = MA(VART1,N)
    VART3 = SQRT(VART2)
    UPPER = MID+2*VART3
    LOWER = MID-2*VART3
    BOLL =  REF(MID,1)
    UB = REF(UPPER,1)
    LB = REF(LOWER,1)

    TJ1 = H >= REF(UPPER,1)
    TJ2 = CROSS(C,REF(UPPER,1))
    TJ3 = COUNT(TJ1,N2) == 0
#     XG = REF(TJ3,1) AND TJ2 AND C > O AND H > L


    
#     黄线=MA(CLOSE,25)+MA(CLOSE,25)*6/100
#     白轨=MA(CLOSE,25)+MA(CLOSE,25)*20/100
#     影子线=MA(CLOSE,25)+MA(CLOSE,25)*13/100

#     角度黄线=ATAN((黄线/REF(黄线,1)-1)*100)*180/3.1416


#     XG10=IFAND(CROSS(C,影子线), C/REF(C,1)>1.03, True, False)
#     XG11=IFAND3(CROSS(C,黄线), C/REF(C,1)>1.05, 角度黄线>0, True,False) ;
#     XG12=CROSS(C,白轨)
#     突破牛=IFOR(XG10, XG12, 1, 0)
#     if refFlg:
#         return REF(突破牛,1), -1, True
#     else:
#         return 突破牛, -1, True

def _tdx_DQS_F1(Series, N):
    return Series > MA(Series, N) * 0.89

# 大趋势选股
def tdx_DQS(data, refFlg = True):
    CLOSE = data.close
    C = data.close
    DETA = 0.895
    TJ1 = IFAND3(_tdx_DQS_F1(C, 60), _tdx_DQS_F1(C, 120), _tdx_DQS_F1(C, 240), 1, 0)
#     TJ11 = IFAND5( C >= MA(C,5),  C >= MA(C,10) , C >= MA(C,20),  C >= MA(C,30), C >= MA(C,60), True, False)
    # TJ12 = IFAND3(DIF>=0 , DEA>=0,  MACD>=0, True, False)
#     TJ1 = TJ11 #IFAND(TJ11, TJ12, True, False)
#     TJ2 = IFAND6( C>MA(C,90), C>MA(C,120), C>MA(C,180), C>MA(C,240), C>MA(C,500), C>MA(C,360), True, False)
#     TJ3 = IFAND3(C>MA(C,750), C>MA(C,1000), C>MA(C,1500), True, False)
#     TJ4 = IFAND3(C>MA(C,2000), C>MA(C,3000), C>MA(C,5000), True, False)
    #     XG:TJ1 AND TJ2 AND TJ3 AND TJ4;
    #     XG1:TJ1 AND TJ2 AND TJ3;
    #     XG2:TJ1 AND TJ2;
#     C1 = C > REF(C,1)
#     C2 = C > REF(C,2)
#     C3 = C > REF(C,3)
#     J = KDJ(data, N = 19)['KDJ_J'] > 50
#     TJ5 = IFAND4(C1,C2,C3, J, True, False)

#     TJ6 = IFAND4(TJ1, TJ2, MACD >= 0, TJ5, 1, 0)
    if refFlg:
        return REF(TJ1,1), -1, True
    else:
        return TJ1, -1, True
    