from __future__ import annotations

import json
from abc import ABC, abstractmethod
from functools import lru_cache

import pjdata.mixin.serialization as ser
from typing import TYPE_CHECKING

from pjdata.aux.util import Property
if TYPE_CHECKING:
    import pjdata.types as t
    import pjdata.transformer.pholder as ph
from pjdata.aux.serialization import serialize, deserialize
from pjdata.aux.uuid import UUID
from pjdata.mixin.printing import withPrinting


class Transformer(ser.withSerialization, withPrinting, ABC):
    ispholder = False

    def __init__(self, component: t.Union[str, ser.withSerialization]):
        """Base class for all transformers.

        ps. Assumes all components are symmetric. This class uses the same component details for both enhance and model.
        I.e. the transformation, if any, is always the same, no matter at which step (enhancing/predicting) we are."""
        if isinstance(component, str):
            # If this transformer is created by other transformer, we can take advantage of a previous serialization.
            # This only works for PHolder because of its simpler uuid calculation!
            dic = json.loads(component)
            self._name = dic["name"]
            self.path = dic["path"]
            self.config = dic["config"]
            self.serialized_component = component
            enhance, model = dic["enhance"], dic["model"]
        else:
            self._name = component.name
            self.path = component.path
            self.config = component.config  # TODO: put config/has* in WithSerialization? create a new mixin?
            self.serialized_component = component.serialized
            enhance, model = component.hasenhancer, component.hasmodel

        # WARNING: serialization of Transformer cannot be reverted! It is just a bunch of shortcuts to component.
        self._jsonable = {
            # 'cfuuid': component.cfuuid,
            # 'component_uuid': component.uuid,
            "name": self.name,
            "longname": self.longname,
            "path": self.path,
            "config": self.config,
            "enhance": enhance,
            "model": model,
            # 'transformer': self.__class__.__name__,  # See 'ps' in docs.
            "uuid": self.uuid,
        }

    @Property
    @lru_cache()
    def component(self):
        return deserialize(self.serialized_component)

    @Property
    @lru_cache()
    def longname(self):
        return self.__class__.__name__ + f"[{self.name}]"

    @Property
    @lru_cache()
    def pholder(self) -> ph.PHolder:
        from pjdata.transformer.pholder import PHolder

        return PHolder(self.component)

    @classmethod
    def materialize(cls, serialized):
        jsonable = json.loads(serialized)

        class FakeComponent(ser.withSerialization):
            path = jsonable["path"]
            serialized = jsonable["component"]

            def _name_impl(self):
                return jsonable["name"]

            def _uuid_impl(self):
                return UUID(jsonable["component_uuid"])

            def _cfuuid_impl(self, data=None):
                return jsonable

        component = FakeComponent()
        return cls(component)

    def transform(self, content: t.DataOrTup, exit_on_error=True) -> t.DataOrTup:
        if isinstance(content, tuple):
            return tuple((dt.transformedby(self) for dt in content))
        # Todo: We should add exception handling here because self.func can raise errors
        # print(' transform... by', self.name)
        return content.transformedby(self)

    @abstractmethod
    def _transform_impl(self, data: t.Data) -> t.Result:
        pass

    def _jsonable_impl(self):
        return self._jsonable

    def _name_impl(self):
        return self._name

    def _cfuuid_impl(self, data=None):
        raise Exception("Non sense access!")
