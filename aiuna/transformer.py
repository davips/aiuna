from __future__ import annotations

import json
from functools import lru_cache
from typing import Union, Callable, Optional, overload, Any

import pjdata.types as t
from pjdata.aux.serialization import serialize, deserialize
from pjdata.aux.util import Property
from pjdata.aux.uuid import UUID
from pjdata.mixin.identifiable import Identifiable
from pjdata.mixin.printable import Printable


class Transformer(Identifiable, Printable):  # TODO: it should have some features from old Transformation class

    def __init__(
            self,
            component: Any,  # TODO: <-- use duck typing to import things from pjml into pjdata?
            func: Optional[t.Transformation],  # problema
            info: Optional[Union[
                dict,
                Callable[[], dict],
                Callable[[t.Data], dict]  # TODO: improve this?
            ]]
    ):
        self._uuid = component.cfg_uuid
        self.name, self.path = component.name, component.path
        self.component_uuid = component.uuid
        self._serialized_component = component.serialized
        self._jsonable = {
            'uuid': self.uuid,
            'name': self.name,
            'path': self.path,
            'component_uuid': component.uuid,
            'component': self._serialized_component
        }

        self.func = func if func else lambda data: data
        if callable(info):
            self.info = info
        elif isinstance(info, dict):
            self.info = lambda: info
        elif info is None:
            self.info = lambda: {}
        else:
            raise TypeError('Unexpected info type. You should use, callable, dict or None. Not', type(info))

    @Property
    @lru_cache()
    def serialized(self):
        return serialize(self)

    @Property
    @lru_cache()
    def config(self):
        return deserialize(self._serialized_component)

    @staticmethod
    def materialize(serialized):
        jsonable = json.loads(serialized)

        class FakeComponent:
            name = jsonable['name']
            path = jsonable['path']
            uuid = UUID(jsonable['component_uuid'])
            serialized = jsonable['component']

        component = FakeComponent()
        return Transformer(component, ) #TODO: how to materialize func?

    @overload
    def transform(self, content: t.DataOrTup) -> t.DataOrTup:
        ...

    @overload
    def transform(self, content: t.CollOrTup) -> t.CollOrTup:
        ...

    def transform(self, content: t.DataOrCollOrTup) -> t.DataOrCollOrTup:  # TODO: overload
        if isinstance(content, tuple):
            return tuple((dt.transformedby(self) for dt in content))
        # Todo: We should add exception handling here because self.func can
        #  raise an error
        return content.transformedby(self)

    def _uuid_impl(self):
        return self._uuid

    @Property
    def jsonable(self):
        return self._jsonable
