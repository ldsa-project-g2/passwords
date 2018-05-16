import re
from collections import Counter

# # # We consider ASCII-128 characters only..

digits = list('0123456789')

alpha = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

special = list(' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')  # <- ASCII 128 common visible symbols

file = ['password124x', '$$pass123rd23%', 'qwerty', 'qwerty1', 'mikeey', 'mikeey1', 'fishyy2', 'fishyy22']

s_counter = Counter()  #  <- this counts the individual strings types, e.g. 'pass' or '123'
t_counter = Counter()  #  <- this counts the structure of the password string e.g. 'L8D3S1' (8-alphas, 3-digits, 1-spec)
for line in file:
    structures = re.findall(r'[0-9]+|[a-zA-Z]+|[' + ''.join(special) + r']+', line)
    base = '-'
    for structure in structures:
        s_counter[structure] += 1
        if structure[0] in alpha:
            # then this is an alpha string structure
            base += 'L' + str(len(structure)) + '-'
        elif structure[0] in digits:
            # then this is a digit structure
            base += 'D' + str(len(structure)) + '-'
        else:
            # the final, least likely outcome is a special structure
            base += 'S' + str(len(structure)) + '-'
    t_counter[base] += 1

print('S Counter: ', s_counter.most_common())
print('T Counter: ', t_counter.most_common())