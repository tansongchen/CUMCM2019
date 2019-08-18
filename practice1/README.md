# CUMCM2019：模拟竞赛 A 题资料夹

# 文件结构

由于是模拟练习，我们尽量模拟真实比赛时使用的有序的文件管理方式。

- `/thesis` 存放论文和所用到的图片；
- `/code` 存放代码；
- `/source` 存放搜集到的资料。

# 分工

$$
p_i=p_0+\sum_{a=1}^{n_i}\frac{g(c_a)}{f(|\vec r_a-\vec r_i|)}
$$

- $i$：任务标号

- $a$：近邻用户标号

- $\vec r$：位置矢量

- $p_0$：基数，固定为 75

- $p_i$：任务 $i$ 的价格

- $c_a$：用户 $a$ 的信誉或任务限额

- $n_i$：$i$ 任务附近半径 $\rho$ 内的用户数

- $f$：位置函数

- $g$：用户函数

将问题转化为一个高维的优化问题：$\rho,f,g$ 的选择。

# 势能面方法

一个任务被完成的概率 $q_i$ 是

$$
q_i=1-\prod_{a=1}^{n_i}(1-\mathrm{min}(1,e^{-\beta E_a(i)}))
$$

其中 $a,n_i$ 意义同前，$\beta$ 是温度倒数，而一个用户完成任务的能量消耗是

$$
E_a(i)=E_0+E_k(|\vec r_a-\vec r_i|)+E_p(\vec r_i)-p_i
$$

- $E_0$：任务的基础能量消耗，可以解释为出家门

- $E_k$：动能，用户移动到位置需要的能量，理论上是标量距离的一次函数（$E_k(x)=kx$）

- $E_p$：势能，是任务位置的向量函数

- $p_i$：价格

现在 $\beta$，$E_0$，$k$ 已经参数化了，$p_i$ 已知，只需要参数化 $E_p$。为此，作展开

$$
E_p(\vec r_i)\approx \sum_{n=1}^N\sum_{m=1}^MA_{nm}\varphi_{nm}(\vec r_i)
$$

记 $\vec r_{nm}=(x_n,y_m)$ 是格点大小为 $h=0.1$ 的经纬格点，然后

$$
\varphi_{nm}(\vec r_i)=\exp\left(\frac{|\vec r_i-\vec r_{nm}|^2}{2h^2}\right)
$$

给定数据集，计算最大似然函数：

$$
\ln L(\beta,E_0,k,\mathbf A)=\sum_{i=1}^{835}\ln \mathrm{if}\left\{\mathbb I(i),q_i,1-q_i\right\}
$$

用共轭梯度法最大化即可。
