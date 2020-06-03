from typing import Union, Tuple, Any

from pjdata.collection import Collection
from pjdata.data import Data
from pjdata.specialdata import NoData

TDatasTuple = Union[Tuple[NoData, ...], Tuple[Data, ...],
                    Tuple[Collection, ...],
                    NoData, Data, Collection]

TDatas = Union[NoData, Data, Collection]


def flatten(lst):
    return [item for sublist in lst for item in sublist]


class Property(object):
    """Substitute for the @property decorator due mypy conflicts"""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)
