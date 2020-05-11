from dataclasses import dataclass
from functools import lru_cache
from math import factorial


def int2pmat(number, side=35):
    """Convert number into permutation matrix.

    Pads to side. If None, no padding.

    Parameters
    ----------
    number
    side

    Returns
    -------

    """
    available = list(range(side))
    mat = []
    for i in range(side, 0, -1):
        number, r = divmod(number, i)
        mat.append(available.pop(r))
    mat.extend(available)
    return mat


def pmat2int(matrix):
    """Convert permutation matrix to number.

    Parameters
    ----------
    matrix

    Returns
    -------

    """
    radix = len(matrix)
    available = list(range(radix))
    i = 1
    res = 0
    for row in matrix:
        idx = available.index(row)
        del available[idx]
        res += idx * i
        i *= radix
        radix -= 1
    return res


def pmat_mult(a, b):
    """Multiply two permutation matrices (of the same size?).

    Parameters
    ----------
    a
        list of positive integers plus zero
    b
        list of positive integers plus zero

    Returns
    -------

    """
    return [b[-row - 1] for row in a]


def pmat_transpose(m):
    """Transpose a permutation matrix (square?).

     https://codereview.stackexchange.com/questions/241511/how-to-efficiently-fast-calculate-the-transpose-of-a-permutation-matrix-in-p/241524?noredirect=1#comment473994_241524

    Parameters
    ----------
    m
        list of positive integers plus zero

    Returns
    -------
        list of positive integers plus zero
    """
    n = len(m)
    tr_ls = [0] * n

    for l in m:
        tr_ls[n - 1 - m[l]] = n - 1 - l

    return tr_ls


# Useful, but not really used functions. ====================================


@lru_cache()
def fact(n):
    """Cached factorial to speed up repetitive calls."""
    return factorial(n)


def print_binmatrix(m):
    """Print a binary matrix.

    Parameters
    ----------
    m
        list of positive integers plus zero

    Returns
    -------
        None
    """
    for row in m:
        print(' '.join(format(2 ** row, f'0{len(m)}b')), row)


def int2fac(number):
    """Convert decimal into factorial numeric system. Left-most is LSB.

    Parameters
    ----------
    number

    Returns
    -------

    """
    i = 2
    res = [0]
    while number > 0:
        number, r = divmod(number, i)
        res.append(r)
        i += 1
    return res


def fac2pmat(digits):
    """Convert factoradic number to permutation matrix.

    Parameters
    ----------
    digits

    Returns
    -------

    """
    available = list(range(len(digits)))
    mat = []
    for digit in reversed(digits):
        mat.append(available.pop(digit))
    return mat


def pmat2fac(matrix):
    """Convert permutation matrix to factoradic number.

    Parameters
    ----------
    matrix

    Returns
    -------

    """
    available = list(range(len(matrix)))
    digits = []
    for row in matrix:
        idx = available.index(row)
        del available[idx]
        digits.append(idx)
    return list(reversed(digits))


def fac2int(digits):
    """Convert factorial numeric system into decimal. Left-most is LSB.

    Parameters
    ----------
    digits

    Returns
    -------

    """
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
        return M(l=pmat_transpose(l))

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
        return M(l=pmat_mult(self.l, other.l))

    def __truediv__(self, other):
        return M(l=pmat_mult(self.l, other.t))

    def __add__(self, other):
        n = pmatrix2int(self.l) + pmatrix2int(other.l)
        return M(n % self.last)
