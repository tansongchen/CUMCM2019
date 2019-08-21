import sys
sys.path.append('../数据')
from 函数库 import *
import numpy as np

# 读入数据
task_data = extract_task_data_from('../数据/新任务数据.txt')
mem_data = extract_mem_data_from('../数据/会员数据.txt')
neighbor_map = generate_neighbor_map_for(task_data, mem_data, absolute_neighbor = True)

# 分组并将所有分好的组进行测试
target_d = np.arange(0.002, 0.022, 0.002)
methods = generate_grouping_methods_for(task_data, target_d)

# 保存结果
f = open('新任务分组结果.txt', encoding = 'utf-8', mode = 'w')
for nmethod, method in enumerate(methods):
	d = target_d[nmethod]
	p_data = generate_prices_for(task_data, neighbor_map, '../第 2 题/势能面拟合结果.txt', method = method)
	P = sum(p_data.values())
	f.write(str(round(d, 3)) + '\t' + str(P) + '\n')
f.close()