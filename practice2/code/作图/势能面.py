import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager
import math
import copy
myfont = matplotlib.font_manager.FontProperties(fname='/System/Library/Fonts/PingFang.ttc')

# 两点间的距离
def dist(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

f = open('../第 2 题/势能面拟合结果.txt', encoding = 'utf-8', mode = 'r')
# 温度 T｜耗散系数 k｜展开系数 b_m
lines = f.readlines()
_, T = lines[0].strip().split()
T = float(T)
_, k = lines[1].strip().split()
k = float(k)
b = []
for m, line in enumerate(lines[2:]):
    x_m, y_m, b_m = line.strip().split()
    b.append((float(x_m), float(y_m), float(b_m)))
f.close()
def f(x,y):
	f = 0
	for item in b:
		y_m, x_m, b_m = item
		f = f + b_m * math.exp(- dist((x_m, y_m), (x, y))**2 / (2 * 0.05**2))
	return f

x_list = np.arange(112.40, 114.61, 0.01)
y_list = np.arange(22.40, 23.61, 0.01)
points = [[f(x,y) for x in x_list] for y in y_list]

plt.pcolor(x_list, y_list, points, cmap = 'YlOrRd')
plt.xlabel('经度', FontProperties = myfont)
plt.ylabel('纬度', FontProperties = myfont)
plt.colorbar()
plt.show()