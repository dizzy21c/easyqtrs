
# coding:utf-8
import sys
import traceback
import talib
import numpy as np
import pandas as pd
from pandas import Series
from .base import *
from .talib_series import LINEARREG_SLOPE as SLOPE

def udf_cross(A, B):
  if isinstance(A, float):
    A1 = A0 = A
    ls = len(B)
    B1 = B.iloc[ls -2]
    B0 = B.iloc[ls -1]
  elif isinstance(B, float):
    B1 = B0 = B
    ls = len(A)
    A1 = A.iloc[ls -2]
    A0 = A.iloc[ls -1]
  else:
    return SINGLE_CROSS(A,B)
    
  if A1 < B1 and A0 > B0:
    return True
  return False

def udf_ref_pct(A, B, N = 1):
  if len(A) < N + 1:
    return False
  C = A / REF(A, N)
  lc = len(C)
  return C[lc - 1] > B

def udf_dapan_risk_df(data_df, N1=6, N2=12):
  dsize = len(data_df)
  if dsize <= N2:
    return (False, None)

  return udf_dapan_risk(data_df.close, data_df.high, data_df.low, N1, N2) 

def udf_dapan_risk(C,H,L, N1=6, N2=12):
  dsize = len(C)
  if dsize <= N2:
    return (False, None)

  # C = data_df.close
  # H = data_df.high
  # L = data_df.low

  s0=3.5
  s5=3.3
  b3=1.3
  b5=0.5
  # VAR2 = talib.MIN(L, N1)
  # VAR3 = talib.MAX(H, N2)
  VAR2 = LLV(L, N1)
  VAR3 = HHV(H, N2)

  DLX=talib.EMA((C-VAR2)/(VAR3-VAR2)*4,4)

  flg = 0
  if udf_cross(DLX, b5):
    buy50 = 1
  else:
    buy50 = 0
  flg = flg + buy50

  if udf_cross(DLX, b3):
    buy30 = 1
  else:
    buy30 = 0
  flg = flg + buy30

  if udf_cross(DLX, s5):
    sell5 = 1
  else:
    sell5 = 0
  flg = flg + sell5
  
  if udf_cross(DLX, s0):
    sell0 = 1
  else:
    sell0 = 0

  flg = flg + sell0
  
  return (flg > 0, {'buy50':buy50, 'buy30':buy30, 'sell5':sell5, 'sella':sell0})

def udf_index_risk(data, N1=6, N2=12):
  qc=3.5
  jb=3.3
  j3=1.3
  j5=0.5
  L=data.low
  H=data.high
  C=data.close
  VAR2=LLV(L, N1)
  VAR3=HHV(H, N2)
  DLX=EMA(((C-VAR2)/(VAR3-VAR2))*4, 4)
  sj5=CROSS(DLX,j5)
  sj3=CROSS(DLX,j3)
  sjb=CROSS(DLX,jb)
  sqc=CROSS(DLX,qc)
  dict_rt = {'BUY50':sj5, 'ADD30':sj3, 'SELL50':sjb, 'SELL0':sqc}
  return pd.DataFrame(dict_rt)
  
def udf_base_check_df(data_df, N1=70, N2=144, N3=250):
  return udf_base_check(data_df.close, data_df.vol, N1, N2, N3)

def udf_base_check(C, V, N1=70, N2=144, N3=250):
  len_d = len(C)
  N = MAX(MAX(N1,N2),N3)
  if len_d < N:
    return (False, None)

  len_d -= 1
  # C = data_df.close
  # V = data_df.vol
  
  cn1 = C > MA(C, N1)
  cn2 = C > MA(C, N2)
  cn3 = C > MA(C, N3)
  
  return (cn1[len_d] or cn2[len_d] or cn3[len_d], {str(N1):cn1[len_d], str(N2):cn2[len_d], str(N3):cn3[len_d]})

def udf_hangqing_start_df(data_df, snum=13, lnum=144):#, sd=20, ld=250):
  return udf_hangqing_start(data_df.close, sum, lnum)

