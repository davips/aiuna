from pjdata.step.transformation import Transformation


class Apply(Transformation):
    def __init__(self, transformer):
        """
        Immutable application of a Transformer.
        :param transformer: Transformer/Pipeline
        """
        super().__init__(transformer, 'a')

    def __str__(self):
        return str(
            self.transformer
        ) + '->' + self.step

    __repr__ = __str__
