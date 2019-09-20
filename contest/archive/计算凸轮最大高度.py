# coding: utf-8
import pandas as pd
import sys
import numpy as np
import math
data=pd.read_excel('附件1-凸轮边缘曲线.xlsx')
data['最大高度(mm)']=None
for i in range(len(data)):
    alpha=data['极角（rad）'][i]
    len_list=[]
    for j in range(len(data)):
        theta=data['极角（rad）'][j]
        length=data['极径（mm）'][j]*math.sin(alpha+theta)
        len_list.append(length)
    data['最大高度(mm)'][i]=max(len_list)
print(data)
data.to_excel('result.xls')

