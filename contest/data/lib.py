import math

# 全局常数
pi = math.pi
P_0 = 101.325
P_1 = 1.6e5
P_2_std = 1e5
rho_std = 0.850
rho_2_std = 0.850
C = 0.85 / math.sqrt(1000)
d_2 = 10
l_2 = 500
V_2 = l_2 * pi * d_2**2/4
d_A = 1.4
S_A = pi * d_A**2 / 4
V_B = 44
tau_0 = 100
tau_A_close = 10

def get_data_from(path_to_file):
    f = open(path_to_file, encoding = 'utf-8', mode = 'r')
    l = [[float(field) for field in line.strip('\n').split('\t')] for line in f]
    f.close()
    return l

def write_data_to(path_to_file, data):
    f = open(path_to_file, encoding = 'utf-8', mode = 'r')
    for item in data:
        item_s = [str(field) for field in item]
        f.write(''.join(item_s) + '\n')
    f.close()

def Q(P_high, P_low, rho_high, A):
    return C * A * math.sqrt(2 * (P_high - P_low) / rho_high)

def interpolation(x, x_array, y_array, equally_spaced = False):
    """
    目的：找到自变量 x 所在分段函数的区间
    输入：
    - x：待求值的自变量；
    - x_array：已知数据点中自变量的升序系列
    - y_array：分别对应于 x_array 中每一个点的因变量值
    - length：0 表示 ref 中 x 不是等间隔系列，其他数值表示以 length 为等间隔；
    输出：数组 (x_1, x_2, y_1, y_2)，其中 x_1 <= x < x_2
    """

    if x < x_array[0] or x >= x_array[-1]: raise Exception('过小或过大的自变量数值（在 get_interval 中')

    imin = 0
    imax = len(x_array) - 1
    if equally_spaced:
        space = x_array[1] - x_array[0]
        i = int((x - x_array[0]) / space)
        return y_array[i] + (y_array[i+1] - y_array[i]) * (x - x_array[i]) / space
    else:
        while imax - imin > 1:
            temp = int((imax + imin)/2)
            if x_array[temp] <= x:
                imin = temp
            else:
                imax = temp
        return y_array[imin] + (y_array[imax] - y_array[imin]) * (x - x_array[imin]) / (x_array[imax] - x_array[imin])

# 密度
density_data = get_data_from('../data/density.dat')
rho_array = tuple(item[0] for item in density_data)
P_array = tuple(item[1] for item in density_data)
rho_min = rho_array[0]
# 高度
height_data = get_data_from('../data/height.dat')
alpha_array = tuple(item[0] for item in height_data)
height_array = tuple(item[1] for item in height_data)
min_h = min(height_array)
max_h = max(height_array)
# 针阀高度
movement_data = get_data_from('../data/movement.raw')
t_array = tuple(item[0] for item in movement_data)
z_array = tuple(item[1] for item in movement_data)

def calc_rho(P):
    return interpolation(P, P_array, rho_array, equally_spaced = True)

def calc_pres(rho):
    if rho < rho_min:
        return 0
    return interpolation(rho, rho_array, P_array, equally_spaced = False)

def calc_height(alpha):
    return interpolation(alpha, alpha_array, height_array, equally_spaced = True)

def calc_z(t):
    return interpolation(t, t_array, z_array, equally_spaced = False)

def calc_V_1(height):
    return 20 + (max_h-height)*pi*25/4
def calc_V_h(height):
    return 20 + (max_h-height)*pi*25/4

def solve_Q_B(P_1, h):
    """
    目标：计算喷油器 B 的流速
    输入：
    - P_1: 高压油管的压强（kPa）, 要求大于大气压 P_0
    - h: 针阀升程（mm）
    输出：流量（mm^3/ms）
    """
    theta = math.pi / 20  # 9°的夹角
    sin_t = math.sin(theta)
    S_B_prime = math.pi * (h * h * sin_t * sin_t * math.cos(theta) + 2.5 * h * sin_t)  # 针阀和圆锥之间等效截面积
    S_B = math.pi * 0.49  # 圆锥底部截面积
    rho_1 = calc_rho(P_1)  # P_1压强下的煤油密度
    # x,y>0 表示 delta_P_1 与 delta_p2, 分别表示在针阀和圆锥底部的压降, 满足 x+y=P_1-P_0
    # p2 为圆锥中间压强, 满足 p2=P_1+delta_P_1
    x = 0
    # 实际待求方程组为：
    # x+y=P_1-P_0
    # return = S_B_prime*math.sqrt(2*x/rho_1) = S_B*math.sqrt(2*(y)/calc_rho(P_1-x))

    x_1 = 0.25 * (P_1 - P_0)  # 利用x_1, x_2用割线法求解 f(x)=0, 这里f(x)是严格单调递增函数
    x_2 = 0.75 * (P_1 - P_0)  # 这里x_1, x_2的初值其实是任意的
    f_1 = S_B_prime * math.sqrt(2 * x_1 / rho_1) - S_B * math.sqrt(2 * (P_1 - P_0 - x_1) / calc_rho(P_1 - x_1))  # 目标为f=0
    max_times = 1000  # 设置一个迭代次数上限
    for j in range(max_times):
        if abs(x_1 - x_2) < 0.00001:  # 设置允差
            x = x_2
            break
        else:
            f_2 = S_B_prime * math.sqrt(2 * x_2 / rho_1) - S_B * math.sqrt(2 * (P_1 - P_0 - x_2) / calc_rho(P_1 - x_2))
            x_1 = x_2 - (x_2 - x_1) * f_2 / (f_2 - f_1)
            # 防止前几次迭代使得x越界
            if x_1 > P_1 - P_0:
                x_1 = P_1 - P_0
            elif x_1 < 0:
                x_1 = 0
            # 交换下标1和2用于下次迭代
            x_1, x_2 = x_2, x_1
            f_1 = f_2
    # 迭代超过上限就报错
    if x == 0: raise Exception("Secant method doesn't converge！(In yuanzhui())")
    return C * S_B_prime * math.sqrt(2 * x / rho_1)

# 测试函数

def test_interpolation():
    x_array = (1, 2, 3, 4)
    y_array = (1, 4, 9, 16)
    x = 2.5
    print(interpolation(x, x_array, y_array, True))

# test_interpolation()