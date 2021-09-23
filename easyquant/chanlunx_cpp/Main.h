#ifndef __MAIN_H__
#define __MAIN_H__

#include <float.h>
#include <vector>
// #include "ChanlunZb.h"
// #include "ChanlunXg.h"
#include "Bi.h"
#include "Duan.h"
#include "ZhongShu.h"

#define BOOL int
#define TRUE 1
#define FALSE 0

#define DLL_PUBLIC __attribute__ ((visibility("default")))

#ifdef __cplusplus
extern "C" {
#endif
  DLL_PUBLIC void Func1(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);
  
  DLL_PUBLIC void Func2(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);

  DLL_PUBLIC void Func3(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);

  DLL_PUBLIC void Func4(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);

  DLL_PUBLIC void Func5(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);

  DLL_PUBLIC void Func6(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);

  DLL_PUBLIC void Func7(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);

  DLL_PUBLIC void Func8(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);

  DLL_PUBLIC int addBuf(char* data, int num, char* outData);

    // subBuf* subBuf_new(){ return new subBuf(); }
    // int subBuf_sub(subBuf* subfuf, char* data, int num, char* outData){ subfuf->cursubBuf(data, num, outData); }
#ifdef __cplusplus
}
#endif

#endif
