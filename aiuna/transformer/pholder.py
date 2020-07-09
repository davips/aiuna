from __future__ import annotations

from typing import TYPE_CHECKING

import pjdata.mixin.serialization as ser
if TYPE_CHECKING:
    import pjdata.types as t
import pjdata.aux.uuid as u
import pjdata.transformer.transformer as tr


class PHolder(tr.Transformer):  # TODO: Find a better name? Skiper?
    # TODO: lembrar por que o PHolder é necessário
    """Placeholder for a component to appear in history but do nothing."""
    ispholder = True

    def __init__(self, component: t.Union[str, ser.WithSerialization]):
        self._uuid = u.UUID.identity
        super().__init__(component)

    def rawtransform(self, content: t.Data) -> t.Result:
        return {}

    def _uuid_impl(self):
        return self._uuid
