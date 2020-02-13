from pjdata.mixin.printable import Printable
from pjdata.step.apply import Transformation


class Use(Transformation, Printable):
    def __init__(self, transformer, apply_transformations):
        """
        Immutable use of a Transformer.
        :param transformer: Transformer/Pipeline
        apply_transformations
            apply_transformations thatdata provided to transformer.apply(data)
        """
        if apply_transformations is None:
            self.training_data_uuid = 'DØØØØØØØØØØØØØØØØØØ0'
        else:
            self.training_data_uuid = apply_transformations.uuid
        Printable.__init__(self, [transformer, 'u', self.training_data_uuid])

        self._uuid = transformer.uuid
        super().__init__(transformer, 'u')

    def _uuid_impl(self):
        return self.step, self._uuid + self.training_data_uuid
