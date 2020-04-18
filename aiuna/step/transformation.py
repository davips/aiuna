from functools import lru_cache

from pjdata.aux.serialization import deserialize
from pjdata.mixin.identifyable import Identifyable
from pjdata.mixin.printable import Printable


class Transformation(Identifyable, Printable):
    def __init__(self, transformer, step):
        """
        Immutable application or use of a Transformer.
        :param transformer: Transformer/Pipeline
        :param step: 'a'pply or 'u'se
        """
        # Precisei retirar referência ao transformer, para que pickle parasse
        # de dar problema ao carregar um objeto Data do PickleServer. Esse
        # problema começar após a unificação ML com CS, sobrescrenvendo
        # __new__ nos containeres. O erro acontecia quando o pickle tentava
        # recriar Containeres do histórico de Data, mas, por algum motivo
        # tentava fazê-lo sem transformers. Serializei config pelo mesmo motivo.
        if step is None:
            raise Exception(
                'Operation cannot be None! Hint: self._transformation() '
                'should be called only during apply() or use() steps!')
        self.name, self.path = transformer.name, transformer.path
        self.transformer_uuid00 = transformer.uuid00
        self._serialized_transformer = transformer.serialized

        # TIP: Step is being added to jsonable by Printable.
        super().__init__(jsonable=self._serialized_transformer)
        self.step = step

    @property
    @lru_cache()
    def config(self):
        return deserialize(self._serialized_transformer)

    def _uuid_impl00(self):
        from pjdata.aux.encoders import uuid00
        # Mark step to differentiate 'apply' from 'use'. And also to avoid
        # having the same uuid as its transformer.
        mark = uuid00(self.step.encode())
        return self.transformer_uuid00 + mark

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
