from ..data.lib import *
from simanneal import Annealer
import math
import random

# 读入数据
task_data = extract_task_data_from('../数据/任务数据.txt', with_price_and_finished = True)
mem_data = extract_mem_data_from('../数据/会员数据.txt')
neighbor_map = generate_neighbor_map_for(task_data, mem_data)

# 给定初始参数
init_state = {
    'a0': -1.0,
    'a1': -1.0,
    'a2': -1.0,
    'b0': 2.0,
    'b1': 40,
    'b2': 700,
}

# 构造一个退火类
class PricingFitting(Annealer):

    def __init__(self, state):
        super(PricingFitting, self).__init__(state)
  
    def energy(self):
        """
        输出：计算能量，即总的估计误差
        """
        a0 = self.state['a0']
        a1 = self.state['a1']
        a2 = self.state['a2']
        b0 = self.state['b0']
        b1 = self.state['b1']
        b2 = self.state['b2']
        error = 0
        for task in task_data:
            p_i_hat = p_0
            i, _, p_i, _ = task
            if p_i not in [80, 85]:
                neighbor_data = neighbor_map[i]
                for neighbor in neighbor_data:
                    dist_a_i, q_a, _ = neighbor
                    p_i_hat = p_i_hat + (a0 + a1 * q_a + a2 * q_a**2) / (b0 + b1 * dist_a_i + b2 * dist_a_i**2)
                p_i_hat = round(p_i_hat * 2) / 2
                p_i_hat = min(max(p_i_hat, 65), 75)
                error = error + abs(p_i_hat - p_i)
        return error

    def move(self):
        """
        输出：在参数空间进行随机移动
        """
        s = 6 * random.random()
        if s < 1:
            self.state['a0'] = self.state['a0'] + ran(0.1)
        elif s < 2:
            self.state['a1'] = self.state['a1'] + ran(0.1)
        elif s < 3:
            self.state['a2'] = self.state['a2'] + ran(0.1)
        elif s < 4:
            self.state['b0'] = self.state['b0'] + ran(0.1)
        elif s < 5:
            self.state['b1'] = self.state['b1'] + ran(1)
        else:
            self.state['b2'] = self.state['b2'] + ran(10)

if __name__ == '__main__':
    PF = PricingFitting(init_state)
    PF.copy_strategy = "method"
    # 大改算法之后，要先用 .auto 方法生成一组温度，然后保存用固定参数演化
    # auto_schedule = PF.auto(minutes = 10)
    auto_schedule = {'tmax': 720, 'tmin': 0.1, 'steps': 100000, 'updates': 100}
    PF.set_schedule(auto_schedule)
    print(auto_schedule)
    state, error = PF.anneal()

    f = open('定价规律拟合结果.txt', encoding = 'utf-8', mode = 'w')
    for key, value in state.items():
        f.write(str(key) + '\t' + str(round(value, 1)) + '\n')
    f.close()