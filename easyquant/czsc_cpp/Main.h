/*****************************************************************************
 * Visual K-Line Analysing System For Zen Theory
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

#ifndef __MAIN_H__
#define __MAIN_H__

#include <float.h>
// #include "FXIndicator.h"
#include "CCentroid.h"

#define DLL_PUBLIC __attribute__ ((visibility("default")))

#ifdef __cplusplus
extern "C" {
#endif
  // DLL_PUBLIC void Func1(int nCount, float *pOut, float *pHigh, float *pLow, float *pIgnore);
  DLL_PUBLIC void Func1(int nCount, float *pOut, float *pHigh, float *pLow, int pIgnore);
  
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
