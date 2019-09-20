from lib import *
import math

infile = 'elasticity.raw'
outfile = 'density.dat'

f = open(infile, encoding = 'utf-8', mode = 'r')
elasticity_data = [line.strip().split('\t') for line in f]
f.close()

P_array = [float(line[0]) for line in elasticity_data]
E_array = [float(line[1]) for line in elasticity_data]
rho_array = [0 for i in range(len(P_array))]
rho_array[200] = rho_std

# 计算积分
for i in range(200, 400):
    old_rho_log = math.log(rho_array[i])
    integral = (1/E_array[i] + 1/E_array[i+1])/2*0.5
    new_rho_log = old_rho_log + integral
    rho_array[i+1] = math.exp(new_rho_log)

for i in range(200, 0, -1):
    old_rho_log = math.log(rho_array[i])
    integral = (1/E_array[i] + 1/E_array[i-1])/2*0.5
    new_rho_log = old_rho_log - integral
    rho_array[i-1] = math.exp(new_rho_log)

f = open(outfile, encoding = 'utf-8', mode = 'w')

for i in range(401):
    f.write(str(rho_array[i]) + '\t' + str(P_array[i]*1000) + '\n')
f.close()