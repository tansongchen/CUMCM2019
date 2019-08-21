import sys 
sys.path.append('../数据')
from 函数库 import *

# 读入数据
task_data = extract_task_data_from('../数据/任务数据.txt')
mem_data = extract_mem_data_from('../数据/会员数据.txt')
neighbor_map = generate_neighbor_map_for(task_data, mem_data)
p_data = generate_prices_for(task_data, neighbor_map, '势能面拟合结果.txt')

# 保存结果
f = open('定价结果.txt', encoding = 'utf-8', mode = 'w')
f.write('总价格为：%d' % sum(p_data.values()))
for task in task_data:
    i, r_i = task[:2]
    p_i_ast = p_data[i]
    f.write(i + '\t' + str(r_i[0]) + '\t' + str(r_i[1]) + '\t' + str(p_i_ast) + '\n')
f.close()