import sys
sys.path.append('..')
from data.lib import *

dt = 0.01
relax_period_number_dict = {
    # 对于每一个给定的弛豫时间，要尝试的那些开启时间，现在只是猜想
    20: [0.905 + i * 0.001 for i in range(31)],
    50: [0.745 + i * 0.001 for i in range(31)],
    100: [0.735 + i * 0.001 for i in range(31)]
    }
stable_period_number = 100
period_steps = int(tau_0 / dt)
stable_steps = stable_period_number * period_steps

# 系统参数
rho_1 = calc_rho(P_1)
rho_2 = rho_std
P_2_std_new = 1.5e5
tau_A_close = 10
tau_A_open_stable = 0.752
A_initial_phase = 0

def calc_Q_A(t, P_2, tau_A_open):
    """
    输入：时间 t，油管压力 P_2
    输出：该时间单向阀 A 的流量
    """
    tau_A_period = tau_A_close + tau_A_open
    phase = (t + A_initial_phase) % tau_A_period
    if phase < tau_A_open:
        return Q(P_1, P_2, rho_1, S_A)
    else:
        return 0

def calc_Q_B(t):
    """
    输入：时间 t
    输出：该时间喷油嘴 B 的流量
    """
    phase = t % 100
    if phase < 2.4:
        if phase < 0.2:
            return 100 * (phase + dt / 2)
        elif phase < 2.2:
            return 20
        else:
            return 20 - 100 * (phase - 2.2 + dt / 2)
    else:
        return 0

for relax_period_number, tau_A_open_list in relax_period_number_dict.items():
    f = open('adjustment_in_%d.dat' % (relax_period_number * tau_0), encoding = 'utf-8', mode = 'w')
    f.write('%s\t%s\n' % ('tauA', 'D'))
    relax_steps = relax_period_number * period_steps
    count = 0
    for tau_A_open in tau_A_open_list:
        D = 0
        P_2 = P_2_std
        m_2 = calc_rho(P_2) * V_2
        for i in range(-relax_steps, stable_steps):
            t = dt * i
            if (t < 0):
                Q_A = calc_Q_A(t, P_2, tau_A_open)
            else:
                Q_A = calc_Q_A(t, P_2, tau_A_open_stable)
            # 进油
            delta_m = Q_A * rho_1 * dt
            m_2 += delta_m
            Q_B = calc_Q_B(t)
            # 出油
            delta_m = Q_B * rho_2 * dt
            m_2 -= delta_m
            rho_2 = m_2 / V_2
            P_2 = calc_pres(rho_2)
            if (t > 0): D += (P_2 - P_2_std_new)**2
            # if (i == 0): print(tau_A_open, P_2)
        D = math.sqrt(D / stable_steps)
        f.write('%f\t%f\n' % (tau_A_open, D))
        count += 1
        print('完成了 %d 个时长的计算，一共 %d 个时长' % (count, len(tau_A_open_list)))
    f.close()
