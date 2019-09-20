# coding=utf-8
import sys
sys.path.append('..')
from data.lib import *
import matplotlib.pyplot as plt


# 系统参数
rho_1 = calc_rho(P_1)
rho_2 = rho_std
A_initial_phase = 5 # （是不是要改成一个 list？）

def calc_Q_A2(P_2, rho_h):
    """
    输入：时间 t，油管压力 P_2, P_h为高压油泵内压强
    输出：该时间单向阀 A 的流量
    """
    P_h = calc_pres(rho_h)
    if P_h > P_2:
        return Q(P_h, P_2, rho_h, S_A)
    else:
        return 0

def calc_Q_B(t, P_2):
    """
    输入：时间 t, 油管压强P_2
    输出：该时间喷油嘴 B 的流量
    """
    phase = t % 50
    z = calc_z(phase)
    if z <= 0:
        return 0
    else:
        return solve_Q_B(P_2, z)


f = open('t-P-2.dat', encoding = 'utf-8', mode = 'w')
f.write('t\tP_2\n')
# 运行控制参数
N_list = [1]
dt = 0.01
period_number = 6

rho_h_std = calc_rho(500)
m_h_std = rho_h_std * calc_V_h(min_h)


omega = 2*pi/50   # rad/ms
X = []
Y = []
temp_Y = []
tau_temp_Y = 1     # Y的平滑时间

D = 0
P_2 = P_2_std
m_2 = calc_rho(P_2) * V_2
rho_h = rho_h_std
period_steps = int(2 * pi / omega / dt)
total_steps = period_number * period_steps  # period_number 个50ms
m_h = m_h_std   # 初始时刻油量
alpha_0 = 1.5*pi   # 初始时刻alpha

t_0 = -10.35     # 初始时刻(决定了B的相位)

t = t_0
alpha = alpha_0

# 记录系统状态
dec_time = 0.0  # 第一个周期中表示第几次降压(减压阀或者喷嘴)

D_lock = False  # True 时D锁定, 不能开启, 每次锁定10ms
D_lock_time_std = 10.0  # 每次锁定的时间
D_remain_time = 0.0     # 剩余锁定时间
D_P_upper = 600    # 高于标准P_2这个值时自动进入开启状态
D_open = False      # 记录前一时刻D阀门是否打开

for i in range(total_steps):

    # 更新D_lock状态
    if D_remain_time > 0:
        D_remain_time -= dt
    if D_remain_time <= 0:
        D_lock = False

    if abs(alpha % (2*pi) - 1.5*pi) <= omega*dt:
        m_h = m_h_std
    t += dt
    V_h = calc_V_h(calc_height(alpha % (2*pi)))
    rho_h = m_h/V_h

    # 演化一步
    # 进油流量
    Q_A = calc_Q_A2(P_2, rho_h)
    delta_m_A = Q_A * rho_h * dt

    m_h -= delta_m_A
    # 出油流量
    Q_B = calc_Q_B(t, P_2)
    delta_m_B = Q_B * rho_2 * dt

    if D_lock:  # D锁定
        m_2 += delta_m_A - delta_m_B
        if dec_time == 1.5 and Q_B > 10:# 喷嘴开始喷油
            dec_time = 2

        elif dec_time == 2 and Q_B < 5:# 喷嘴喷油结束
            dec_time = 2.5
    else:   # D可以控制
        delta_m_D_std = Q(P_2, 500, rho_2, S_A) * rho_2 * dt  # 通过减压阀的流量

        phase_h = (i/period_steps) % 1    # [0, 1]之间的数，表示处于一个period的哪个位置
        # 更新After_B状态
        if phase_h < 2/period_steps:    # 初始时刻
            dec_time = 0

        if dec_time == 0:
            if P_2 > P_2_std + D_P_upper:   # 第一次打开减压阀
                dec_time = 1
                D_open = True
                m_2 += delta_m_A - delta_m_B - delta_m_D_std
            else:
                m_2 += delta_m_A - delta_m_B

        elif dec_time == 1:    # 第一次减压阀减压结束
            if P_2 < P_2_std - D_P_upper:   # 减压阀关闭
                dec_time = 1.5
                D_open = False
                D_lock = True
                D_remain_time = D_lock_time_std
                m_2 += delta_m_A - delta_m_B
            else:
                m_2 += delta_m_A - delta_m_B - delta_m_D_std

        elif dec_time == 1.5:
            m_2 += delta_m_A - delta_m_B
            if Q_B > 10:  # 喷嘴开始喷油
                dec_time = 2

        elif dec_time == 2:
            m_2 += delta_m_A - delta_m_B
            if Q_B < 5:  # 喷嘴喷油结束
                dec_time = 2.5

        elif dec_time == 2.5:
            if P_2 > P_2_std + D_P_upper:   # 第二次打开减压阀
                dec_time = 3
                D_open = True
                m_2 += delta_m_A - delta_m_B - delta_m_D_std
            else:
                m_2 += delta_m_A - delta_m_B

        elif dec_time == 3 and D_open:
            if P_2 < P_2_std - 0.973*D_P_upper:   # 减压阀关闭
                dec_time = 3.5
                D_open = False
                D_lock = True
                D_remain_time = D_lock_time_std
                m_2 += delta_m_A - delta_m_B
            else:
                m_2 += delta_m_A - delta_m_B - delta_m_D_std
        else:   # 第二次减压阀减压结束
            # 自动稳压
            if P_2 > P_2_std:
                D_open = True
                m_2 += delta_m_A - delta_m_B - delta_m_D_std
            else:   #压强小于等于标准值
                if D_open:
                    D_open = False
                    D_lock = True
                    D_remain_time = D_lock_time_std
                    m_2 += delta_m_A - delta_m_B
                else:
                    m_2 += delta_m_A - delta_m_B

    # 更新密度和压强
    rho_2 = m_2 / V_2
    P_2 = calc_pres(rho_2)
    # 计算平方误差
    D += (P_2 - P_2_std)**2
    # f.write(str(t) + '\t' + str(int(P_2)) + '\n')

    temp_Y.append(P_2)  # 在这里添加想要观察的物理量作为Y轴
    if i % tau_temp_Y == 0:
        X.append(i / 100)
        Y_new = sum(temp_Y)/len(temp_Y)
        Y.append(Y_new)
        temp_Y = []

    alpha += omega*dt
    if i % 10 == 0:
        f.write('%f\t%f\n' % (i / 100, P_2-P_2_std))
D = D / total_steps  # 均方误差

print('Accomplished')

plt.plot(X, Y)
plt.show()

f.close()
