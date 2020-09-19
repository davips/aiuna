from abc import ABC, abstractmethod
from functools import lru_cache, cached_property

from transf.serialization import serialize
from aiuna.mixin.identification import withIdentification


class WithSerialization(withIdentification, ABC):
    path = None

    @cached_property
    def cfuuid(self):
        """UUID excluding 'model' and 'enhance' flags. Identifies the *transformer*."""
        return self._cfuuid_impl()

    @cached_property
    def serialized(self):
        # print('TODO: aproveitar processamento do cfserialized()!')  # <-- TODO
        return serialize(self)

    @abstractmethod
    def _cfuuid_impl(self):
        pass
