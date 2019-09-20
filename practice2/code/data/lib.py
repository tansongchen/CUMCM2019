import random
import numpy as np
import math
import copy

# 先验参数
r_0 = 0.05
h = 0.05
p_0 = 75
E_0 = 65
z_0 = 0.9

def dist(a, b):
    """
    输入：两个二维矢量（浮点数的元组）
    输出：计算两个矢量之间的距离（浮点数）
    备注：虽然是在球面上，但曲率可以忽略，仍按平面几何处理
    """
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def ran(step):
    """
    输入：退火算法中参数空间的位移步长（浮点数）
    输出：随机选择增加或减少一个步长（浮点数）
    """
    s = random.random()
    return step if s > 0.5 else -step

def extract_task_data_from(task_file, with_price_and_finished = False):
    """
    输入：任务数据输入文件（字符串），以及列表中是否包含价格和完成情况（布尔值）
    输出：整理好的任务数据（列表）
    备注：表中几列分别为：序号 i｜经度 x_i｜纬度 y_i｜定价 p_i｜完成情况 u_i
    """
    f = open(task_file, encoding = 'utf-8', mode = 'r')
    task_data = [line.strip().split('\t') for line in f]
    if with_price_and_finished:
        task_data = [(line[0], (float(line[1]), float(line[2])), float(line[3]), int(line[4])) for line in task_data]
    else:
        task_data = [(line[0], (float(line[1]), float(line[2]))) for line in task_data]
    f.close()
    return task_data

def extract_mem_data_from(mem_file):
    """
    输入：会员数据输入文件（字符串）
    输出：整理好的会员数据（列表）
    备注：表中几列分别为：序号 a｜经度 x_a｜纬度 y_a｜信誉 c_a｜限额 q_a｜开始时间 t_a
    另注：没有用到信誉和开始时间这两个字段
    """
    f = open(mem_file, encoding = 'utf-8', mode = 'r')
    mem_data = [line.strip().split('\t') for line in f]
    mem_data = [(line[0], (float(line[1]), float(line[2])), int(line[4])) for line in mem_data]
    f.close()
    return mem_data

def extract_potential_surface_from(pot_file):
    """
    输入：势能面输入文件（字符串）
    输出：温度 T（浮点数）｜耗散系数 k（浮点数）｜展开系数向量 b（numpy 一维浮点数组）
    """
    f = open(pot_file, encoding = 'utf-8', mode = 'r')
    lines = f.readlines()
    _, T = lines[0].strip().split()
    T = float(T)
    _, k = lines[1].strip().split()
    k = float(k)
    b = np.zeros(len(lines[2:]))
    for m, line in enumerate(lines[2:]):
        _, _, b_m = line.strip().split()
        b[m] = b_m
    f.close()
    return T, k, b

def generate_potential_matrix_for(task_data):
    """
    输入：任务数据（列表）
    输出：势能矩阵（numpy 一维浮点数组）
    备注：各点上的函数值等于势能矩阵乘以展开系数向量
    """
    x_list = np.arange(112.60, 114.60, h)
    y_list = np.arange(22.40, 23.65, h)
    m_list = [(x, y) for x in x_list for y in y_list]
    m_number = tuple(range(len(m_list)))
    potential_matrix = np.empty((len(task_data), len(m_list)))
    for ntask, task in enumerate(task_data):
        i, r_i = task[:2]
        for m, r_m in enumerate(m_list):
            potential_matrix[ntask, m] = math.exp(- dist(r_i, r_m)**2 / (2 * h**2))
    return potential_matrix

def generate_neighbor_map_for(task_data, mem_data, absolute_neighbor = False):
    """
    输入：任务数据（列表）、会员数据（列表）、是否包含近邻用户的序号（布尔值）
    输出：任务的近邻映射（字典）
    """
    q = {}
    n = {}
    q_avg = sum(mem[2] for mem in mem_data)/len(mem_data)

    for mem in mem_data:
        a, r_a, q_a = mem
        q[a] = q_a / q_avg
        n[a] = 0
        for task in task_data:
            i, r_i = task[:2]
            dist_a_i = dist(r_a, r_i)
            if dist_a_i < r_0:
                n[a] += 1

    task_numbers = range(len(task_data))
    neighbor_map = {}
    for ntask, task in enumerate(task_data):
        i, r_i = task[:2]
        neighbor_i = []
        for mem in mem_data:
            a, r_a, q_a = mem
            dist_a_i = dist(r_a, r_i)
            if dist_a_i < r_0:
                if absolute_neighbor:
                    neighbor_i.append((a, dist_a_i, q[a], n[a]))
                else:
                    neighbor_i.append((dist_a_i, q[a], n[a]))
        neighbor_map[i] = tuple(sorted(neighbor_i))

    return neighbor_map

