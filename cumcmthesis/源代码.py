import matplotlib.pyplot as p
# 中文注释也是可以的
f = open('1.dat', encoding = 'utf-8', mode = 'r')
l = [line.strip('\r\n').split('\t') for line in f]
f.close()

t = range(len(l))
q1 = [float(x[0]) for x in l]
p1 = [float(x[1]) for x in l]
e1 = [float(x[2]) for x in l]
q2 = [float(x[3]) for x in l]
p2 = [float(x[4]) for x in l]
e2 = [float(x[5]) for x in l]

# p.scatter(q1, p1, s=1, color = 'blue', label = 'Runge Kutta')
p.scatter(q2, p2, s=0.1)
# p.scatter(q2, p2, s=1, color = 'red', label = 'Leap Frog')
p.xlabel('q')
p.ylabel('p')
p.xlim((-1.5, 1.5))
p.ylim((-1.5, 1.5))
p.legend()
p.show()