from lib import *
import math

infile = 'outline.raw'
outfile = 'height.dat'

f = open(infile, encoding = 'utf-8', mode = 'r')
outline_data = [line.strip().split('\t') for line in f]
f.close()

theta_array = [float(line[0]) for line in outline_data]
r_array = [float(line[1]) for line in outline_data]
alpha_array = theta_array
height_array = [max(r * math.sin(alpha + theta) for theta, r in zip(theta_array, r_array)) for alpha in alpha_array]

f = open(outfile, encoding = 'utf-8', mode = 'w')
for alpha, height in zip(alpha_array, height_array):
    f.write(str(alpha) + '\t' + str(height) + '\n')
f.close()