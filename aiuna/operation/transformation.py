from pjdata.aux.identifyable import Identifyable


class Transformation(Identifyable):
    def __init__(self, transformer, operation):
        """
        Immutable application or use of a Transformer.
        :param transformer: Transformer/Pipeline
        :param operation: 'a'pply or 'u'se
        """
        if operation is None:
            raise Exception(
                'Operation cannot be None! Hint: self._transformation() '
                'should be called only during apply() or use() operations!')
        self.transformer = transformer
        self.operation = operation
        self.name = transformer.name
        self.path = transformer.path
        self.config = transformer.config

    def _uuid_impl(self):
        return self.operation, self.transformer.uuid

    def __str__(self):
        return str(self.transformer) + '->' + self.operation

    __repr__ = __str__


class NoTransformation(type):
    transformer = None
    operation = None
    name = None
    path = None
    config = None
    from pjdata.aux.encoders import int2tiny
    uuid = 'T' + int2tiny(0)

    def __new__(cls, *args, **kwargs):
        raise Exception(
            'NoTransformation is a singleton and shouldn\'t be instantiated')
