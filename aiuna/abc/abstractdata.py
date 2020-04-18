from abc import ABC, abstractmethod
from functools import lru_cache

from pjdata.mixin.identifyable import Identifyable


class AbstractData(Identifyable, ABC):
    isfrozen = False

    @property
    @lru_cache()
    def iscollection(self):
        from pjdata.collection import Collection
        return isinstance(self, Collection)

    # Collection not hashable! That's why we memoize it by hand there.
    @property
    @abstractmethod
    def allfrozen(self):
        pass
