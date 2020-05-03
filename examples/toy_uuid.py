from random import random
from timeit import timeit

from pjdata.aux.linalg import int2pmatrix, print_binmatrix, pmatrix2int, \
    int2fac, pmatmult
from pjdata.aux.uuid import UUID

# Show output of operations.
a = UUID(int2pmatrix(2 ** 128 - 1))
b = UUID('12345678901234567890')
c = UUID(1)
print(a, b, c)
print()
print((a * b))
print((a * b) * b)
print((a * b) * b.t)
print((a * b) * c)

fac = int2fac(2 ** 128 + 3214134)

# Check for collisions.
s = set()
r = set()
aa = bb = 0
for i in range(100000):
    while aa in r:
        aa = round(random() * 2 ** 128)
    while bb in r:
        bb = round(random() * 2 ** 128)
    r.add(aa)
    r.add(bb)
    a = int2pmatrix(aa)
    b = int2pmatrix(bb)
    n = pmatrix2int(pmatmult(a, b))
    s.add(n)
    if i > len(s) - 1:
        print(i, a, b, n)
        print('Colision detected!!!!!!!!!!!!!!')
        break
if i == 100000:
    print_binmatrix('OK!')


# Check general overhead of all uuid ops.
def f():
    a = UUID(int2pmatrix(2 ** 128 - 1))
    b = UUID('12345678901234567890')
    (a * b) * b.t


print(timeit(f, number=10000) * 100, 'us')
