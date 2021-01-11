import numpy as np
dag =  [('q4', 'q3', 'q0'), ('q2', None), ('q1', 'q5')]
max_len1 = 0
max_len2 = -1
max_len = 0
for i in dag:
    if i[1] == None:
        if max_len1 == 0:
            max_len1 = 1
    elif len(i) == max_len1:
        max_len2 = max_len1
    elif len(i) > max_len1:
        max_len1 = len(i)
        print(max_len1)
    else:
        max_len2 = len(i)
if max_len2 >= 0:
    max_len = np.lcm(max_len1, max_len2)
else:
    max_len = max_len1
