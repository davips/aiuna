from pjdata.aux.identifyable import Identifyable


class Transformation(Identifyable):
    def __init__(self, transformer, step):
        """
        Immutable application or use of a Transformer.
        :param transformer: Transformer/Pipeline
        :param step: 'a'pply or 'u'se
        """
        if step is None:
            raise Exception(
                'Operation cannot be None! Hint: self._transformation() '
                'should be called only during apply() or use() steps!')
        self.transformer = transformer
        self.step = step
        self.name = transformer.name
        self.path = transformer.path
        self.config = transformer.config

    def _uuid_impl(self):
        return self.step, self.transformer.uuid


class NoTransformation(type):
    transformer = None
    step = None
    name = None
    path = None
    config = None
    from pjdata.aux.encoders import int2tiny
    uuid = 'T' + int2tiny(0)

    def __new__(cls, *args, **kwargs):
        raise Exception(
            'NoTransformation is a singleton and shouldn\'t be instantiated')
