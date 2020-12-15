from Main_project import creat_random_transducer2
from time import time
import matplotlib.pyplot as plt


list_time = []
list_density = []
total_time = 0
for i in range(15,100):
    TF = 0
    d = i/100
    print(i)
    for l in range(1000):
        b = creat_random_transducer2(5,d,3,{'a','b'},{'aa','b'},want_epsilon_transition=True)
        if b.is_sequential():
            TF += 1

        total_time = TF/1000
        list_time += [total_time]
        list_density += [d]

plt.plot(list_density,list_time)
plt.show()

