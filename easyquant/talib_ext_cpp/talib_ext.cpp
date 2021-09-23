
#include "talib_ext.h"

//=============================================================================
// 数学函数部分
//=============================================================================
void sum_list(int nCount, float *pOut, float *pData, int *pNum)
{
  float t_sum = 0.0;

  for (int i = 0; i < nCount; i++)
  {
    if (pNum[i] > 0) {
      t_sum += pData[i];
    } else {
      t_sum = 0.0;
    }

    pOut[i] = t_sum;
  }
}

void barslast_list(int nCount, int *pOut, float *pData, int pNum)
{
  int t_sum = 0.0;

  for (int i = 0; i < nCount; i++)
  {
    if (pData[i] > pNum) {
      t_sum = 0;
    } else {
      t_sum += 1;
    }

    pOut[i] = t_sum;
  }
}

void hhv_list(int nCount, float *pOut, float *pData, int *pNum)
{
//  float t_max = 0.0;
//  for (int i = 0; i < nCount; i++) {
//    if (t_max < pData[i]) {
//        t_max = pData[i];
//    }
//  }

  for (int i = 0; i < nCount; i++)
  {
    float t_out = 0.0;
    int pos = pNum[i];
    if (pos > 0) {
        int pre_pos = i > pos ? i - pos + 1 : 0;
        for(int j = pre_pos; j < i + 1; j++) {
            if (t_out < pData[j]) {
                t_out = pData[j];
            }
        }
    } else {
//        t_out = t_max;
        t_out = pData[i];
    }
    pOut[i] = t_out;
  }
}

void llv_list(int nCount, float *pOut, float *pData, int *pNum)
{
  for (int i = 0; i < nCount; i++)
  {
    float t_out = 9999999999999.0;
    int pos = pNum[i];
    if (pos > 0) {
        int pre_pos = i > pos ? i - pos : 0;
        for(int j = pre_pos; j < i + 1; j++) {
            if (t_out > pData[j]) {
                t_out = pData[j];
            }
        }
    } else {
        t_out = pData[i];
    }
    pOut[i] = t_out;
  }
}

void dma_list(int nCount, float *pOut, float *pData, float *pWeight)
{
  float preOut = 0.0;
  for (int i = 0; i < nCount; i++)
  {
    float t_out = 0.0;
    float weight = pWeight[i];
    if (i < 1) {
        t_out = pData[i];
    } else {
        t_out = pData[i] * weight + (1 - weight) * preOut;
    }
    pOut[i] = t_out;
    preOut = t_out;
  }
}

