from functools import lru_cache
from math import factorial

from pjdata.aux.linalg import int2pmatrix, transpose, pmatrix2int, pmatmult


class UUID:
    first_matrix = int2pmatrix(1)
    _n = None  # number
    _id = None  # pretty
    _m = None  # matrix
    _isfirst = None
    _inv = None
    lower_limit = 1  # Zero has ciclic inversions
    upper_limit = factorial(35) - 2  # To avoid recalculating every init.

    def __init__(self, identifier=first_matrix,
                 digits=20, side=35, nolimits=False):
        if side != 35:
            self.upper_limit = factorial(side) - 2  # (side! - 1) is identity
        if nolimits:
            # "Zero" matrix has special properties:   Z*Z=I  Z-¹=Z
            self.lower_limit = 0
            # Identity matrix has special properties: A*I=A  I-¹=I
            self.upper_limit = factorial(side) - 1
        self.side = side
        self.digits = digits
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
        elif isinstance(identifier, bytes):
            from pjdata.aux.encoders import md5digest, bytes2int
            self._n = bytes2int(md5digest(identifier))
        else:
            raise Exception('Wrong argument type for UUID:', type(identifier))

    @property  # Avoiding lru, due to the need of a "heavy" hashable function.
    def inv(self):
        """Pretty printing version, proper for use in databases also."""
        if self._inv is None:
            self._inv = UUID(transpose(self.m))
        return self._inv

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
            self._m = int2pmatrix(self.n)
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
         Invertible: (a * b) * b.inv = a
                     a.inv * (a * b) = b
         Associative: (a * b) * c = a * (b * c)
         """
        return UUID(pmatmult(self.m, other.m))

    def __add__(self, other):
        """Alias meaning a bounded merge with another UUID.

         Non commutative: a + b != b + a
         Invertible: (a + b) - b = a
         Associative: (a + b) + c = a + (b + c)
         """
        return UUID(pmatmult(self.m, other.m))

    def __sub__(self, other):
        """Bounded unmerge from last merged UUID."""
        if self.m == self.first_matrix:
            raise Exception(f'Cannot subtract from UUID={self}!')
        return UUID(pmatmult(self.m, other.inv.m))

    def __eq__(self, other):
        return self.n == other.n if self._m is None else self.m == other.m

    def __str__(self):
        return self.id

    __repr__ = __str__  # TODO: is this needed?
