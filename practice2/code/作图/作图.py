import matplotlib.pyplot as pt
import math

f = open('data.txt', encoding = 'utf-8', mode = 'r')
l = [[float(y) for y in x.strip().split('\t')] for x in f]
f.close()
f = open('mem.txt', encoding = 'utf-8', mode = 'r')
ll = [[float(y) for y in x.strip().split('\t')] for x in f]
f.close()

def n2(a, b):
	return (a[0] - b[0])**2 + (a[1] - b[1])**2
def n1(a, b):
	return abs(a[0] - b[0]) + abs(a[1] - b[1])
def price(k):
	return 75 - k * 0.5
def fr(n):
	if n <= 75:
		return (1 - (n - 65) / 10)
	else:
		return 0
def fg(n):
	if n <= 75:
		return (1 - abs(n - 70) / 5)
	else:
		return 0
def fb(n):
	if n <= 75:
		return (1 - (75 - n) / 10)
	else:
		return 0
def fri(n):
	if math.log(n) > 10:
		return 0
	elif math.log(n) < 0:
		return 1
	else:
		return (1 - math.log(n) / 10)
def fgi(n):
	if math.log(n) > 10:
		return 0
	elif math.log(n) < 0:
		return 0
	else:
		return (1 - abs(math.log(n) - 5)/ 5)
def fbi(n):
	if math.log(n) > 10:
		return 0
	elif math.log(n) < 0:
		return 0
	else:
		return (1 - (10 - math.log(n)) / 10)
test = 0
# for i in l:
# 	count = 0
# 	for j in ll:
# 		if n1(j[:2], i[:2]) < 0.05: count = count + 1
# 	p = price(count)
# 	# print(p, i[2], p == i[2])
# 	if abs(p - i[2]) <= 0.5: test = test + 1
# print(test)
# for i in l:
# 	if (i[3] == 0):
# 		pt.scatter([i[0]], [i[1]], color = (fr(i[2]), fg(i[2]), fb(i[2])), s = 20, marker = 'x')
# 	else:
# 		pt.scatter([i[0]], [i[1]], color = (fr(i[2]), fg(i[2]), fb(i[2])), s = 20, marker = 'o')

for i in ll:
	if math.log(i[2]) > 4:
		pt.scatter([i[0]], [i[1]], color = (fri(i[2]),fgi(i[2]),fbi(i[2])), s = 5)
pt.xlim((22.4, 24))
pt.ylim((112.5,114.5))
# pt.xlim((22, 24))
# pt.ylim((112, 116))
pt.show()