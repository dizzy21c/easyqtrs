/************************************************************************/
/* 
缠论核心模块实现
单例模式
所有Chanlun接口中缠论核心函数在此实现
*/
/************************************************************************/
#ifndef __CHANLUNCORE_H_INCLUDE
#define __CHANLUNCORE_H_INCLUDE

// #include "FxjFunc.h"
#include <list>

using namespace std;

#define NULL 0

///////////////////////////////////////////////////////////////////////////
//分析周期
enum DATA_TYPE
{
	TICK_DATA=2,				//分笔成交
	MIN1_DATA,					//1分钟线
	MIN5_DATA,					//5分钟线					
	MIN15_DATA,					//15分钟线
	MIN30_DATA,					//30分钟线
	MIN60_DATA,					//60分钟线
	DAY_DATA,					//日线
	WEEK_DATA,					//周线
	MONTH_DATA,					//月线
	MULTI_DATA					//多日线
};

///////////////////////////////////////////////////////////////////////////
//基本数据

typedef struct tagSTKDATA	
{
	// time_t	m_time;			//时间,UCT
	float	m_fOpen;		//开盘
	float	m_fHigh;		//最高
	float	m_fLow;			//最低
	float	m_fClose;		//收盘
	float	m_fVolume;		//成交量
	float	m_fAmount;		//成交额
	// WORD	m_wAdvance;		//上涨家数(仅大盘有效)
	// WORD	m_wDecline;		//下跌家数(仅大盘有效)
} STKDATA;


////////////////////////////////////////////////////////////////////////////
//扩展数据,用于描述分笔成交数据的买卖盘

typedef union tagSTKDATAEx
{
	struct
	{
		float m_fBuyPrice[3];		//买1--买3价
		float m_fBuyVol[3];			//买1--买3量
		float m_fSellPrice[3];		//卖1--卖3价	
		float m_fSellVol[3];		//卖1--卖3量
	};
	float m_fDataEx[12];			//保留
} STKDATAEx;

typedef struct tagCALCINFO
{
	// const DWORD			m_dwSize;				//结构大小
	// const DWORD			m_dwVersion;			//调用软件版本(V2.10 : 0x210)
	// const DWORD			m_dwSerial;				//调用软件序列号
	// const char*			m_strStkLabel;			//股票代码
	// const BOOL			m_bIndex;				//大盘

	const int			m_nNumData;				//数据数量(pData,pDataEx,pResultBuf数据数量)
	const STKDATA*		m_pData;				//常规数据,注意:当m_nNumData==0时可能为 NULL
	const STKDATAEx*	m_pDataEx;				//扩展数据,分笔成交买卖盘,注意:可能为 NULL

	const int			m_nParam1Start;			//参数1有效位置
	const float*		m_pfParam1;				//调用参数1	
	const float*		m_pfParam2;				//调用参数2
	const float*		m_pfParam3;				//调用参数3
	const float*		m_pfParam4;				//调用参数3

	float*				m_pResultBuf;			//结果缓冲区
	const DATA_TYPE		m_dataType;				//数据类型
	const float*		m_pfFinData;			//财务数据
} CALCINFO;


// 定义基本数据
// 缠论K线结构
// 处理过包含关系的K线
typedef struct chankx
{
	int no;				// K线序号 从1开始是
	float rhigh;		// 高值
	float rlow;			// 低值
	float high;			// 包含处理后的高值
	float low;			// 包含处理后的低值
	int	flag;			// 1顶 -1底 0 非顶底
	float fxqj;			// 分型区间 如果为顶底 记录区间边界
	int dir;			// K线方向 1上 -1下 2 上包含 -2 下包含
	int bi;				// 笔 1上 -1下 2 上包含 -2 下包含
	int duan;			// 段 1上 -1下 2 上包含 -2 下包含
} ckx;

// 笔 (特征序列)
typedef struct chanbi
{
	int no;				// 序号
	int noh;			// 高点K线编号
	int nol;			// 低点K线编号
	float high;			// 高点
	float low;			// 低点
	int dir;			// 方向 方向 1上 -1下 2 上包含 -2 下包含
	int flag;			// 1顶 -1底
	int qk;				// 特征1 2 之间是否存在缺口 
} cbi;

// 段
typedef struct chanduan
{
	int no;				// 序号
	int noh;			// 高点K线编号
	int nol;			// 低点K线编号
	float high;			// 高点
	float low;			// 低点
	int flag;			// 1顶 -1底
	int binum;			// 包含几笔
} cduan;

// 走势中枢
typedef struct chanzhongshu
{
	int no;				// 序号
	int duanno;			// 段序号
	int flag;			// 走势方向 1上 -1下
	int ksno;			// zg所在K线NO (有zg必有zd)
	int jsno;			// zd所在K线NO
	int znnum;			// 包含zn数
	float zg;			// ZG=min(g1、g2)
	float zd;			// ZD=max(d1、d2)
	float gg;			// GG=max(gn);
	float dd;			// dd=min(dn);
	float zz;			// 震荡中轴(监视器)
} czhongshu;
//定义基本数据END

typedef list<ckx> KXDATA;
typedef list<cbi> BIDATA;
typedef list<cduan> DUANDATA;
typedef list<czhongshu> ZSDATA;

typedef list<ckx>::iterator CKXIT;
typedef list<cbi>::iterator BIIT;
typedef list<cduan>::iterator DUANIT;
typedef list<czhongshu>::iterator ZSIT;

typedef list<ckx>::const_iterator C_CKXIT;
typedef list<cbi>::const_iterator C_BIIT;
typedef list<cduan>::const_iterator C_DUANIT;
typedef list<czhongshu>::const_iterator C_ZSIT;

// 缠论核心实现
class ChanlunCore
{
private:
	ChanlunCore();		// 构造函数
	~ChanlunCore();		// 析构函数

	static ChanlunCore* instance;

	KXDATA kxData;		// 根据缠论处理过的K线
	BIDATA xbData;		// 向下笔 （向上笔开始的段的特征序列）
	BIDATA sbData;		// 向上笔 （向下笔开始的段的特征序列）
	DUANDATA dData;		// 段
	ZSDATA zsData;		// 中枢
	
	float biQuekou;
	int firstDuanDir;

	void initBiQK(CALCINFO* pData);		// 初始化缺口
	void initTZXL();					// 初始化特征分型
	void initDuanList();				// 初始化段

	BIIT findTZG(int fromNo);			// 查找特征序列的顶分型
	BIIT findTZD(int fromNo);			// 查找特征序列的底分型
	
	void findFanTanZS(int duanno, int begin, int end, int high, int low);	// 查找下跌段中枢
	void findHuiTiaoZS(int duanno, int begin, int end, int high, int low);	// 查找上升段中枢

public:
	static ChanlunCore* GetInstance();		// 获取唯一实例
	
	void initKx(CALCINFO* pData);	// 初始化缠论K线
	void initFX();					// 初始化分型
	void initBi();					// 初始化笔
	void initDuan();				// 初始化段
	void initZhongshu();			// 初始化中枢

	CKXIT getCKX(int num);

	// Getter
	KXDATA getCkxData();
	BIDATA getXbData();
	BIDATA getSbData(); 
	DUANDATA getDuanData();
	ZSDATA getZsData();

	// 自定义常量
	// 方向 1向上 -1向下
	static const int DIR_0;
	static const int DIR_UP;
	static const int DIR_DN;
	static const int DIR_SBH;
	static const int DIR_XBH;
	
	static const int QK_N; // 不存在缺口
	static const int QK_Y; // 存在缺口
};

#endif // __CHANLUNTOOLS_H_INCLUDE