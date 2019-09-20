# coding=utf-8
import math

pi = math.pi
P_std = 1e5
rho_std = 0.850
C = 0.85
P_1 = 1.6e5
d_A = 1.4

def A(d, inner_d = 0):
    return pi * (d**2 - inner_d**2) / 4

def Q(P_high, P_low, rho_high, A):
    return C * A * math.sqrt(2 * (P_high - P_low) / rho_high)


def search_pole(x, ref, id=0, method=0):
    """
    找到x所在区间
    :param x:自变量
    :param ref:(x,y)或(y,x)数组的元组,升序排列！
    :param id:0表示x在ref第一个元素，id=1表示x是ref第二个元素
    :param method:0表示非等间隔，1表示等间隔(x是等间隔递增序列)
    :return:数组(x1,x2,y1,y2)。无论id=0或1,x1x2物理量与x相同,x1<=x<x2
    """
    ix = 0
    iy = 1
    if id == 1:
        ix = 1
        iy = 0

    imin = 0
    imax = len(ref) - 1
    if x < ref[imin][ix] or x >= ref[imax][ix]:
        raise Exception("The parameter x is out of range of ref!(In search_pole())")

    if method == 0:
        while imax - imin > 1:
            temp = int((imax + imin)/2)
            if ref[temp][ix] <= x:
                imin = temp
            else:
                imax = temp
        return ref[imin][ix], ref[imax][ix], ref[imin][iy], ref[imax][iy]

    else:
        delta = ref[1][ix]-ref[0][ix]
        i = int((x-ref[0][ix])/delta)
        return ref[i][ix], ref[i+1][ix], ref[i][iy], ref[i+1][iy]


def linear_in(x, ref, id=0, method=0):
    """线性插值"""
    section = search_pole(x, ref, id, method)
    delta = section[1]-section[0]

    return section[2] + ((section[3]-section[2])/delta)*(x-section[0])

def calc_rho(p):
    return 0.85

def yuanzhui(p1, h):
    """
    计算喷嘴的流量
    :param p1: 高压油管的压强(kpa), 要求大于大气压p0
    :param h: 针阀升程(mm)
    :return: 流量(mm^3/ms)
    """
    theta = math.pi/20  # 9°的夹角
    sin_t = math.sin(theta)

    A1 = math.pi*(h*h*sin_t*sin_t*math.cos(theta)+2.5*h*sin_t)  #针阀和圆锥之间等效截面积
    A2 = math.pi*0.49   # 圆锥底部截面积

    C = 0.85/math.sqrt(1000)     # 流量系数
    p0 = 101.25      # 大气压(kpa)
    rho1 = calc_rho(p1)     # p1压强下的煤油密度

    # x,y>0 表示 delta_p1 与 delta_p2, 分别表示在针阀和圆锥底部的压降, 满足 x+y=p1-p0
    # p2 为圆锥中间压强, 满足 p2=p1+delta_p1
    x = 0

    # 实际待求方程组为：
    # x+y=p1-p0
    # return = A1*math.sqrt(2*x/rho1) = A2*math.sqrt(2*(y)/calc_rho(p1-x))

    x1 = 0.25*(p1-p0)    # 利用x1, x2用割线法求解 f(x)=0, 这里f(x)是严格单调递增函数
    x2 = 0.75*(p1-p0)    # 这里x1, x2的初值其实是任意的
    f1 = A1*math.sqrt(2*x1/rho1) - A2*math.sqrt(2*(p1-p0-x1)/calc_rho(p1-x1))     # 目标为f=0

    max_times = 1000  # 设置一个迭代次数上限
    for j in range(max_times):
        if abs(x1 - x2) < 0.00001:  # 设置允差
            x = x2
            break
        else:
            f2 = A1*math.sqrt(2*x2/rho1) - A2*math.sqrt(2*(p1-p0-x2)/calc_rho(p1-x2))
            x1 = x2 - (x2 - x1) * f2 / (f2 - f1)

            # 防止前几次迭代使得x越界
            if x1 > p1-p0:
                x1 = p1-p0
            elif x1 < 0:
                x1 = 0

            # 交换下标1和2用于下次迭代
            x1, x2 = x2, x1
            f1 = f2
    # 迭代超过上限就报错
    if x == 0:
        raise Exception("Secant method doesn't converge！(In yuanzhui())")

    return C*A1*math.sqrt(2*x/rho1)


ref = ((1, 1), (2, 4), (3, 9), (4, 16))
x=3.9
print(yuanzhui(100000, 0.5))