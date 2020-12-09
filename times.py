from Main_project import creat_random_transducer2
from time import time
import matplotlib.pyplot as plt
list_time = []
list_density = []
for i in range(15,100):
    total_time = 0
    density = i/100
    list_density += [i/100]
    print(i)
    for t in range(5000):
        b = creat_random_transducer2(4,density,2,{'a','b'},{'a','b'},want_epsilon_transition=True)
        a = time()
        b.is_sequential()
        total_time += time() - a
    total_time = total_time/50000
    list_time += [total_time]
plt.plot(list_density,list_time)
plt.show()