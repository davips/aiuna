from __future__ import annotations

import typing
from abc import ABC, abstractmethod
from functools import lru_cache

if typing.TYPE_CHECKING:
    pass

from pjdata.aux.serialization import serialize
from pjdata.aux.util import Property
from pjdata.mixin.identification import WithIdentification


class WithSerialization(WithIdentification, ABC):
    path = None

    @Property
    @lru_cache()
    def cfuuid(self):
        """UUID excluding 'model' and 'enhance' flags. Identifies the *transformer*."""
        return self._cfuuid_impl()

    @Property
    @lru_cache()
    def serialized(self):
        # print('TODO: aproveitar processamento do cfserialized()!')  # <-- TODO
        return serialize(self)

    @abstractmethod
    def _cfuuid_impl(self):
        pass
