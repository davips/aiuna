import json
from functools import lru_cache

from pjdata.aux.uuid import UUID
from pjdata.aux.serialization import deserialize, serialize
from pjdata.mixin.identifiable import Identifiable
from pjdata.mixin.printable import Printable


class Transformation(Identifiable, Printable):
    def __init__(self, transformer, step):
        if None in [transformer, step]:
            raise Exception(
                'Transformation needs non Nones! Hint: self._transformation() '
                'should be called only during apply() or use() steps!')
        self.name, self.path = transformer.name, transformer.path
        self.transformer_uuid = transformer.uuid
        self._serialized_transformer = transformer.serialized
        self.step = step
        jsonable = {
            'uuid': self.uuid,
            'step': step,
            'name': self.name,
            'path': self.path,
            'transformer_uuid': self.transformer_uuid,
            'transformer': self._serialized_transformer
        }
        super().__init__(jsonable=jsonable)

    @property
    @lru_cache()
    def serialized(self):
        return serialize(self)

    @property
    @lru_cache()
    def config(self):
        return deserialize(self._serialized_transformer)

    @staticmethod
    def materialize(serialized):
        jsonable = json.loads(serialized)
        step = jsonable['step']

        class FakeTransformer:
            name = jsonable['name']
            path = jsonable['path']
            uuid = UUID(jsonable['transformer_uuid'])
            serialized = jsonable['transformer']

        transformer = FakeTransformer()
        return Transformation(transformer, step)

    def _uuid_impl(self):
        from pjdata.aux.uuid import UUID
        # Mark step to differentiate 'apply' from 'use'. And also to avoid
        # having the same uuid as its transformer (for general dump purposes).
        # TODO: customize crypto, allow header for 'a', 'u' and others.
        mark = UUID(self.step.encode())
        return self.transformer_uuid * mark

# class NoTransformation(type):
#     transformer = None
#     step = None
#     name = None
#     path = None
#     config = None
#     from pjdata.aux.encoders import int2pretty
#     uuid = 'T' + int2pretty(0)
#
#     def __new__(cls, *args, **kwargs):
#         raise Exception(
#             'NoTransformation is a singleton and shouldn\'t be instantiated')
#
#     def __bool__(self):
#         return False
