import math


# 2-范数
def n2(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


class SystemState:
    def __init__(self):
        """
            （略）
            （此处还应该包含之前模型所有系统参数，以及他们从文件中读取的初始化过程）

        """

        # norm_prob 代表给定的成功率
        self.norm_prob = 0.50

        # r 为全体任务点的坐标的列表，r[i]为第i个任务的坐标[x_i,y_i]
        self.r = [[1, 1], [2, 1], [1, 3]]   # 这些数据只是方便debug
        self.task_num = len(self.r)     # 任务点个数，会多次用到

        # group 记录任务的分组情况，g[i]为整数，表示第i个任务处于分组g[i]
        self.group = [i for i in range(self.task_num)]     # 初始时所有任务各自分组不同

        # distance 记录任务点i和j两两距离(i<j) 元素为{i,j,n2(r[i], r[j])}，元素个数n(n-1)/2
        self.distance = [{'i': i, 'j': j, 'n2': n2(self.r[i], self.r[j])}\
                         for i in range(self.task_num) for j in range(self.task_num) if i < j]
        # distance 按照n2升序排列
        self.distance = sorted(self.distance, key=lambda x: x['n2'])

    # prob即qi，为第i个任务被完成的概率。参数p为该任务的定价
    def prob(self, i, p):
        """

            此处缺少计算过程，目前的return只是用来debug


        """
        return min(i/5/self.task_num+(p/100)**2, 1)


# price通过给定成功概率反解出任务i的定价，考虑到概率是p的单调函数并且不能求导，使用割线法
def price(ss, i):
    p1 = 65.0
    p2 = 70.0
    f1 = ss.prob(i, p1)-ss.norm_prob     # 目标为f=0

    max_times = 1000   # 设置一个迭代次数上限
    for j in range(max_times):
        if abs(p1-p2) < 0.00001:
            return p2
        else:
            f2 = ss.prob(i, p2)-ss.norm_prob
            p1 = p2 - (p2-p1)*f2/(f2-f1)

            # 交换下标1和2用于下次迭代
            p1, p2 = p2, p1
            f1 = f2
    #   迭代超过上限就报错
    raise Exception("Secant method doesn't converge！")


# 总价格
def total_price(ss):
    p = 0.0
    for i in range(ss.task_num):
        p += price(ss, i)
    return p


# find_solution结果保存在ss的分组方式group中
def find_solution(ss):
    # 按升序尝试连接，每次连接距离最近的两个任务
    p = total_price(ss)
    d = 0.0
    for connect in ss.distance:
        i = connect['i']
        j = connect['j']

        gi = ss.group[i]
        gj = ss.group[j]

        # 跳过已合并的任务
        if gi == gj:
            continue

        # 重新分组
        for k in range(len(ss.group)):
            if ss.group[k] == gj:
                ss.group[k] = gi
        p_temp = total_price(ss)

        # 新连接没有改善p
        if p_temp > p:
            #  没有任何连接就报错
            if d == 0:
                raise Exception("No task is packaged!")
            else:
                print(u"任务打包的参数d结果为:"+str(d))

                # 还原正确的group (为了算p_temp多修改了一步group)
                ss.group = [x for x in range(ss.task_num)]
                for connect2 in ss.distance:
                    if connect2['n2'] > d:
                        break

                    i2 = connect['i']
                    j2 = connect['j']

                    gi2 = ss.group[i2]
                    gj2 = ss.group[j2]

                    if gi2 == gj2:
                        continue
                    for k2 in range(len(ss.group)):
                        if ss.group[k2] == gj2:
                            ss.group[k2] = gi2

                return
        p = p_temp
        d = connect['n2']

    # 只剩一个任务就报错
    raise Exception("There remains only one task！")


SS = SystemState()
print(total_price(SS))
find_solution(SS)
print(SS.group)

