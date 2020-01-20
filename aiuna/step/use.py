from pjdata.step.apply import Transformation


class Use(Transformation):
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

        super().__init__(transformer, 'u')

    def _uuid_impl(self):
        return self.step, self.transformer.uuid + self.training_data_uuid

    def __str__(self):
        return str(
            self.transformer
        ) + '+' + self.training_data_uuid + '->' + self.step

    __repr__ = __str__
