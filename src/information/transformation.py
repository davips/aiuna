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
<<<<<<< HEAD
<<<<<<< HEAD
            self._uuid = uuid(self.transformer.uuid().encode(), self.operation)
=======
            txt = (self.transformer.uuid()).encode()
            self._uuid = uuid(txt, prefix=self.operation)
>>>>>>> 2f329f9... improved tinyMD5
=======
            self._uuid = uuid(self.transformer.uuid().encode(), self.operation)
>>>>>>> b528667... minor
        return self._uuid
