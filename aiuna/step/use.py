from pjdata.step.apply import Transformation


class Use(Transformation):
    def __init__(self, transformer, training_data):
        """
        Immutable use of a Transformer.
        :param transformer: Transformer/Pipeline
        training_data
            data provided to transformer.apply(data)
        """
        super().__init__(transformer, 'u')
        self.training_data = training_data

    def _uuid_impl(self):
        return self.step, self.transformer.uuid + self.training_data.uuid
