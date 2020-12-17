from Main_project import *
from time import time
import matplotlib.pyplot as plt



for t in range(4,8):
    list_time = []
    list_density = []
    total_time = 0
    for i in range(15,85):
        TF = 0
        d = i/100
        print(i)
        for l in range(100):
            b = creat_random_transducer3(t,d,3,{'a','b'},3,want_epsilon_transition=True)
            if b.is_sequential():
                TF += 1

        total_time = TF/100
        list_time += [total_time]
        list_density += [d]

    plt.plot(list_density,list_time,label = t)
plt.legend()
plt.show()

"""
TT = 0
TF = 0
count_error = 0
first_webber = []
second_T1 = []
density = []
truc1 = 0
truc2 = 0
for d in range(10,100):
    print(d)
    c = d/100
    density += [c]
    for i in range(100):
        transduce = creat_random_transducer2(5,0.3,1,{'c'},{'aa','b'},want_epsilon_transition=False)
        transduce.trim()
        a = square_transducer_product(transduce,transduce)
        d = from_transducer_to_multiple_initial_nfa(a)
        o = transduce.is_sequential()
        w = states_set_of_co_accessible_nfa(a,a.initial_states)
        q = sub_automaton(d,w)
        a.compare_nfa_and_transducer(q)
        p = find_marked_states_for_dag(q)
        b = create_dag_of_strongly_connected_component(q,p)
        g = b.states
        l = time()
        n = T1_criteria(a,g)
        truc1 += time()-l
        l = time()
        x = T1_criteria_bis(a,g)
        truc2 += time() - l
        if n!= x:
            print('allo?')
    first_webber += [truc1/100]
    second_T1 += [truc2/100]




plt.plot(density,first_webber,label='first')
plt.plot(density,second_T1,label ='second')
plt.legend()
plt.show()
"""
