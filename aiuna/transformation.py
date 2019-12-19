from pjdata.aux.identifyable import Identifyable


class Transformation(Identifyable):
    def __init__(self, transformer, operation):
        """
        Immutable application or use of a Transformer.
        :param transformer: Transformer/Pipeline
        :param operation: 'a'pply or 'u'se
        """
        self.transformer = transformer
        self.operation = operation
        self.name = transformer.name
        self.path = transformer.path
        self.config = transformer.config

    def _uuid_impl(self):
        return self.transformer.uuid, self.operation

    def __str__(self):
        return str(self.transformer) + '->' + self.operation
