from functools import lru_cache
from math import factorial

from pjdata.aux.linalg import int2pmatrix, transpose, pmatrix2int, pmatmult


class UUID:
    default_side = 35
    lower_limit = 1  # Zero has cyclic inversions, Z*Z=I  Z-¹=Z

    # Lazy starters.
    _n = None  # number
    _id = None  # pretty
    _m = None  # matrix
    _isfirst = None
    _t = None  # inverse (also transpose) pmatrix

    def __init__(self, identifier=None, digits=20, side=default_side):
        self.side = side
        self.digits = digits
        if identifier is None:
            identifier = self.first_matrix

        if isinstance(identifier, list):
            if len(identifier) != side:
                l = len(identifier)
                raise Exception(
                    f'Permutation matrix should be {side}x{side}! Not {l}x{l}'
                )
            self._m = identifier
        elif isinstance(identifier, int):
            if identifier > self.upper_limit or identifier < self.lower_limit:
                raise Exception(
                    f'Number should be in the interval [{self.lower_limit},'
                    f'{self.upper_limit}]!'
                )
            self._n = identifier
        elif isinstance(identifier, str):
            from pjdata.aux.encoders import pretty2int
            if len(identifier) != digits:
                l = len(identifier)
                raise Exception(f'Str id should have {digits} chars! Not {l}!')
            self._id = identifier
            self._n = pretty2int(identifier)
            if self.n > self.upper_limit or self.n < self.lower_limit:
                raise Exception(
                    f'String should represent a number in the interval '
                    f'[{self.lower_limit}, {self.upper_limit}]!'
                )
        elif isinstance(identifier, bytes):
            from pjdata.aux.encoders import md5digest, bytes2int
            self._n = bytes2int(md5digest(identifier))
        else:
            raise Exception('Wrong argument type for UUID:', type(identifier))

    @staticmethod  # Needs to be static to get around making UUID hashable.
    @lru_cache()
    def _lazy_upper_limit(side):
        # Identity matrix has special properties: A*I=A  I-¹=I
        return factorial(side) - 2  # (side! - 1) is identity

    @staticmethod  # Needs to be static to get around making UUID hashable.
    @lru_cache()
    def _lazy_first_matrix(side):
        return int2pmatrix(1, side=side)

    @property
    def upper_limit(self):
        return self._lazy_upper_limit(self.side)

    @property
    def first_matrix(self):
        return self._lazy_first_matrix(self.side)

    @property  # Avoiding lru, due to the need of a "heavy" hashable function.
    def t(self):
        """Transpose, but also inverse matrix."""
        if self._t is None:
            self._t = UUID(transpose(self.m))
        return self._t

    @property  # Cannot be lru, because id may come from init.
    def id(self):
        """Pretty printing version, proper for use in databases also."""
        if self._id is None:
            from pjdata.aux.encoders import int2pretty
            self._id = int2pretty(self.n)
        return self._id

    @property  # Cannot be lru, because m may come from init.
    def m(self):
        """Id as a permutation matrix (list of numbers)."""
        if self._m is None:
            self._m = int2pmatrix(self.n, self.side)
        return self._m

    @property  # Cannot be lru, because n may come from init.
    def n(self):
        """Id as a natural number."""
        if self._n is None:
            self._n = pmatrix2int(self.m)
        return self._n

    @property  # Cannot be lru, because id may come from init.
    def isfirst(self):
        """Is this the origin of all UUIDs?"""
        if self._isfirst is None:
            self._isfirst = self.m == self.first_matrix
        return self._isfirst

    def __mul__(self, other):
        """Flexible merge/unmerge with another UUID.

         Non commutative: a * b != b * a
         Invertible: (a * b) / b = a
                     a.inv * (a * b) = b
         Associative: (a * b) * c = a * (b * c)
         """
        return UUID(pmatmult(self.m, other.m))

    def __truediv__(self, other):
        """Bounded unmerge from last merged UUID."""
        if self.m == self.first_matrix:
            raise Exception(f'Cannot divide by UUID={self}!')
        return UUID(pmatmult(self.m, other.t.m))

    def __eq__(self, other):
        return self.n == other.n if self._m is None else self.m == other.m

    def __str__(self):
        return self.id

    __repr__ = __str__  # TODO: is this needed?
