from Main_project import *
from time import time
import matplotlib.pyplot as plt



list_time = []
list_time2 = []
list_time3 = []
list_density = []
number_of_true = []
for i in range(2,100):
    d = i/100
    total_time = 0
    number_of_true_value = 0
    print(i)
    for l in range(50):
        a = time()
        b = creat_random_transducer3(8,d,3,{'a','b'},3,want_epsilon_transition=True)
        if b.is_sequential():
            number_of_true_value += 1
        """
        if m:
            number_of_true_value += 1
        current_time = time() - a
        total_time += current_time
        a = time()
        n = b.is_sequential_weeber_and_klem()
        current_time = time() - a
        total_time2 += current_time
        if m != n:
            print(b.transitions)
            print(b.states)
            print(b.initial_states)
            print(b.final_states)
            assert (1 == 2)
        """
    """
    total_time = total_time/50
    total_time2 = total_time2/50
    total_time3 = total_time3/50
    """
    number_of_true_value = number_of_true_value/50
    number_of_true += [number_of_true_value]
    list_density += [d]
    """
    list_time += [total_time]
    list_time2 += [total_time2]
    list_time3 += [total_time3]
    
    """
plt.plot(list_density,number_of_true,label = 'probability of been sequential')
plt.legend()
plt.show()
"""
plt.legend()
plt.plot(list_density,list_time2,label = 'Weber and Klemm method')
plt.show()
plt.plot(list_density,list_time,label = 'Squaring transducers method')
plt.plot(list_density,list_time2,label = 'Weber and Klemm method')
plt.legend()
plt.show()
"""
