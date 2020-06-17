from __future__ import annotations

import typing

from pjdata import types as t
from pjdata.mixin.withserialization import WithSerialization
from pjdata.transformer.transformer import Transformer

if typing.TYPE_CHECKING:
    pass

from pjdata.aux.uuid import UUID


class PHolder(Transformer):  # TODO: Find a better name? Skiper?
    """Placeholder for a component to appear in history but do nothing."""

    def __init__(self, component: WithSerialization):
        self._uuid = UUID.identity
        super().__init__(component)

    def rawtransform(self, content: t.Data) -> t.Result:
        return content

    def _uuid_impl(self):
        return self._uuid
