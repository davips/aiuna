from __future__ import annotations

from typing import Union, Callable, Optional, overload

import pjdata.types as t
from pjdata.aux.uuid import UUID
from pjdata.mixin.identifiable import Identifiable
from pjdata.mixin.printable import Printable


class Transformer(Identifiable, Printable):  # TODO: it should have some features from old Transformation class
    def __init__(
            self,
            cfg_uuid: UUID,
            func: Optional[t.Transformation],  # problema
            info: Optional[Union[
                dict,
                Callable[[], dict],
                Callable[[t.Data], dict]  # TODO: improve this?
            ]]
    ):
        super().__init__(jsonable={'some info to print about transformers': None})  # <-- TODO
        self._uuid = cfg_uuid
        self.func = func if func else lambda data: data

        if callable(info):
            self.info = info
        elif isinstance(info, dict):
            self.info = lambda: info
        elif info is None:
            self.info = lambda: {}
        else:
            raise TypeError('Unexpected info type. You should use, callable, '
                            'dict or None.')

    @overload
    def transform(self, content: t.DataOrTup) -> t.DataOrTup:
        ...

    @overload
    def transform(self, content: t.CollOrTup) -> t.CollOrTup:
        ...

    def transform(self, content: t.DataOrCollOrTup) -> t.DataOrCollOrTup:
        if isinstance(content, tuple):
            return tuple((dt.transformedby(self.func) for dt in content))
        # Todo: We should add exception handling here because self.func can
        #  raise an error
        return content.transformedby(self.func)

    def _uuid_impl(self):
        return self._uuid
