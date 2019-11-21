from information.encoders import uuid


class Transformation:
    def __init__(self, transformer, operation):
        """
        Immutable application or use of a Transformer.
        :param transformer: Transformer/Pipeline
        :param operation: 'a'pply or 'u'se
        """

        # Add lazy cache for uuid
        self._uuid = None

        self.transformer = transformer
        self.operation = operation

    def uuid(self):
        """
        Lazily calculated unique identifier for this transformation.
        :return: unique identifier
        """
        if self._uuid is None:
            txt = (self.transformer.uuid() + self.operation).encode()
            self._uuid = uuid(txt)
        return self._uuid