def udf_hangqing_start(C, snum=13, lnum=144):#, sd=20, ld=250):
  if len(C) < lnum:
    return False

  # C = data_df.close

  # A1 = (C-MA(C,lnum))/MA(C,lnum)*100
  # N1 = BARSLAST(CROSS(C,MA(C,lnum)), 1)
  # N2 = BARSLAST(CROSS(MA(C,lnum),C), 1)
  # B1 = IF(N1<N2,N1+1,0)
  # C1 = HHV(A1,B1)
  # D1 = (C-REF(C,B1))/REF(C,B1)*100
  N3 = BARSLAST(CROSS(C,MA(C,snum)))
  N4 = BARSLAST(CROSS(MA(C,snum),C))
  AA = IF(N3<N4,N3+1,0)
  BB = (C-REF(C,AA))/REF(C,AA)*100

  # IFAND(udf_cross(BB, 10.0), C/REF(C,1) > 1.05, True, False)
  return udf_cross(BB, 10.0) and udf_ref_pct(C, 1.05)

def udf_niu_check_df(data_df, n1 = 36, n2 = 30, n3 = 25):
  return udf_niu_check(data_df.close, data_df.high, data_df.low, data_df.vol, data_df.amount, n1, n2, n3)

def udf_niu_check(C,H,L,VOL,AMOUNT, n1 = 36, n2 = 30, n3 = 25):
  if len(C) > n1:
    return False

  # L = data_df.low
  # H = data_df.high
  # C=data_df.close
  # VOL=data_df.volume
  VARR24=LLV(L,36)
  VARR25=HHV(H,30)
  VARR26=EMA((C-VARR24)/(VARR25-VARR24)*4,4)*25
  VARB27=(((C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100)/2+22)*1
  VARB28=(((C -(((EMA(AMOUNT*100,13) /EMA(VOL,13)) / 100))) / (((EMA(AMOUNT*100,13) /EMA(VOL,13)) / 100))) * 100)
  # JD=((VARB28 < (0)) AND ((C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100)<VARB27-2 AND VARR26<10
  JD1 = (VARB28 < (0))
  JD2 = ((C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100)<VARB27-2
  JD3 = VARR26<10
  JD4=IFAND(JD1,JD2,JD1,False)
  JD=IFAND(JD4,JD3,JD4,False)
  CD=IF(JD,20,0)
  AAA=REF(CD,1)>0
  # BBB=CD=0
  # DR=AAA AND BBB
  # return JD OR DR
  RTN=IFOR(JD, AAA, True, False)
  lrtn = len(RTN)
  return RTN[lrtn - 1] or RTN[lrtn - 2] or RTN[lrtn - 3]

  
def udf_top_df(data_df):
  return udf_top(data_df.close, data_df.high, data_df.low)

def udf_top(C,H,L):
  # {涨停板次日跳空高开的选股}
  # REF(C,1)/REF(C,2)>1.098 AND REF(C,1)=REF(H,1) AND L>REF(H,1);
  len_d = len(C)
  if len_d < 2:
    return False
  
  # C=data_df.close
  # H=data_df.high
  # L=data_df.low
  
  A1=REF(C,1)/REF(C,2)>1.098
  A2=REF(C,1)==REF(H,1)
  A3=L>REF(H,1)
  
  A4 = IFAND(IFAND(A1,A2,True,False),A3,True,False)
  return A4[len_d - 1]
  
  
def udf_top_last(C, PCT = 9.8, M = 5, N=30):
  len_d = len(C) - 1
  if len_d < N:
    return False

  rtn = False
  if M <= 0:
    M = 5
  for i in range(0, M):
    A = (REF(C,i) - REF(C,i+1)) * 100 /REF(C,i+1) > PCT
    if A[len(A)-1]:
      rtn = True
      break
    
  return rtn

def udf_macd_zq(C,O,H,L):
  rtn = {'flg':False}
  len_d = len(C) - 1
  #macd zengqiang
  DIFF=EMA(C,12)-EMA(C,26)
  DEA=EMA(DIFF,9)
  #MACD=2*(DIFF-DEA), COLORSTICK
  MACD=2*(DIFF-DEA)
  #DI_JIN=CROSS(DIFF,DEA) AND DIFF<-0.1
  DI_JIN=IFAND(CROSS(DIFF,DEA), DIFF<-0.1, True, False)
  rtn['DI_JIN'] = cv = DI_JIN[len_d]
  if cv:
    rtn['flg'] = True
  #DRAWICON(DI_JIN,0.2,3)
  #DRAWTEXT(DI_JIN,0.2,'DI_JIN'),COLORBLACK
  JC=BARSLAST(DEA>=0)
  #JCCOUNT=COUNT(CROSS(DIFF,DEA),JC)
  JCCOUNT=COUNT(CROSS(DIFF,DEA),JC[len(JC)-1])
  #JC2=COUNT(JCCOUNT=2,21)=1
  JC2=COUNT(JCCOUNT==2,21)==1
  #ER_JIN=CROSS(DIFF,DEA) AND DEA<0 AND JC2
  ER_JIN=IFAND(IFAND(CROSS(DIFF,DEA), DEA<0, True, False), JC2,True,False)
  rtn['ER_JIN'] = cv = ER_JIN[len_d]
  if cv:
    rtn['flg'] = True
  #DRAWICON(ER_JIN,0.4,7)
  #DRAWTEXT(ER_JIN,0.4,'ER_JIN'),COLORYELL
  A1=BARSLAST(REF(CROSS(DIFF,DEA),1))
  #DI_BEI_LI=REF(C,A1+1)>C AND DIFF>REF(DIFF,A1+1) AND CROSS(DIFF,DEA),NODRAW
  DI_BEI_LI=IFAND(IFAND(REF(C,A1+1)>C, DIFF>REF(DIFF,A1+1),True,False), CROSS(DIFF,DEA), True,False)
  rtn['DI_BEI_LI'] = cv = DI_BEI_LI[len_d]
  if cv:
    rtn['flg'] = True
  #DRAWICON(DI_BEI_LI,0,1)
  #DRAWTEXT(DI_BEI_LI,0,'DI_BEI_LI'),COLORBLUE
  A2=BARSLAST(REF(CROSS(DEA,DIFF),1))
  #DING_BEI_LI=REF(C,A2+1)<C AND REF(DIFF,A2+1)>DIFF AND CROSS(DEA,DIFF)
  DING_BEI_LI=IFAND(IFAND(REF(C,A2+1)<C , REF(DIFF,A2+1)>DIFF, True,False) , CROSS(DEA,DIFF), True, False)
  rtn['DING_BEI_LI'] = cv = DING_BEI_LI[len_d]
  if cv:
    rtn['flg'] = True
  #DRAWTEXT(DING_BEI_LI,DEA,'DING_BEI_LI'),COLORBLUE
  #DRAWICON(DING_BEI_LI,DEA,2)
  #SAN_JIN=DI_JIN AND ER_JIN AND DI_BEI_LI,NODRAW
  SAN_JIN=IFAND(IFAND(DI_JIN , ER_JIN , True,False), DI_BEI_LI,True, False)
  rtn['SAN_JIN'] = cv = SAN_JIN[len_d]
  if cv:
    rtn['flg'] = True
  #DRAWICON(SAN_JIN,0.6,16)
  #DRAWTEXT(SAN_JIN,0.6,'SAN_JIN'),COLORRED,LINETHICK2
  ### #HONG_MIANJI=SUM(MACD,BARSLAST(MACD<0))*(MACD>0),COLOR0000FF,NODRAW
  ### HONG_MIANJI=SUMS(MACD,BARSLAST(MACD<0))*MACD(MACD>0))
  ### #LV_MIANJI=SUM(MACD,BARSLAST(MACD>0))*(MACD<0),COLORFFFF00,NODRAW
  ### LV_MIANJI=SUMS(MACD,BARSLAST(MACD>0)) #*(MACD<0)
  ### AA=REF(LV_MIANJI,1)*100
  ### BB=REF(HONG_MIANJI,1)*100
  ### #DRAWNUMBER(CROSS(0,MACD),HHV(REF(MACD,1),5)+0.03,ABS(BB)),COLORRED
  ### #DRAWNUMBER(CROSS(MACD,0),LLV(REF(MACD,1),5)-0.03,ABS(AA)),COLORBLUE
  JC3 = DEA-DIFF
  #LVZHU_MIANJI=IF(MACD<0,SUM(MACD,BARSLAST(JC3<0)),0)
  LVZHU_MIANJI=SUMS(MACD,BARSLAST(JC3<0))
  #HONGZHU_MIANJI=IF(MACD>0,SUM(MACD,BARSLAST(JC3>0)),0)
  HONGZHU_MIANJI=SUMS(MACD,BARSLAST(JC3>0))
  BEN_CI_LLV=LLV(L,BARSLAST(JC3<0))
  BEN_CI_HHV=HHV(H,BARSLAST(JC3>0))
  X1=IF (MACD<0,BARSLAST(CROSS(DIFF,DEA)),0)
  ### QIAN_CI_LVZHU_MIANJI=REF(LVZHU_MIANJI,X1+1)
  QIAN_CI_LLV=REF(BEN_CI_LLV,X1+1)
  #Y1=IF((LVZHU_MIANJI<0 AND ABS(LVZHU_MIANJI) AND BEN_CI_LLV<QIAN_CI_LLV ),1,0)
  Y1=IFAND( IFAND(LVZHU_MIANJI<0 , ABS(LVZHU_MIANJI),True,False), BEN_CI_LLV<QIAN_CI_LLV , 1, 0)
  ### RS1= MACD<0 AND REF(MACD,1)<0 AND C<QIAN_CI_LLV AND ABS(LVZHU_MIANJI)
  DI_BEI_CI=IF(CROSS(DIFF,DEA),REF(Y1,1),0) #,NODRAW
  X2=IF (MACD>0,BARSLAST(CROSS(DEA,DIFF)),0)
  QIAN_CI_HONGZHU_MIANJI=REF(HONGZHU_MIANJI,X2+1)
  QIAN_CI_HHV=REF(BEN_CI_HHV,X2+1)
  #Y2=IF((HONGZHU_MIANJI>0 AND HONGZHU_MIANJI<QIAN_CI_HONGZHU_MIANJI AND BEN_CI_HHV>QIAN_CI_HHV ),1,0)
  Y2=IFAND(IFAND(HONGZHU_MIANJI>0 , HONGZHU_MIANJI<QIAN_CI_HONGZHU_MIANJI, True, False) , BEN_CI_HHV>QIAN_CI_HHV ,1,0)
  ### RS2= MACD>0 AND REF(MACD,1)>0 AND C>QIAN_CI_HHV AND ABS(HONGZHU_MIANJI)
  DING_BEI_CI=IF(CROSS(DEA,DIFF),REF(Y2,1),0) #,NODRAW
  rtn['DI_BEI_CI'] = cv = DI_BEI_CI[len_d]
  if cv > 0:
    rtn['flg'] = True
  rtn['DING_BEI_CI'] = cv = DING_BEI_CI[len_d]
  if cv > 0:
    rtn['flg'] = True
  #DRAWICON(DI_BEI_CI,DEA,1)
  #DRAWTEXT(DI_BEI_CI,DEA,'DI_BEI_CI'),COLORRED
  #DRAWICON(DING_BEI_CI,DIFF,2)
  #DRAWTEXT(DING_BEI_CI,DIFF,'DING_BEI_CI'),COLORBLUE

  return rtn

def udf_yao_check_df(data):
  return udf_yao_check(data.close, data.open, data.high, data.low, data.vol)

def udf_yao_check(C,OPEN,HIGH,LOW,VOL):
  ##妖股公式
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
  result=pd.DataFrame({"cross":CROSS(VAR0, VAR1), "var4":VAR4, "var9": VAR9})
  # FLCS = CROSS(VAR0,VAR1) AND VAR4,COLORMAGENTA
  result['FLCS'] = result.apply(lambda x : x['cross'] > 0 and x['var4'], axis=1)
  # FLTP = (CROSS(VAR0,VAR1) AND VAR4) AND VAR9,COLORRED,LINETHICK2
  result['FLTP'] = result.apply(lambda x : x['cross'] > 0 and x['var4'] and x['var9'], axis=1)
  return result

def udf_ctlsb_check(C,N1=2,N2=21,N3=20,N4=42):
  BL=EMA(C,N1)
  SL=EMA(SLOPE(C,N2)*N3 + C, N4)
  BF=SINGLE_CROSS(BL,SL)
  SF=SINGLE_CROSS(SL,BL)
  return {'buy':BF,'sell':SF}
  # 买线:EMA(C,2),COLOR0000AA;
  # 卖线:EMA(SLOPE(C,21)*20+C,42),POINTDOT,COLOR0000CC,LINETHICK3;
  # BUY:=CROSS(买线,卖线);
  # SEL:=CROSS(卖线,买线);
  # DRAWTEXT(BUY,LOW*0.99,'B'),COLORF00FF0,LINETHICK5;
  # DRAWTEXT(SEL,HIGH*1.01,'S'),COLORWHITE,LINETHICK5;
