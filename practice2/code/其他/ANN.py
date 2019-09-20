import keras
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
import pandas as pd
import random
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

# 数据所在文件夹
root_path = r"C:\Users\cyc\Desktop\2017B"

# 附件1数据
data1 = pd.DataFrame(pd.read_excel(root_path+r'\data1.xls'))

# data1 = data1[data1.任务执行情况==1].reset_index(drop=True)

data1[u'经度'] -= data1[u'经度'].mean()
data1[u'经度'] /= data1[u'经度'].std()
data1[u'纬度'] -= data1[u'纬度'].mean()
data1[u'经度'] /= data1[u'经度'].std()
price = data1[u'任务标价'].std()  # 价格单位
data1[u'任务标价'] -= data1[u'任务标价'].mean()
data1[u'任务标价'] /= data1[u'任务标价'].std()

# Train中1表示训练集，0表示测试集
train_ratio = 0.5000  # 训练集比例
data1['Train'] = pd.DataFrame([int(random.random()<train_ratio) for x in range(0, len(data1))])

train = data1[data1.Train==1].reset_index(drop=True)
test = data1[data1.Train==0].reset_index(drop=True)

# train = train[train.任务执行情况==0].reset_index(drop=True)
# test = test[test.任务执行情况==1].reset_index(drop=True)

# 创建神经网络模型
model = Sequential()    # 顺序模型
keras.layers.Dropout(0.5, noise_shape=None, seed=None)

# 三层网络
model.add(Dense(units=1000, activation='relu', input_dim=2))
model.add(Dense(units=30, activation='relu'))
model.add(Dense(units=30, activation='relu'))
model.add(Dense(units=1, activation='linear'))

model.compile(loss='mse',
              optimizer=keras.optimizers.Adam())

# 训练
X = train[[u'经度', u'纬度']]
Y = train[u'任务标价']
model.fit(X, Y, epochs=2000, batch_size=100)

# 比较
X_test = test[[u'经度', u'纬度']]
predict = pd.DataFrame(model.predict(X_test))
print(predict.describe())
test['predict'] = predict
print(test[u'任务标价'].corr(test['predict']))

train['predict'] = pd.DataFrame(model.predict(X))
print(train['predict'].describe())
print(train[u'任务标价'].corr(train['predict']))

'''
test['predict'] /= test['predict'].std()
test['delta'] = abs(test[u'任务标价'] - test['predict'])
print(test['delta'].describe())
'''

