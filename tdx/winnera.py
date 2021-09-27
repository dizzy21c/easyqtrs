

import pandas as pd
import copy
from easyquant import MongoIo
from easyquant.indicator.base import *
import datetime
class ChipDistribution():

    def __init__(self, data):
        self.Chip = {} # 当前获利盘
        self.ChipList = {}  # 所有的获利盘的
        self.data = data
        self.capital = CAPITAL(self.data)

    def calcuJUN(self,dateT,highT, lowT, volT, TurnoverRateT, A, minD):

        x =[]
        l = (highT - lowT) / minD
        if l == 0:
            lowT = lowT - minD
            l = 1
        for i in range(int(l)):
            x.append(round(lowT + i * minD, 2))
        length = len(x)
        eachV = volT/length
        for i in self.Chip:
            self.Chip[i] = self.Chip[i] *(1 -TurnoverRateT * A)
        for i in x:
            if i in self.Chip:
                self.Chip[i] += eachV *(TurnoverRateT * A)
            else:
                self.Chip[i] = eachV *(TurnoverRateT * A)
        import copy
        self.ChipList[dateT] = copy.deepcopy(self.Chip)



    def calcuSin(self,dateT,highT, lowT,avgT, volT,TurnoverRateT,minD,A):
        x =[]

        l = (highT - lowT) / minD
        if l == 0:
            lowT = lowT - minD
            l = 1
        for i in range(int(l)):
            x.append(round(lowT + i * minD, 2))

        length = len(x)

        #计算仅仅今日的筹码分布
        tmpChip = {}
        eachV = volT/length


        #极限法分割去逼近
        for i in x:
            # print("x i", i)
            x1 = i
            x2 = i + minD
            h = 2 / (highT - lowT)
            s= 0
            if i < avgT:
                y1 = h /(avgT - lowT) * (x1 - lowT)
                y2 = h /(avgT - lowT) * (x2 - lowT)
                s = minD *(y1 + y2) /2
                s = s * volT
            else:
                y1 = h /(highT - avgT) *(highT - x1)
                y2 = h /(highT - avgT) *(highT - x2)

                s = minD *(y1 + y2) /2
                s = s * volT
            tmpChip[i] = s


        for i in self.Chip:
#             print("Chip i", i, self.Chip[i])
            self.Chip[i] = self.Chip[i] *(1 -TurnoverRateT * A)

        for i in tmpChip:
            # print("tempChip i", i)
            if i in self.Chip:
                self.Chip[i] += tmpChip[i] *(TurnoverRateT * A)
            else:
                self.Chip[i] = tmpChip[i] *(TurnoverRateT * A)
        import copy
        self.ChipList[dateT] = copy.deepcopy(self.Chip)


    def calcu(self,dateT,highT, lowT,avgT, volT, TurnoverRateT,minD = 0.01, flag=1 , AC=1):
        if flag ==1:
            self.calcuSin(dateT,highT, lowT,avgT, volT, TurnoverRateT,A=AC, minD=minD)
        elif flag ==2:
            self.calcuJUN(dateT,highT, lowT, volT, TurnoverRateT, A=AC, minD=minD)

    def calcuChip(self, flag=1, AC=1):  #flag 使用哪个计算方式,    AC 衰减系数
        # low = self.data['low']
        # high = self.data['high']
        # vol = self.data['volume']
        # # TurnoverRate = self.data['TurnoverRate']
        # TurnoverRate = vol / CATITAL * 100
        # # avg = self.data['avg']
        # avg = self.data['amount'] / self.data['volume']
        # date = self.data['date']

        # for i in range(len(date)):
        for idx in self.data.index:
            item = data.loc[idx]

        #     if i < 90:
        #         continue

            highT = item.high
            lowT = item.low
            volT = item.volume
            TurnoverRateT = item.volume / self.capital * 100 #TurnoverRate[i]
            avgT = item.amount / item.volume
            # print(date[i])
            dateT = idx[0].strftime("%Y-%m-%d")
            self.calcu(dateT,highT, lowT,avgT, volT, TurnoverRateT/100, flag=flag, AC=AC)  # 东方财富的小数位要注意，兄弟萌。我不除100懵逼了

        # 计算winner
    def winner(self,p=None):
            self.calcuChip(flag=1, AC=1)
            Profit = []
            date = self.data.index.levels[0]

            if p == None:  # 不输入默认close
                p = self.data['close']
                count = 0
                for i in self.ChipList:
                    # 计算目前的比例

                    Chip = self.ChipList[i]
                    total = 0
                    be = 0
                    for i in Chip:
                        total += Chip[i]
                        if i < p[count]:
                            be += Chip[i]
                    if total != 0:
                        bili = be / total
                    else:
                        bili = 0
                    count += 1
                    Profit.append(bili)
            else:
                for i in self.ChipList:
                    # 计算目前的比例

                    Chip = self.ChipList[i]
                    total = 0
                    be = 0
                    for i in Chip:
                        total += Chip[i]
                        if i < p:
                            be += Chip[i]
                    if total != 0:
                        bili = be / total
                    else:
                        bili = 0
                    Profit.append(bili)

#             import matplotlib.pyplot as plt
#             plt.plot(date[len(date) - 200:-1], Profit[len(date) - 200:-1])
#             plt.show()
            return Profit

    def lwinner(self,N = 5, p=None):
        self.calcuChip(flag=1, AC=1)

        data = copy.deepcopy(self.data)
        date = data.index.levels[0]
        ans = []
        for i in range(date.size):
            # print(date[i])
            if i < N:
                ans.append(None)
                continue
            tempData = data.iloc[i-N:i,]
            # self.data.index= range(0,N)
            self.__init__(tempData)
            # self.calcuChip()    #使用默认计算方式
            a = self.winner(p)
            ans.append(a[-1])
        # import matplotlib.pyplot as plt
        # plt.plot(date[len(date) - 60:-1], ans[len(date) - 60:-1])
        # plt.show()
        # print("lw-data", data)
        # print("lw", ans)
        self.data = data
        return ans



    def cost(self,N):
        # date = self.data['date']
        self.calcuChip(flag=1, AC=1)
        N = N / 100  # 转换成百分比
        ans = []
        for i in self.ChipList:  # 我的ChipList本身就是有顺序的
            Chip = self.ChipList[i]
            ChipKey = sorted(Chip.keys())  # 排序
            total = 0  # 当前比例
            sumOf = 0  # 所有筹码的总和
            for j in Chip:
                sumOf += Chip[j]

            for j in ChipKey:
                tmp = Chip[j]
                tmp = tmp / sumOf
                total += tmp
                if total > N:
                    ans.append(j)
                    break
        # import matplotlib.pyplot as plt
        # plt.plot(date[len(date) - 1000:-1], ans[len(date) - 1000:-1])
        # plt.show()
        return ans



if __name__ == "__main__":
    m=MongoIo()
    data=m.get_stock_day("000859")
    a=ChipDistribution(data)
    # a.get_data(data) #获取数据
    # a.calcuChip(flag=1, AC=1) #计算
    start_t = datetime.datetime.now()
    data['win'] = a.winner() #获利盘
    end_t = datetime.datetime.now()
    print(end_t, 'tdx_func_mp spent:{}'.format((end_t - start_t)))

#     data['cos'] = a.cost(70) #成本分布
#     data['lwin'] = a.lwinner()
    print(data.tail(20))
