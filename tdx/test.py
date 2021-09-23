#-*- coding: utf-8 -*-
from numpy import array
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from pandas import read_csv
from pandas import datetime
from pandas import DataFrame
from pandas import concat
from matplotlib import pyplot

series = read_csv(r'000001.csv', header=0, parse_dates=[0], index_col=0, squeeze=True)

'''
将数据转换成有监督数据
训练的目的就是找到训练数据input和output的关系
具体实现就是将整体的时间数据向后滑动n格，和原始数据拼接，就是有监督的数据
'''
# 把data数组构建成监督学习型数据
# lag：步长
def timeseries_to_supervised(data, lag=1):  
    df = DataFrame(data)
    # 原始数据时间窗向后移动lag步长
    colums = [df.shift(i) for i in range( lag + 1,1,-1)]
    # 拼接数据
    colums.append(df.shift(axis=0, periods=1))  
    # 横向拼接重塑数据
    df = concat(colums, axis=1)  
    print(df)
    # 删除nan数据
    df.dropna(inplace=True)  
    return df

X = series.values
supervised = timeseries_to_supervised(X, 4)
print(supervised)
print(supervised.values[:,0:-1])
print(supervised.values[:,-1])

# 定义数据
X = supervised.values[:,0:-1]
X = X.reshape(X.shape[0], X.shape[1], 1)
y = supervised.values[:,-1]

# 定义模型
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(X.shape[1], X.shape[2])))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mae')
print(model.summary())
# 训练模型
model.fit(X, y, epochs=500, verbose=1)

print('学习完成')
# 开始预测
x_input = array([18.11, 17.81, 17.66, 17.18])
x_input = x_input.reshape((1, 4, 1))
yhat = model.predict(x_input, verbose=0)

print('输入:')
print([18.11, 17.81, 17.66, 17.18])
print('预测下一个出现的数字:')
print(yhat[0][0])

# 17.18, 17.37, 17.83, 18.46, 18.85, 18.86
X_t = array([ 
    [18.11, 17.81, 17.66, 17.18], 
    [17.81, 17.66, 17.18, 17.37], 
    [17.66, 17.18, 17.37, 17.83], 
    [17.18, 17.37, 17.83, 18.46], 
    [17.37, 17.83, 18.46, 18.85]])
X_t = X_t.reshape(X_t.shape[0], X_t.shape[1], 1)
y_t = array([17.37, 17.83, 18.46, 18.85, 18.86])
# 存储预测值
y_pre_list = []
# 存储真实值
y_real_list = []
# 存储x轴值
x_axis_list = []
# 记录预测值和真实值
for i in range(0, len(X_t)):
    yhat = model.predict(X_t[i].reshape((1, X_t.shape[1], X_t.shape[2])), verbose=0)
    # 记录预测值和真实值
    y_pre_list.append(yhat[0][0])
    y_real_list.append(y_t[i])
    x_axis_list.append(i)

fig = pyplot.figure()
ax=fig.add_subplot()
# 在一个图表里显示两根折线
pyplot.plot(x_axis_list,y_pre_list,label='y_pre')
pyplot.plot(x_axis_list,y_real_list,label='y_real')
pyplot.grid(axis="x")
ax.legend()
pyplot.title('more+single->single+single')
pyplot.show()