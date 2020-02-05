from pjdata.step.transformation import Transformation


class Apply(Transformation):
    def __init__(self, transformer):
        """
        Immutable application of a Transformer.
        :param transformer: Transformer/Pipeline
        """
        self._uuid = transformer.uuid
        super().__init__(transformer, 'a')

    def _uuid_impl(self):
        return self.step, self._uuid

    def __str__(self):
        return str(
            self.serialized
        ) + '->' + self.step

    __repr__ = __str__
