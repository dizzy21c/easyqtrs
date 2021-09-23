/*****************************************************************************
 * ���ۿ��ӻ�����ϵͳ
 * Copyright (C) 2016, Martin Tang

 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *****************************************************************************/

#ifndef __FXSelector_h__
#define __FXSelector_h__
#pragma pack(push,1)

#define ASK_ALL -1
#define INVDATA 0xf8f8f8f8

// NTimeʱ����Ϣ
typedef struct tag_NTime
{
  unsigned short  year;
  unsigned char month;
  unsigned char day;
  unsigned char hour;
  unsigned char minute;
  unsigned char second;
} NTime;

// ��������
typedef struct tag_HISDAT
{
  NTime Time;             // ʱ��
  float Open;             // ���̼�
  float High;             // ��߼�
  float Low;              // ��ͼ�
  float Close;            // ���̼�
  union
  {
    float Amount;         // �ɽ����
    DWORD VolInStock;     // �ֲ���(�ڻ���Ч)
  };
  float fVolume;          // �ɽ���
  union 
  { 
    float Settle;         // �����(�ڻ���Ч)
    long  lYClose;
    struct
    {   
      WORD up;            // ���Ǽ���(ָ����Ч)
      WORD down;          // �µ�����(ָ����Ч)
    }zd;
  };
} HISDAT,*LPHISDAT;

// ��������(�ڶ���)
typedef struct tag_REPORTDAT2
{
  DWORD ItemNum;          // ��������
  float Close;            // ǰ���̼�
  float Open;             // ���̼�
  float Max;              // ��߼�
  float Min;              // ��ͼ�
  float Now;              // �ּ�
  DWORD RefreshNum;       // ˢ����
  DWORD Volume;           // ����
  DWORD NowVol;           // ����(���ֲ�)
  float Amount;           // �ܳɽ����
  DWORD Inside;           // ����
  DWORD Outside;          // ����
  float TickDiff;         // ���ǵ�(��λ��)
  BYTE  InOutFlag;        // �����̱�־ 0:Buy 1:Sell 2:None
  DWORD CJBS;             // �ɽ�����
  float Jjjz;             // ����ֵ
  union
  {
    struct  // ����
    {
      float Buyp[5];      // ��������
      DWORD Buyv[5];      // ��Ӧ�������۵��������
      float Sellp[5];     // ���������
      DWORD Sellv[5];     // ��Ӧ��������۵��������
    } Ggpv;
    struct  // ָ��
    {
      float LxValue;      // ����ָ��
      float Yield;        // ������Ȩ��ָ��
      long  UpHome;       // ���Ǽ���
      long  DownHome;     // �µ�����
    } Zspv;
  } Other;
  char  ununsed[20];      // ����
} REPORTDAT2,*LPREPORTDAT2;


// Ʒ�ֻ�������
typedef struct tag_STOCKINFO 
{
  char    Name[9];        // ֤ȯ����
  short   Unit;           // ���׵�λ 
  long    VolBase;        // ���ȵĻ���
  short   Fz[8];          // ������ʱ��(4��)
  short   InitTimer;      // ��ʼ��ʱ��
  short   EndTimer;       // ����ʱ��
  short   nDelayMin;      // ��ʱ������
  char    bBelongHS300;   // �Ƿ����ڻ���300���
  char    bBelongHasKQZ;  // �Ƿ����ں���תծ���
  char    nBelongRZRQ;    // �Ƿ�����������ȯ���
  char    bQH;            // �Ƿ����ڻ�Ʒ��
  char    bHKGP;          // �Ƿ��Ǹ۹�Ʒ��
  short   QHVol_BaseRate; // �ڻ���ÿ�ֳ���
  float   MinPrice;       // ��С�䶯��λ
  char    unused[1];      // ����
  float   ActiveCapital;  // ��ͨ�ɱ�
  long    J_start;        // ��������
  short   J_addr;         // ����ʡ��
  short   J_hy;           // ������ҵ
  float   J_zgb;          // �ܹɱ�
  float   J_zjhhy;        // ֤�����ҵ
  float   J_oldjly;       // ������ھ�����
  float   J_oldzysy;      // �������Ӫҵ����
  float   J_bg;           // B��
  float   J_hg;           // H��
  float   J_mgsy2;        // ����ÿ������ (�Ʊ����ṩ��ÿ������,������Ĳ���)
  float   J_zzc;          // ���ʲ�(Ԫ)
  float   J_ldzc;         // �����ʲ�
  float   J_gdzc;         // �̶��ʲ�
  float   J_wxzc;         // �����ʲ�
  float   J_gdrs;         // �ɶ�����
  float   J_ldfz;         // ������ծ
  float   J_cqfz;         // �����ɶ�Ȩ��
  float   J_zbgjj;        // �ʱ�������
  float   J_jzc;          // �ɶ�Ȩ��(���Ǿ��ʲ�)
  float   J_yysy;         // Ӫҵ����
  float   J_yycb;         // Ӫҵ�ɱ�
  float   J_yszk;         // Ӧ���ʿ�
  float   J_yyly;         // Ӫҵ����
  float   J_tzsy;         // Ͷ������
  float   J_jyxjl;        // ��Ӫ�ֽ�����
  float   J_zxjl;         // ���ֽ�����
  float   J_ch;           // ���
  float   J_lyze;         // �����ܶ�
  float   J_shly;         // ˰������
  float   J_jly;          // ������
  float   J_wfply;        // δ��������
  float   J_mgjzc2;       // ����ÿ�ɾ��ʲ� (�Ʊ����ṩ��ÿ������,������Ĳ���)
  float   J_jyl;          // ������%
  float   J_mgwfp;        // ÿ��δ����
  float   J_mgsy;         // ÿ������(�����ȫ���)
  float   J_mggjj;        // ÿ�ɹ�����
  float   J_mgjzc;        // ÿ�ɾ��ʲ�
  float   J_gdqyb;        // �ɶ�Ȩ���
} STOCKINFO,*LPSTOCKINFO;

