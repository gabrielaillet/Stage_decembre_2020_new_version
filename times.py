from Main_project import creat_random_transducer2
from time import time
import matplotlib.pyplot as plt
list_time = []
list_density = []
total_time = 0
for i in range(1,8):
    a = time()
    for t in range(100):
        print(t)
        b = creat_random_transducer2(7,0.5,i,{'a','b'},{'a','b'},want_epsilon_transition=True)
        a = time()
        b.is_sequential()
        total_time += time() - a
    total_time = total_time/100
    list_time += [total_time]
    list_density += [i]
plt.plot(list_density,list_time)
plt.show()