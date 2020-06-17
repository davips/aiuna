from __future__ import annotations

from functools import lru_cache
from typing import Callable, TYPE_CHECKING, Union, Dict, Any

from pjdata.mixin.withserialization import WithSerialization
from pjdata.transformer.info import Info
from pjdata.transformer.transformer import Transformer

if TYPE_CHECKING:
    import pjdata.types as t

from pjdata.aux.util import Property


class Enhancer(Transformer):

    def __init__(self, component: WithSerialization, func: t.Transformation,
                 info_func: Callable[[t.Data], Union[Info, Dict[str, Any]]]):
        self._rawtransform = func
        self._info_func = info_func
        self._uuid = component.cfuuid
        super().__init__(component)

    @Property
    @lru_cache()
    def info(self, data: t.Data) -> Info:
        info = self._info_func(data)
        return info if isinstance(info, Info) else Info(items=info)

    def rawtransform(self, content: t.DataOrTup) -> t.DataOrTup:
        return self._rawtransform(content)

    def _uuid_impl(self):
        return self._uuid
