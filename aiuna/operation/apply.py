from pjdata.operation.transformation import Transformation


class Apply(Transformation):
    def __init__(self, transformer):
        """
        Immutable application of a Transformer.
        :param transformer: Transformer/Pipeline
        """
        super().__init__(transformer, 'a')
