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

    @property  # Collection not hashable! We memoize it by hand here.
    @abstractmethod
    def allfrozen(self):
        pass
