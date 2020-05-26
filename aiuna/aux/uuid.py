from functools import lru_cache
from math import factorial

from pjdata.aux.alphabets import alphabet800, alphabet800dic
from pjdata.aux.encoders import pretty2pmatrix, pmatrix2pretty, enc, dec
from pjdata.aux.linalg import int2pmat, pmat_transpose, pmat_mult, pmat2int, \
    print_binmatrix


class UUID:
    """Flexible representation of non-standard universal unique identifiers.
    Intended to be an extension and "replacement" of MD5 (or SHA256) hashes.

    This implementation intrinsically cannot comply with RFC 4122,
    ISO/IEC 9834-8:2005, nor any related standards; since it is deterministic,
    no time-dependant, and forms a non-abelian group over multiplication which
    needs fredom to operate on all bits.

    It allows cummulative and reversible combination of UUID objects.
    For a fixed number of 'bits' (132 or 260), a UUID object represents any
    given decimal integer, permutation matrix (see bellow), bytes or strings;
    provided they are within certain bounds related to 'bits'.

    The bit-size options 132 and 260 were defined to accomodate the usual 128
    and 256-bit hashes.
    The increase was necessary due to the mismatch between the amount of
    possible (128/256-bit) numbers and the amount of possible permutation
    matrices (sized 35x35/58x58).

    E.g., for MD5 128-bit hashes, some 35x35 matrices resulting from UUID
    operations will represent a number that exceeds the highest
    number (2^128 - 1), becoming a 133-bit number (log2(35)) in the worst case.
    Therefore, for a fixed-size exchangeable representation, one should choose
    whether to use uuid.n which is at most a 133-bit (or 261-bit) number,
    or uuid.id which is a fixed-size string with 14 (or 27) characters, which
    is intended to be faster and visually shorter at the expense of using more
    bytes.

    Note that, despite the bit-size options (namely 132/260), the real limit
    is somewhere between 132/260 and 133/261. So, it is highly recommended to
    provide only up to 132/260 bits when generating a new UUID object directly
    from binary information (not a common, expected scenario).
    It will be represented by 16/32 bytes anyway (128/256 bits) in the hardware.

        Parameters
        ----------
        identifier
        bits
    """

    # Default values for 128 bits.
    bits = 128
    side = 35
    digits = 14

    alphabet = alphabet800
    alphabetrev = alphabet800dic
    lower_limit = 1  # Zero has cyclic inversions, Z*Z=I  Z-¹=Z

    # Lazy starters.
    _n = None  # number
    _m = None  # matrix
    _id = None  # pretty
    _isfirst = None
    _t = None  # inverse (also transpose) pmatrix

    def __init__(self, identifier=None, bits=128):
        if identifier is None:
            identifier = self.first_matrix

        # Handle internal representation for the provided number of bits.
        if bits == 256:
            self.bits = bits
            self.side = 58
            self.digits = 27
            raise NotImplementedError('256 bits still not implemented.')

        elif bits != 128:
            raise NotImplementedError('Only 128 and 256 bits are implemented.')

        # Handle different types of the provided identifier.
        if isinstance(identifier, list):
            side = len(identifier)
            if side != self.side:
                print_binmatrix(identifier)
                raise Exception(
                    f'Permutation matrix should be {self.side}x{self.side}!'
                    f' Not {side}x{side}'
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
            size = len(identifier)
            if size != self.digits:
                raise Exception(
                    f'Str id should have {self.digits} chars! Not {size}!'
                )
            self._id = identifier
        elif isinstance(identifier, bytes):
            from pjdata.aux.encoders import md5_int
            self._n = md5_int(identifier)
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
        return int2pmat(1, side=side)

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
            self._t = UUID(pmat_transpose(self.m))
        return self._t

    @property  # Cannot be lru, because id may come from init.
    def id(self) -> str:
        """'Pretty' printing version, proper for use in databases also."""
        if self._id is None:
            self._id = enc(self.n, self.alphabet, padding=self.digits)
        return self._id

    @property  # Cannot be lru, because m may come from init.
    def m(self):
        """Id as a permutation matrix (list of numbers)."""
        if self._m is None:
            self._m = int2pmat(self.n, self.side)
        return self._m

    @property  # Cannot be lru, because n may come from init.
    def n(self):
        """Id as a natural number."""
        if self._n is None:
            if self._m:
                self._n = pmat2int(self.m)
            elif self._id:
                self._n = dec(self.id, self.alphabetrev)
            else:
                raise Exception('UUID broken, missing data to calculate n!')
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
        return UUID(pmat_mult(self.m, other.m))

    def __truediv__(self, other):
        """Bounded unmerge from last merged UUID."""
        if self.m == self.first_matrix:
            raise Exception(f'Cannot divide by UUID={self}!')
        return UUID(pmat_mult(self.m, other.t.m))

    def __eq__(self, other):
        return self.n == other.n if self._m is None else self.m == other.m

    def __str__(self):
        return self.id

    __repr__ = __str__  # TODO: is this needed?
