
import pandas as pd
from easyquant.indicator.base import *

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
    return 买股, False

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
    return 金K线, False
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
    return 大黑马出笼, False

def tdx_sxp(data):
    CLOSE=data.close
    C=data.close
    前炮 = CLOSE > REF(CLOSE, 1) * 1.099
    小阴小阳 = HHV(ABS(C - REF(C, 1)) / REF(C, 1) * 100, BARSLAST(前炮)) < 9
    小阴小阳1 = ABS(C - REF(C, 1)) / REF(C, 1) * 100 < 9
    时间限制 = IFAND(COUNT(前炮, 30) == 1, BARSLAST(前炮) > 5, True, False)
    后炮 = IFAND(REF(IFAND(小阴小阳, 时间限制, 1, 0), 1) , 前炮, 1, 0)
    return 后炮, True

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
    return 大肉, False

def tdx_tpcqpz(data, N = 55, M = 34):
    C = data.close
    CLOSE = data.close
    H = data.high
    HIGH = data.high
    # L = data.low
    HCV = (HHV(C, N) - LLV(C, N)) / LLV(C, N) * 100
    TJN = REF(H, 1) < REF(HHV(H, N), 1)
    XG = IFAND3(REF(HCV, 1) <= M, CLOSE > REF(HHV(HIGH, N), 1), TJN, 1, 0)
    return XG, False

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
    XG1 = IFAND5(X01 , X02 , X03 , X04 , X05 , X06, True, False)
    率土之滨XG = IFAND3(XG1, X07, X08, 1, 0)
    return 率土之滨XG, False

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
    return XG, False

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
    return 建仓, False

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
    耍无赖XG: IFAND(TJ == 0,   REF(TJ==1, 1), 1, 0)
    return 耍无赖XG, False

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
    return XG, False

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
    return IFOR(XG1, XG2, 1, 0), False

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
    return RTN, False

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
    return XG, False

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
    XG = IFAND(钻石底XG, INDEXC(data) < REF(INDEXC(data), 1) ,  REF(C > REF(C, 1), 1), 1, 0)
    return XG, False

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
    BAME=CROSS(X_21,(-25)) and C>REF(C,1)
    HJ_1=C/MA(C,40)
    HJ_2=C/MA(C,60)*100<71
    MOGU=CROSS(HJ_1,HJ_2)
    短线黑马XG:(DXHM and HMA) or (BAME and MOGU)

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
    return 妖股启动, False

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
    return XG, True

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
    return IFOR(暴利, 见龙, 1, 0), False

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
    # SZ5 = (VAR1 > VAR2, VAR2 > REF(VAR2, 1), VAR1 <> REF(VAR1, 1), CLOSE < VAR2)
    # OR(VAR1 > VAR2, VAR1 < REF(VAR1, 1), VAR2 < REF(VAR2, 1), CLOSE < VAR2)
    SZ6 = IFAND3(REF(VAR1, 1) > REF(VAR2, 1), VAR1 == VAR2, CLOSE < VAR2, True, False)
    XD11 = IFAND4(VAR1 < REF(VAR1, 1), VAR2 < REF(VAR2, 1), REF(VAR1, 1) == REF(VAR2, 1), CLOSE < VAR2, True, False)
    XD1 = IFAND(VAR1 == VAR2, IFOR(CLOSE < VAR2, XD11, True, False), True, False)
    XD2 = IFAND(VAR1 == VAR2, CLOSE > VAR1, True, False)
    SAT = (AMOUNT / C) / (HHV(AMOUNT, 20) / HHV(C, 20))
    量能饱和度 = IF(SAT > 1, 1, SAT) * 100
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
        刀 = (MC - JC) / JC * 1000 * 附加条件

    return 刀

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
    涨幅T = (C - REF(C,1)) / REF(C,1)
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
    return IFAND4(涨幅, 跳空, 限量, 多头, 1, 0)

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
    return 后炮, True
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
    MACDTJ = IFAND3(MACD > 0, DIF > 0, DEA > 0, True, False)

    # B_1 = IFAND3(TJ1 >= 0, REF(TJ1,1) < 0, MACDTJ, 1, 0)
    # B_1 = IFAND(TJ1 >= 0, REF(TJ1, 1) < 0, 1, 0)
    # B_1 = IFAND4(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, MACDTJ, 1, 0)
    B_1 = IFAND3(TJ1 > 0, REF(TJ1, 1) < 0, TJ2, 1, 0)
    S_1 = IFAND(TJ1 < 0, REF(TJ1, 1) > 0, 1, -1)
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
