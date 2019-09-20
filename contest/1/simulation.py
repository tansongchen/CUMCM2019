import sys
sys.path.append('..')
from data.lib import *

# 数值模拟控制参数
dt = 0.01 # 步长
period_number_list = {
    10: [0.294 + i * 0.001 for i in range(10)], 
    20: [0.289 + i * 0.001 for i in range(10)], 
    50: [0.289 + i * 0.001 for i in range(10)], 
    100: [0.287 + i * 0.001 for i in range(5)], 
    200: [0.287 + i * 0.001 for i in range(5)], 
    500: [0.286 + i * 0.001 for i in range(4)], 
    1000: [0.286 + i * 0.001 for i in range(3)]
    }
# period_number_list = [20 * i for i in range(1, 6)] # 周期数列表
# period_number_list = [1] # 周期数
period_steps = int(tau_0 / dt) # 每个周期中的演化步数

# 系统参数
rho_1 = calc_rho(P_1) # 油泵中油的压力
rho_2 = rho_std # 油管中油的压力
tau_A_close = 10 # A 的关闭时间
tau_A_open_list = [0.280 + i * 0.001 for i in range(20)] # A 的开启时间
# tau_A_open_list = [0.288 + i * 0.001 for i in range(1)] # A 的开启时间
t_0 = 0 # B 的初始相位时间

def calc_Q_A(t, P_2, tau_A_open):
    """
    输入：时间 t，油管压力 P_2
    输出：该时间单向阀 A 的流量
    """
    tau_A_period = tau_A_close + tau_A_open
    phase = t % tau_A_period
    if phase < tau_A_open:
        return Q(P_1, P_2, rho_1, S_A)
    else:
        return 0

def calc_Q_B(t):
    """
    输入：时间 t
    输出：该时间喷油嘴 B 的流量
    """
    phase = (t + t_0) % 100
    if phase < 2.4:
        if phase < 0.2:
            return 100 * (phase + dt / 2)
        elif phase < 2.2:
            return 20
        else:
            return 20 - 100 * (phase - 2.2 + dt / 2)
    else:
        return 0

# f = open('P-t.dat', encoding = 'utf-8', mode = 'w')
# f.write('%s\t%s\n' % ('t', 'P'))
f = open('tau-N.dat', encoding = 'utf-8', mode = 'w')
f.write('%s\t%s\n' % ('N', 'tau'))
for period_number, tau_A_open_list in period_number_list.items():
# for period_number in period_number_list:
    count = 0
    total_steps = period_number * period_steps # 总的演化步数
    D_min = 1e8
    best_tau_A_open = 0
    # f = open('D-tauA%d.dat' % period_number, encoding = 'utf-8', mode = 'w')
    # f.write('%s\t%s\n' % ('tauA', 'D'))
    for tau_A_open in tau_A_open_list:
        D = 0
        P_2 = P_2_std
        m_2 = calc_rho(P_2) * V_2
        for i in range(total_steps):
            t = dt * i
            # 演化一步
            # 进油
            Q_A = calc_Q_A(t, P_2, tau_A_open)
            delta_m = Q_A * rho_1 * dt
            m_2 += delta_m
            # 出油
            Q_B = calc_Q_B(t)
            delta_m = Q_B * rho_2 * dt
            m_2 -= delta_m
            # 更新压强
            rho_2 = m_2 / V_2
            P_2 = calc_pres(rho_2)
            # 计算平方误差
            D += (P_2 - P_2_std)**2
            # 该行代码输出 P-t 图
            # if i % 10 == 0: f.write('%f\t%d\n' % (t, int(P_2) - 100000))
        D = math.sqrt(D / total_steps) # 均方误差
        # f.write('%f\t%f\n' % (tau_A_open, D))
        if D < D_min:
            D_min = D
            best_tau_A_open = tau_A_open
        count += 1
        print('完成了 %d 个时长的计算，一共 %d 个时长' % (count, len(tau_A_open_list)))
    # f.close()
    f.write('%d\t%f\n' % (period_number, best_tau_A_open))
f.close()