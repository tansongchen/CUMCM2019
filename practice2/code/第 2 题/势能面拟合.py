import sys 
sys.path.append('../数据')
from 函数库 import *
from simanneal import Annealer
import math
import random
import numpy as np

# 读入数据
task_data = extract_task_data_from('../数据/任务数据.txt', with_price_and_finished = True)
mem_data = extract_mem_data_from('../数据/会员数据.txt')
neighbor_map = generate_neighbor_map_for(task_data, mem_data)
potential_matrix = generate_potential_matrix_for(task_data)

# 给定初始参数
m_number = potential_matrix.shape[1]
init_state = {
    'T': 0.50,
    'k': 30,
    'b': np.zeros(m_number, dtype = 'float64')
}
b_range = tuple(float(i) for i in range(-20, 21, 1))
m_number_range = range(m_number)

# 构造一个退火类
class PotentialSurfaceFitting(Annealer):

    def __init__(self, state):
        super(PotentialSurfaceFitting, self).__init__(state)

    def energy(self):
        """
        输出：计算能量，即总的预测错误数
        """
        T = self.state['T']
        k = self.state['k']
        E_p = np.dot(potential_matrix, self.state['b'])
        L = 0
        for ntask, task in enumerate(task_data):
            i, r_i, p_i, u_i = task
            z_i = 1
            neighbor_data = neighbor_map[i]
            for neighbor in neighbor_data:
                dist_a_i, q_a, n_a = neighbor
                E_a_i = E_0 + E_p[ntask] + k * dist_a_i - p_i
                z_i = z_i * (1 - min(1, math.exp(- E_a_i / T) * q_a / n_a))
            z_i = 1 - z_i
            if z_i > 0.5 and not u_i: L += 1
            if z_i < 0.5 and u_i: L += 1
        return L

    def move(self):
        """
        输出：在参数空间进行随机移动
        """
        s = 10 * random.random()
        if s < 1:
            self.state['T'] = self.state['T'] + ran(0.01)
        elif s < 2:
            self.state['k'] = self.state['k'] + ran(1)
        else:
            m = random.choice(m_number_range)
            self.state['b'][m] = random.choice(b_range)

if __name__ == '__main__':
    PSF = PotentialSurfaceFitting(init_state)
    PSF.copy_strategy = "method"
    # 大改算法之后，要先用 .auto 方法生成一组温度，然后保存用固定参数演化
    # auto_schedule = PSF.auto(minutes = 60)
    auto_schedule = {'tmax': 100, 'tmin': 0.001, 'steps': 100000, 'updates': 100}
    PSF.set_schedule(auto_schedule)
    print(auto_schedule)
    state, dup = PSF.anneal()
    print(state)

    f = open('势能面拟合结果.txt', encoding = 'utf-8', mode = 'w')
    f.write('T\t' + str(state['T']) + '\n')
    f.write('k\t' + str(state['k']) + '\n')
    for m, b_m in enumerate(state['b']):
        f.write(str(round(m_list[m][0], 2)) + '\t' + str(round(m_list[m][1], 2)) + '\t'+ str(round(b_m)) + '\n')
    f.close()