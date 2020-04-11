from abc import ABC
from functools import lru_cache

from pjdata.mixin.identifyable import Identifyable


class AbstractData(Identifyable, ABC):
    @property
    @lru_cache()
    def iscollection(self):
        from pjdata.collection import Collection
        return isinstance(self, Collection)
