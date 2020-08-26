from __future__ import annotations

from abc import abstractmethod
from functools import lru_cache
from typing import Any, TYPE_CHECKING, Union, Dict

from pjdata.mixin.serialization import withSerialization
from pjdata.transformer.info import Info
from pjdata.transformer.transformer import Transformer


class Model(Transformer):
    def __init__(self, component: withSerialization, data: t.Data):
        # The multiplication order here cannot be otherwise, because it would mean "data output from enhancer".
        # PCA is an example where enhUUID != modUUID; apesar de que ambos deveriam ser modUUID/ mas é impossível,
        # pois enh não conhece o data futuro.
        self._uuid = component.cfuuid(data) * data.uuid
        self.data = data
        super().__init__(component)

    @lru_cache()
    def info(self) -> Info:
        info = self._info_impl(self.data)
        return info if isinstance(info, Info) else Info(items=info)

    @abstractmethod
    def _info_impl(self, train):
        pass

    def _uuid_impl(self):
        return self._uuid


