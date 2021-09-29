
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

void calcuJUN(int *npChip, Dict *dpOutChip, DictNode *dpOutChipList, int nCount, float highT, float lowT, float volT, float TurnoverRateT, float minD, int AC) {

}

void calcuSin(int *npChip, Dict *dpOutChip, DictNode *dpOutChipList, int nCount, float highT, float lowT,float avgT, float volT, float TurnoverRateT, float minD, int AC) {
//    TurnoverRateT = TurnoverRateT / 1;
    float l = (highT * 100 - lowT * 100 ) / 100 / minD;
    if (highT == lowT) {
        lowT = lowT - minD;
        l = 1.0;
    }
    int length = floor(l);
    float *x = (float *) malloc((length + 1) * sizeof(float));
//    float *x = new float(length);
    for(int i = 0; i < length; i++) {
//        length ++;
        x[i] = round((lowT + i * minD) * 100) / 100;
    }

//        #计算仅仅今日的筹码分布
    Dict *tmpChip = (Dict *) malloc((length+1) * sizeof(Dict));
//    int nTmpChip = 0;
    float eachV = volT / length;
//        #极限法分割去逼近
    for(int i = 0; i < length; i++) {
        float x1 = x[i];
        float x2 = x[i] + minD;
        float h = 2 / (highT - lowT);
        float s = 0;
        if (x[i]  < avgT) {
            float y1 = h /(avgT - lowT) * (x1 - lowT);
            float y2 = h /(avgT - lowT) * (x2 - lowT);
            s = minD *(y1 + y2) / 2;
            s = s * volT;
        } else {
            float y1 = h /(highT - avgT) *(highT - x1);
            float y2 = h /(highT - avgT) *(highT - x2);

            s = minD *(y1 + y2) /2;
            s = s * volT;
        }
        Dict dict = {int(round(x1 * 100)), s};
        tmpChip[i] = dict;
    }

    free(x);

    for (int i = 0; i < *npChip; i++) {
        Dict item = dpOutChip[i];
        item.value = item.value *(1 -TurnoverRateT * AC);
        dpOutChip[i] = item;
    }

    for(int i = 0; i < length; i++) {
        Dict tmp = tmpChip[i];
        int iFind = 0;
//        if (*npChip > 0) {
        for (int j = 0; j < *npChip; j++) {
            Dict chip = dpOutChip[j];
            if (chip.key == tmp.key) {
                chip.value += tmp.value  * (TurnoverRateT * AC);
                dpOutChip[j] = chip;
                iFind = 1;
                break;
            }
        }
//        }
        if (iFind == 0) {
            Dict newItem = (Dict){ tmp.key, tmp.value  * (TurnoverRateT * AC) };
//            dpOutChip[*npChip] = (Dict){tmp.key, tmp.value *(TurnoverRateT * AC)};
//            dpOutChip[*npChip] = tmp;
            dpOutChip[*npChip] = newItem;
            (*npChip) += 1;
        }
    }
    free(tmpChip);

    Dict *dpOutChip2 = (Dict *) malloc(((*npChip) + 1) * sizeof(Dict));
    for(int i = 0; i < *npChip; i++) {
        Dict tmp = dpOutChip[i];
        dpOutChip2[i] = (Dict){tmp.key, tmp.value};
    }
//    memcpy(dpOutChip, dpOutChip2, sizeof(Dict) * *npChip);
    DictNode dictNode = {*npChip, dpOutChip2};
    dpOutChipList[nCount] = dictNode;
}

void calcuChip(Dict *dpOutChip, DictNode *dpOutChipList, int nCount, float *pfHigh, float *pfLow, float *pfVol, float *pfAmount, float capital, float minD) {
    if (minD < 0) {
        minD = 0.01;
    }
    int npChip = 0;
    int flag = 1;
    int AC = 1;
//    int iChip = 0, iChipList = 0;
    for (int i = 0; i < nCount; i++) {
        float avgT = pfAmount[i] / pfVol[i];
        float TurnoverRateT = pfVol[i] / capital;
        calcuSin(&npChip, dpOutChip, dpOutChipList, i, pfHigh[i], pfLow[i], avgT, pfVol[i], TurnoverRateT, minD, AC);
//        calcuJUN(fpOutChip, fpOutChipList, i, pfHigh[i], pfLow[i], pfVol[i], TurnoverRateT, minD, AC);
    }
}

void winner(int nCount, float *pfOut, float *pfClose, float *pfVol, float *pfAmount, DictNode *dpOutChipList) {
//    float *Profit;
//    int count = 0;

    for(int i = 0; i < nCount; i++) {
        float bili = 0;
        float close = pfClose[i] * 100;
        DictNode item = dpOutChipList[i];

//        for (int j = 0; j < nChipList) {
//        for i in self.ChipList:
//            # 计算目前的比例

//            Chip = self.ChipList[i]
            float total = 0;
            float be = 0.0;
            for(int j = 0; j < item.num; j++) {
//            for i in Chip:
                Dict dict = item.pDictList[j];
                total += dict.value;
                if (dict.key < close) {
                    be += dict.value;
                }
            }
            if (total != 0) {
                bili = be / total;
            } else {
                bili = 0;
            }
//            count += 1;
            pfOut[i] = bili;
        }
    }


void cost_list(int nCount, float *pfOut, float *pfHigh, float *pfLow, float *pfVol, float *pfAmount, float *pfClose, float price, float minD, float capital) {
//    Dict *dpOutChip;
//    DictNode *dpOutChipList;
//    int iChip = 0, iChipList = 0;
////    calcuChip()
//    calcuChip(&iChip, dpOutChip, &iChipList, dpOutChipList, nCount, pfHigh, pfLow, pfVol, pfAmount, capital, minD);
//
//    winner(nCount, pfClose, dpOutChipList);
}

void winner_list(int nCount, float *pfOut, float *pfHigh, float *pfLow, float *pfVol, float *pfAmount, float *pfClose, float minD, float capital) {
    Dict *dpOutChip = (Dict *) malloc(100000 * sizeof(Dict));
    DictNode *dpOutChipList = (DictNode *) malloc(nCount * sizeof(DictNode));

    calcuChip(dpOutChip, dpOutChipList, nCount, pfHigh, pfLow, pfVol, pfAmount, capital, minD);
    winner(nCount, pfOut, pfClose, pfVol, pfAmount, dpOutChipList);

    free(dpOutChip);
    for(int i = 0; i < nCount; i++) {
        free(dpOutChipList[i].pDictList);
    }
    free(dpOutChipList);
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

void cost(int nCount, float *pfOut, float *pfHigh, float *pfLow, float *pfVol, float *pfAmount, float *pfClose, float price, float capital) {
//    cost_list(nCount, pfOut, pfHigh, pfLow, pfVol, pfAmount, pfClose, price, minD, capital);
}

void winner(int nCount, float *pfOut, float *pfHigh, float *pfLow, float *pfVol, float *pfAmount, float *pfClose, float capital) {
    float minD = 0.01;
//    printf("hello, %f", capital);
    winner_list(nCount, pfOut, pfHigh, pfLow, pfVol, pfAmount, pfClose, minD, capital);
}