def generate_grouping_methods_for(task_data, target_d):
    """
    输入：任务数据（列表）、最大打包距离的集合（列表）
    输出：打包方案（列表）
    """
    methods = []
    task_num = len(task_data)
    dist_list = []
    group_map = {task[0]: (0, task[0]) for ntask, task in enumerate(task_data)}

    for task in task_data:
        i, r_i = task
        for task_ in task_data:
            j, r_j = task_
            if i < j:
                dist_list.append(((i, j), dist(r_i, r_j)))

    dist_list = sorted(dist_list, key = lambda x: x[1])

    method_number = 0
    for pair, distance in dist_list:
        if distance > target_d[method_number]:
            methods.append(copy.deepcopy(group_map))
            method_number += 1
            if method_number == len(target_d):
                break
        i, j = pair
        g_i = group_map[i]
        g_j = group_map[j]

        # 跳过已合并的任务
        if g_i == g_j:
            continue

        # 重新分组
        for k in group_map:
            if group_map[k] == g_i or group_map[k] == g_j:
                group_map[k] = tuple([g_i[0] + g_j[0] + distance] + sorted(g_i[1:] + g_j[1:]))
    return methods

def generate_prices_for(task_data, neighbor_map, pot_file, method = None):
    """
    输入：任务数据（列表）、近邻映射（字典）、势能面文件（字符串）、任务是否打包（字典）
    输出：各个任务的定价（列表）
    """
    T, k, b = extract_potential_surface_from(pot_file)
    potential_matrix = generate_potential_matrix_for(task_data)
    E_p = np.dot(potential_matrix, b)
    E_p = {task[0]: E_p[ntask] for ntask, task in enumerate(task_data)}

    def Prob(i, p_i):
        """
        输入：任务序号 i 或一组任务序号 i = (j_1, j_2, ...)，价格 p_i；
        输出：定价 p_i 时任务或任务组 i 被完成的概率。
        """
        z_i = 1
        if type(i) == type(''):
            for neighbor in neighbor_map[i]:
                dist_a_i, q_a, n_a = neighbor
                E_a_i = E_0 + E_p[i] + k * dist_a_i - p_i
                z_i = z_i * (1 - min(1, math.exp(- E_a_i / T) * q_a / n_a))
            return 1 - z_i
        else:
            inner_distance = i[0]
            size = len(i) - 1
            neighbor_for_all = {}
            for j in i[1:]:
                for neighbor in neighbor_map[j]:
                    a, dist_a_j, q_a, n_a = neighbor
                    if a in neighbor_for_all:
                        neighbor_for_all[a][0].append(dist_a_j)
                    else:
                        neighbor_for_all[a] = ([dist_a_j], q_a, n_a)
            for a, value in neighbor_for_all.items():
                dists, q_a, n_a = value
                if len(dists) == size:
                    E_a_i = size * E_0 + sum(E_p[j] for j in i[1:]) + min(dists) + inner_distance - p_i
                    try:
                        z_i = z_i * (1 - min(1, math.exp(- E_a_i / T) * q_a / n_a))
                    except OverflowError:
                        z_i = 0
            return 1 - z_i

    def Price(i):
        """
        输入：任务序号 i 或一组任务序号 i = (j_1, j_2, ...)
        输出：任务序号 i 的定价 p_i
        备注：给定成功概率，概率是 p_i 的单调函数并且难以求导，故用二分法解出（割线法有时不收敛）
        """
        p_left = 0.0 # 价格下限
        p_right = 120.0 * len(i) # 价格上限，部分任务取该值时仍不足以完成是因为没有近邻，所以必须设上限

        while p_right - p_left > 0.1:
            p_middle = (p_left + p_right) / 2
            f_middle = Prob(i, p_middle) - z_0
            if f_middle > 0:
                p_right = p_middle
            else:
                p_left = p_middle
        return round(p_right * 2) / 2

    p_data = {}
    if method:
        groups = set(method.values())
        for i in groups:
            p_i_ast = Price(i)
            p_data[i] = p_i_ast
    else:
        for task in task_data:
            i, r_i = task[:2]
            p_i_ast = Price(i)
            p_data[i] = p_i_ast
    return p_data