from identifyable import Identifyable


class Transformation(Identifyable):
    def __init__(self, transformer, operation):
        """
        Immutable application or use of a Transformer.
        :param transformer: Transformer/Pipeline
        :param operation: 'a'pply or 'u'se
        """
        self.transformer = transformer
        self.operation = operation

    def uuid(self):
        """
        Lazily calculated unique identifier for this transformation.
        :return: unique identifier
        """
        if self._uuid is None:
        return self._uuid
