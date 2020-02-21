from pjdata.mixin.printable import Printable
from pjdata.step.transformation import Transformation


class Apply(Transformation, Printable):
    def __init__(self, transformer):
        """
        Immutable application of a Transformer.
        :param transformer: Transformer/Pipeline
        """
        self.transformer_uuid = transformer.uuid
        # TODO: extrair transformation de dentro de conteiners NoOp
        Transformation.__init__(self, transformer, 'a')
        Printable.__init__(self, [transformer, 'a'])

    def _uuid_impl(self):
        return self.step, self.transformer_uuid
