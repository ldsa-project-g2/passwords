
import re

# # # We consider ASCII-128 characters and symbols only..
DIGITS = list('0123456789')
ALPHAS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
SPECIALS = list(' !"#$%&\'()*+,-./:;<=>?@[]^_`{|}~\\')
PATTERN = r'[0-9]+|[a-zA-Z]+|[ !"#$%&\'()*+,-./:;<=>?@\[\]\^_`{\|}~\\\\]+'

f = open('test_text.txt', 'r')
for line in f.readlines():
    s = line.split(':')[1]
    print(re.search('\\\\', s))
    structures = re.findall(PATTERN, s)
    print(s, structures)
    t = '123' + ''.join(SPECIALS) + 'xyz'
    print(re.findall(PATTERN, t))

