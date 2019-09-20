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


f = open('t-P-1.dat', encoding = 'utf-8', mode = 'w')
f.write('t\tP_2\n')

# 运行控制参数
N_list = [3]
dt = 0.01
period_number = 10

rho_h_std = calc_rho(500)
m_h_std = rho_h_std * calc_V_h(min_h)

count = 0
N_len = len(N_list)
for N in N_list:
    omega = 2*N*pi/50   # rad/ms
    X = []
    Y = []
    temp_Y = []
    tau_temp_Y = 1     # Y的平滑时间

    D = 0
    P_2 = P_2_std
    m_2 = calc_rho(P_2) * V_2
    rho_h = rho_h_std
    period_steps = int(2 * pi / omega / dt)
    total_steps = period_number * period_steps * N  # period_number 个50ms
    m_h = m_h_std   # 初始时刻油量
    alpha_0 = 1.5*pi   # 初始时刻alpha

    t_0 = -2     # 初始时刻(决定了B的相位)

    t = t_0
    alpha = alpha_0

    B_open = False   # True表示此period内存在喷嘴喷油(注意到 period=50/N <= 50ms,并假设在第一个period内B开启)
    After_B = False  # 第一个周期中表示B喷嘴是否(喷过或者正在喷)

    for i in range(total_steps):

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

        delta_m_D_std = Q(P_2, 500, rho_2, S_A) * rho_2 * dt  # 通过减压阀的流量上限
        # 根据 B_open 判断油管内油量变化
        B_open = (i/period_steps) % N < 1
        if not B_open:
            After_B = False
            if P_2 > P_2_std:   # 自动稳压
                m_2 += delta_m_A - delta_m_D_std
            else:
                m_2 += delta_m_A
        else:   # 该period内有B喷油
            phase_h = (i/period_steps) % N    # [0, 1]之间的数，表示处于一个period的哪个位置
            if After_B == False and Q_B > 16:
                After_B = True

            if phase_h < 0.13:
                if P_2 > P_2_std:  # 自动稳压
                    m_2 += delta_m_A - delta_m_B - delta_m_D_std
                else:
                    m_2 += delta_m_A - delta_m_B
            else:
                if After_B and delta_m_B <= delta_m_A:
                    if P_2 > P_2_std:  # 自动稳压
                        m_2 += delta_m_A - delta_m_B - delta_m_D_std
                    else:
                        m_2 += delta_m_A - delta_m_B
                else:
                    if P_2 > P_2_std + 65:  # 给P_2设定一个上限
                        m_2 += delta_m_A - delta_m_B - delta_m_D_std
                    else:
                        m_2 += delta_m_A - delta_m_B

        # 更新密度和压强
        rho_2 = m_2 / V_2
        P_2 = calc_pres(rho_2)
        # 计算平方误差
        D += (P_2 - P_2_std)**2
        # f.write(str(t) + '\t' + str(int(P_2)) + '\n')

        if i%10==0:
            temp_Y.append(P_2)  # 在这里添加想要观察的物理量作为Y轴
            if (i/10)%tau_temp_Y == 0:
                X.append(i / 100)
                Y_new = sum(temp_Y)/len(temp_Y)
                Y.append(Y_new)
                temp_Y = []

        alpha += omega*dt
        if i%10==0:
            f.write('%f\t%f\n' % (i / 100, P_2-P_2_std))
    D = D / total_steps  # 均方误差



    count += 1
    print('Accomplished(%d/%d)' % (count, N_len))

    plt.plot(X,Y)
    plt.show()
f.close()