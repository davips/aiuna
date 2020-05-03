import json
from dataclasses import dataclass, field
from functools import lru_cache
from math import factorial


def pmatmult(a, b):
    """Multiply two permutation matrices (of the same size?).
     a,b: lists of positive integers and zero."""
    return [b[-row - 1] for row in a]


def transpose(m):
    """Transpose a permutation matrix (square?).
     m: list of positive integers and zero.

     https://codereview.stackexchange.com/questions/241511/how-to-efficiently-fast-calculate-the-transpose-of-a-permutation-matrix-in-p/241524?noredirect=1#comment473994_241524
     """
    n = len(m)
    tr_ls = [0] * n

    for l in m:
        tr_ls[n - 1 - m[l]] = n - 1 - l

    return tr_ls


def print_binmatrix(m, side=35):
    """Print a permutation matrix (default: 35x35).
     m: list of positive integers and zero."""

    for row in m:
        print(' '.join(format(2 ** row, f'0{side}b')), row)


def pmatrix2int(m):
    """Convert permutation matrix to number."""
    return fac2int(pmatrix2fac(m))


def int2pmatrix(big_number, side=35):
    """Convert number to permutation matrix.

    Pads to side. If None, no padding."""
    factoradic = int2fac(big_number)
    if side is None:
        return fac2pmatrix(factoradic)
    padded_fac = [x for x in factoradic + [0] * (side - len(factoradic))]
    return fac2pmatrix(padded_fac)


def pmatrix2fac(matrix):
    """Convert permutation matrix to factoradic number."""
    available = list(range(len(matrix)))
    digits = []
    for row in matrix:
        idx = available.index(row)
        del available[idx]
        digits.append(idx)
    return list(reversed(digits))


def fac2pmatrix(digits):
    """Convert factoradic number to permutation matrix."""
    available = list(range(len(digits)))
    mat = []
    for digit in reversed(digits):
        mat.append(available.pop(digit))
    return mat


def int2fac(number):
    """Convert decimal into factorial numeric system. Left-most is LSB."""
    i = 2
    res = [0]
    while number > 0:
        number, r = divmod(number, i)
        res.append(r)
        i += 1
    return res


def fac2int(digits):
    """Convert factorial numeric system into decimal. Left-most is LSB."""
    radix = 1
    i = 1
    res = 0
    for digit in digits[1:]:
        res += digit * i
        radix += 1
        i *= radix
    return res


@dataclass(frozen=False)
class M:
    """A class to ease playing around with permutation matrix operations.

    'l' is the list representation of this matrix."""
    n: int = 0
    l: list = None
    side: int = 35

    def __post_init__(self):
        if self.l is None:
            self.l = int2pmatrix(self.n, self.side)
        elif self.n != 0:
            raise Exception(f'Cannot set both args... n:{self.n} l:{self.l}!')

    @staticmethod
    @lru_cache()
    def _lazy_t(l):
        return M(l=transpose(l))

    @staticmethod
    @lru_cache()
    def _lazy_last(side):
        return factorial(side) - 1

    @property
    def t(self):
        return self._lazy_t(tuple(self.l))

    @property
    def last(self):
        return self._lazy_last(self.side)

    def __mul__(self, other):
        return M(l=pmatmult(self.l, other.l))

    def __truediv__(self, other):
        return M(l=pmatmult(self.l, other.t))

    def __add__(self, other):
        n = pmatrix2int(self.l) + pmatrix2int(other.l)
        return M(n % self.last)