// �ɱ��ܹɱ���Ϣ
typedef struct tag_GBInfo
{
  float Zgb;
  float Ltgb;
} GBINFO,*LPGBINFO;

// ��Ʊ�ǵ�ͣ�۸�����
typedef struct tag_TPPrice
{
  float Close;
  float TPTop;
  float TPBottom;
} TPPRICE,*LPTPPRICE;

// ���ݻص�������
#define PER_MIN5      0     // 5��������
#define PER_MIN15     1     // 15��������
#define PER_MIN30     2     // 30��������
#define PER_HOUR      3     // 1Сʱ����
#define PER_DAY       4     // ��������
#define PER_WEEK      5     // ��������
#define PER_MONTH     6     // ��������
#define PER_MIN1      7     // 1��������
#define PER_MINN      8     // ���������(10)
#define PER_DAYN      9     // ����������(45)
#define PER_SEASON    10    // ��������
#define PER_YEAR      11    // ��������
#define PER_SEC5      12    // 5����
#define PER_SECN      13    // ������(15)
#define PER_PRD_DIY0  14    // DIY����
#define PER_PRD_DIY10 24    // DIY����
#define REPORT_DAT2   102   // ��������(�ڶ���)
#define GBINFO_DAT    103   // �ɱ���Ϣ
#define STKINFO_DAT   105   // ��Ʊ�������
#define TPPRICE_DAT   121   // �ǵ�ͣ����

// ������Ϣ�Ľṹ����
typedef struct tag_PluginPara
{
  char  acParaName[14];     // ��������������
  int   nMin;               // ������Сȡֵ��Χ
  int   nMax;               // �������ȡֵ��Χ
  int   nDefault;           // ϵͳ�Ƽ���ȱʡֵ
  int   nValue;             // �û������ֵ
} PLUGINPARAM;

typedef struct tag_PlugInfo
{
  char  Name[50];           // ������汾
  char  Dy[30];             // ����
  char  Author[30];         // �����
  char  Descript[100];      // ѡ������
  char  Period[30];         // ��Ӧ����
  char  OtherInfo[300];
  short ParamNum;           // 0<=��������<=4
  PLUGINPARAM ParamInfo[4]; // ������Ϣ������
} PLUGIN,*LPPLUGIN;

// 1. CodeΪ��Ʊ���룬��������ָ֤��������ֵΪ999999
// 2. nSetCodeΪ�г����࣬0Ϊ���У�1Ϊ����
// 3. DataTypeΪ�����������ͣ�ȱʡΪ��K����ʷ���ݣ�����������������ֵΪ
//    REPORT_DAT2������������Ͳμ�OutStruct.h
// 4. pDataΪ�������ݻ���������ΪNULL��nDataNumΪ-1����������ʷ���ݸ���
// 5. nDataNumΪ�������ݸ�������Ϊ-1��pDataΪNULL����������ʷ���ݸ���
// 6. 2��NtimeΪ�������ݵ�ʱ�䷶Χ��ȱʡΪȫ��������ʷ����
// 7. nTQ�Ƿ�Ϊ��ȷ��Ȩ

// �ص�����,ȡ���ݽӿ�
typedef long(CALLBACK * PDATAIOFUNC)(char *Code, short nSetCode, short DataType, void *pData, short nDataNum, NTime ntTime1, NTime ntTime2, BYTE nTQ, unsigned long);

#ifdef __cplusplus
extern "C" {
#endif

// ע��ص�����
DECLSPEC_EXPORT void RegisterDataInterface(PDATAIOFUNC pfn);

// �õ���Ȩ��Ϣ
DECLSPEC_EXPORT void GetCopyRightInfo(LPPLUGIN info);

// ��������ݼ���(nDataNumΪASK_ALL��ʾ��������)
DECLSPEC_EXPORT BOOL InputInfoThenCalc1(char * Code,short nSetCode,int Value[4],short DataType,short nDataNum,BYTE nTQ,unsigned long unused);

// ѡȡ���μ���
DECLSPEC_EXPORT BOOL InputInfoThenCalc2(char * Code,short nSetCode,int Value[4],short DataType,NTime time1, NTime time2, BYTE nTQ,unsigned long unused); 

#ifdef __cplusplus
};
#endif

#pragma pack(pop)
#endif
