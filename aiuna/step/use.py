from pjdata.step.apply import Transformation


class Use(Transformation):
    def __init__(self, transformer, training_data):
        """
        Immutable use of a Transformer.
        :param transformer: Transformer/Pipeline
        training_data
            data provided to transformer.apply(data)
        """
        if training_data is None:
            self.training_data_uuid = 'DØØØØØØØØØØØØØØØØØØ0'
        else:
            self.training_data_uuid = training_data.uuid

        super().__init__(transformer, 'u')

    def _uuid_impl(self):
        return self.step, self.transformer.uuid + self.training_data_uuid

    def __str__(self):
        return str(
            self.transformer
        ) + '+' + self.training_data_uuid + '->' + self.step

    __repr__ = __str__
