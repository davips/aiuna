from functools import lru_cache
from math import factorial

from pjdata.aux.linalg import int2pmatrix, transpose, pmatrix2int, pmatmult


class UUID:
    null_matrix = int2pmatrix(0)
    null_pretty = '00000000000000000000'
    _id = None
    upper_limit = factorial(35) - 1
    lower_limit = 0

    def __init__(self, identifier=null_matrix):
        if isinstance(identifier, list):
            if len(identifier) != 35:
                raise Exception(
                    'Permutation matrix should be 35x35! Not',
                    len(identifier)
                )
            self.matrix = identifier
        elif isinstance(identifier, int):
            if identifier > self.upper_limit or identifier < self.lower_limit:
                raise Exception(
                    f'Number should be in the interval [{self.lower_limit},'
                    f'{self.upper_limit}]!'
                )
            self.matrix = int2pmatrix(identifier)
        elif isinstance(identifier, str):
            if len(identifier) != 20:
                raise Exception(
                    'Pretty str should be 20 chars long! Not', len(identifier)
                )
            self._id = identifier
            from pjdata.aux.encoders import pretty2int
            self.matrix = int2pmatrix(pretty2int(identifier))
        elif isinstance(identifier, bytes):
            from pjdata.aux.encoders import md5digest, bytes2int
            self.matrix = int2pmatrix(bytes2int(md5digest(identifier)))
        else:
            raise Exception('Wrong argument type for UUID:', type(identifier))
        self.isnull = self.matrix == self.null_matrix

    @property  # Cannot be lru, because UUID should be hashable for __eq__ ==.
    def inv(self):
        """Pretty printing version, proper for use in databases also."""
        return UUID(transpose(self.matrix))

    @property  # Cannot be lru, because id may come from init.
    def id(self):
        """Pretty printing version, proper for use in databases also."""
        if self._id is None:
            from pjdata.aux.encoders import int2pretty
            self._id = int2pretty(pmatrix2int(self.matrix))
        return self._id

    def __mul__(self, other):
        """Flexible merge/unmerge with another UUID.

         Non commutative: a * b != b * a
         Invertible: (a * b) * b.inv = a
                     a.inv * (a * b) = b
         Associative: (a * b) * c = a * (b * c)
         """
        return UUID(pmatmult(self.matrix, other.matrix))

    def __add__(self, other):
        """Alias meaning a bounded merge with another UUID.

         Non commutative: a + b != b + a
         Invertible: (a + b) - b = a
         Associative: (a + b) + c = a + (b + c)
         """
        return UUID(pmatmult(self.matrix, other.matrix))

    def __sub__(self, other):
        """Bounded unmerge from last merged UUID."""
        if self.matrix == self.null_matrix:
            raise Exception(f'Cannot subtract from UUID={self.null_pretty}!')
        return UUID(pmatmult(self.matrix, other.inv.matrix))

    def __eq__(self, other):
        return self.matrix == other.matrix

    def __str__(self):
        return self.id

    __repr__ = __str__  # TODO: is this needed?