int Parse2(int nCount, float *pOut, float *pHigh, float *pLow)
{
  int nSpan = 0;
  int nCurrTop = 0, nPrevTop = 0;
  int nCurrBot = 0, nPrevBot = 0;

  for (int i = 0; i < nCount; i++)
  {
    // 遇到高点，合并化简上升段（上下上）
    if (pOut[i] == 1)
    {
      // 更新位置信息
      nPrevTop = nCurrTop;
      nCurrTop = i;

      // 存在小于五根的线段，去除中间一段
      if ((pHigh[nCurrTop] >= pHigh[nPrevTop]) &&
          (pLow [nCurrBot] >  pLow [nPrevBot]))
      {
        // 检查合法性（严格按照连续五根形成一笔）
        if (((nCurrTop - nCurrBot < 4) && (nCount   - nCurrTop > 4)) ||
             (nCurrBot - nPrevTop < 4) || (nPrevTop - nPrevBot < 4))
        {
          pOut[nCurrBot] = 0;
          pOut[nPrevTop] = 0;
        }
        else if (nCount - nCurrTop > 4)
        {
          // 检查第三段（上）K线合并
          nSpan = nCurrTop - nCurrBot;
          for (int j = nCurrBot; j < nCurrTop; j++)
          {
            if ((pHigh[j] >= pHigh[j+1]) && (pLow[j] <= pLow[j+1]))
            {
              nSpan--;
            } else if ((pHigh[j] < pHigh[j+1]) && (pLow[j] > pLow[j+1])) {
              nSpan--;
            }
          }
          if (nSpan < 4)
          {
            pOut[nCurrBot] = 0;
            pOut[nPrevTop] = 0;
          }

          // 检查第二段（下）K线合并
          nSpan = nCurrBot - nPrevTop;
          for (int j = nPrevTop; j < nCurrBot; j++)
          {
            if ((pHigh[j] >= pHigh[j+1]) && (pLow[j] <= pLow[j+1]))
            {
              nSpan--;
            } else if ((pHigh[j] < pHigh[j+1]) && (pLow[j] > pLow[j+1])) {
              nSpan--;
            }
          }
          if (nSpan < 4)
          {
            pOut[nCurrBot] = 0;
            pOut[nPrevTop] = 0;
          }

          // 检查第一段（上）K线合并
          nSpan = nPrevTop - nPrevBot;
          for (int j = nPrevBot; j < nPrevTop; j++)
          {
            if ((pHigh[j] >= pHigh[j+1]) && (pLow[j] <= pLow[j+1]))
            {
              nSpan--;
            } else if ((pHigh[j] < pHigh[j+1]) && (pLow[j] > pLow[j+1])) {
              nSpan--;
            }
          }
          if (nSpan < 4)
          {
            pOut[nCurrBot] = 0;
            pOut[nPrevTop] = 0;
          }
        }
      }
    }

    // 遇到低点，合并化简下降段（下上下）
    if (pOut[i] == -1)
    {
      // 更新位置信息
      nPrevBot = nCurrBot;
      nCurrBot = i;

      // 存在小于五根的线段，去除中间一段
      if ((pLow [nCurrBot] <= pLow [nPrevBot]) &&
          (pHigh[nCurrTop] <  pHigh[nPrevTop]))
      {
        // 检查合法性（严格按照连续五根形成一笔）
        if (((nCurrBot - nCurrTop < 4) && (nCount   - nCurrBot > 4)) ||
             (nCurrTop - nPrevBot < 4) || (nPrevBot - nPrevTop < 4))
        {
          pOut[nCurrTop] = 0;
          pOut[nPrevBot] = 0;
        }
        else if (nCount - nCurrBot > 4)
        {
          // 检查第三段（下）K线合并
          nSpan = nCurrBot - nCurrTop;
          for (int j = nCurrTop; j < nCurrBot; j++)
          {
            if ((pHigh[j] >= pHigh[j+1]) && (pLow[j] <= pLow[j+1]))
            {
              nSpan--;
            } else if ((pHigh[j] < pHigh[j+1]) && (pLow[j] > pLow[j+1])) {
              nSpan--;
            }
          }
          if (nSpan < 4)
          {
            pOut[nCurrTop] = 0;
            pOut[nPrevBot] = 0;
          }

          // 检查第二段（上）K线合并
          nSpan = nCurrTop - nPrevBot;
          for (int j = nPrevBot; j < nCurrTop; j++)
          {
            if ((pHigh[j] >= pHigh[j+1]) && (pLow[j] <= pLow[j+1]))
            {
              nSpan--;
            } else if ((pHigh[j] < pHigh[j+1]) && (pLow[j] > pLow[j+1])) {
              nSpan--;
            }
          }
          if (nSpan < 4)
          {
            pOut[nCurrTop] = 0;
            pOut[nPrevBot] = 0;
          }

          // 检查第一段（下）K线合并
          nSpan = nPrevBot - nPrevTop;
          for (int j = nPrevTop; j < nPrevBot; j++)
          {
            if ((pHigh[j] >= pHigh[j+1]) && (pLow[j] <= pLow[j+1]))
            {
              nSpan--;
            } else if ((pHigh[j] < pHigh[j+1]) && (pLow[j] > pLow[j+1])) {
              nSpan--;
            }
          }
          if (nSpan < 4)
          {
            pOut[nCurrTop] = 0;
            pOut[nPrevBot] = 0;
          }
        }
      }
    }
  }
}

//=============================================================================
// 输出函数1号：线段高低点标记信号
//=============================================================================

void sum(int nCount, float *pfOut, float *pfIn, int *piIn)
{
  sum_list(nCount, pfOut, pfIn, piIn);
}

void barslast(int nCount, int *piOut, float *pfIn, int iIn)
{
  barslast_list(nCount, piOut, pfIn, iIn);
}

void hhv(int nCount, float *pfOut, float *pfIn, int *piIn2)
{
  hhv_list(nCount, pfOut, pfIn, piIn2);
}

void llv(int nCount, float *pfOut, float *pfIn, int *piIn2)
{
  llv_list(nCount, pfOut, pfIn, piIn2);
}

void dma(int nCount, float *pfOut, float *pfIn, float *pfWeight)
{
  dma_list(nCount, pfOut, pfIn, pfWeight);
}
