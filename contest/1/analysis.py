import sys
sys.path.append('..')
from data.lib import *

# 油泵压力为 1.6e5 kPa、油管压力为 1e5 kPa 时，理论的开启时长

rho_1 = calc_rho(P_1)
rho_2 = rho_std
Q_A = Q(P_1, P_2_std, rho_1, S_A)
m_decrease = rho_2 * V_B
m_increase = m_decrease
tau_A = m_increase / Q_A / rho_1
tau_A_open = tau_A_close * tau_A / (tau_0 - tau_A)

print('油泵压力为 1.6e5 kPa、油管压力为 1e5 kPa 时，理论的开启时长为：', tau_A_open)

# 油泵压力为 1.6e5 kPa、油管压力为 1e5 kPa 时，理论的开启时长

P_2 = 1.5e5
rho_2 = calc_rho(P_2)
Q_A = Q(P_1, P_2, rho_1, S_A)
m_decrease = rho_2 * V_B
m_increase = m_decrease
tau_A = m_increase / Q_A / rho_1
tau_A_open = tau_A_close * tau_A / (tau_0 - tau_A)

print('油泵压力为 1.6e5 kPa、油管压力为 1e5 kPa 时，理论的开启时长为：', tau_A_open)

# # 经过 2、5、10 秒调整时，理论的开启时长
# relax_periods_list = [20, 50, 100]
# rho_increase = rho_2 - rho_std
# m_increase = rho_increase * V_2
# for relax_periods in relax_periods_list:
#     net_m_increase_per_period = m_increase / relax_periods
#     m_decrease_per_period = rho_2 * V_B
#     m_increase_per_period = net_m_increase_per_period + m_decrease_per_period
#     print(net_m_increase_per_period, m_decrease_per_period)
#     Q_A = Q(P_1, P_2, rho_1, S_A)
#     tau_A = m_increase / Q_A / rho_1
#     tau_A_open = tau_A_close * tau_A / (tau_0 - tau_A)
#     print('在 %d 秒调整中，理论的开启时长为：' % relax_periods, tau_A_open)