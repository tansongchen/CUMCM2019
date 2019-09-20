import sys
sys.path.append('..')
from data.lib import *
# import matplotlib.pyplot as plt

# 运行控制参数
# omega_list = [0.0234 + 0.0001*j for j in range(10)]
omega_list = [0.0238]
dt = 0.01
# period_number = 100
period_number = 10
period_steps = int(tau_0 / dt)
total_steps = period_number * period_steps

# 系统参数
rho_1_std = calc_rho(500)
rho_2 = rho_std
m_1_std = rho_1_std * calc_V_1(min_h)
alpha_0 = 1.5 * pi   # 初始时刻alpha
t_0 = 0     # 初始时刻(决定了B的相位)

def calc_Q_A(P_2, rho_1):
    """
    输入：时间 t，油管压力 P_2, P_1为高压油泵内压强
    输出：该时间单向阀 A 的流量
    """
    P_1 = calc_pres(rho_1)
    if P_1 > P_2:
        return Q(P_1, P_2, rho_1, S_A)
    else:
        return 0

def calc_Q_B(t, P_2):
    """
    输入：时间 t, 油管压强P_2
    输出：该时间喷油嘴 B 的流量
    """
    phase = (t + t_0) % 100
    z = calc_z(phase)
    if z <= 0:
        return 0
    else:
        return solve_Q_B(P_2, z)

# f = open('D-omega.dat', encoding = 'utf-8', mode = 'w')
# f.write('%s\t%s\n' % ('omega', 'D'))
# f = open('P-t.dat', encoding = 'utf-8', mode = 'w')
# f.write('%s\t%s\n' % ('t', 'P'))
# f = open('m1-t.dat', encoding = 'utf-8', mode = 'w')
# f.write('%s\t%s\n' % ('t', 'm1'))
f = open('QA-t.dat', encoding = 'utf-8', mode = 'w')
f.write('%s\t%s\n' % ('t', 'QA'))
count = 0
for omega in omega_list:
    D = 0
    P_2 = P_2_std
    m_2 = calc_rho(P_2) * V_2
    rho_1 = rho_1_std
    m_1 = m_1_std   # 初始时刻油量
    alpha = alpha_0

    for i in range(total_steps):
        if abs(alpha % (2*pi) - 1.5*pi) <= omega * dt: m_1 = m_1_std
        t = i * dt
        V_1 = calc_V_1(calc_height(alpha % (2*pi)))
        rho_1 = m_1/V_1

        # 演化一步
        # 进油
        Q_A = calc_Q_A(P_2, rho_1)
        delta_m = Q_A * rho_1 * dt
        m_2 += delta_m
        m_1 -= delta_m
        # 出油
        Q_B = calc_Q_B(t, P_2)
        delta_m = Q_B * rho_2 * dt
        m_2 -= delta_m
        # 更新密度和压强
        rho_2 = m_2 / V_2
        P_2 = calc_pres(rho_2)
        # 计算平方误差
        D += (P_2 - P_2_std)**2
        # if i % 100 == 0: f.write('%f\t%d\n' % (t, int(P_2 - P_2_std)))
        # if i % 100 == 0: f.write('%f\t%f\n' % (t, m_1))
        if i % 100 == 0: f.write('%f\t%f\n' % (t, Q_A))
        alpha += omega * dt
    D = math.sqrt(D / total_steps)  # 均方误差
    # f.write('%f\t%f\n' % (omega, D))
    count += 1
    print('完成了 %d 个角速度的计算，一共 %d 个角速度' % (count, len(omega_list)))
f.close()