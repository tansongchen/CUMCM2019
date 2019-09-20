import sys
sys.path.append('..')
from data.lib import *
import matplotlib.pyplot as plt

l = get_data_from('P-t.dat')

x = [i[0] for i in l]
y = [i[1] for i in l]
plt.plot(x, y)
plt.show()