from pjdata.data import Data as SlowData
from pjdata.history import History
from pjdata.step.transformation import NoTransformation


class FastData(SlowData):
    def __init__(self, dataset, history=None, failure=None, **matrices):
        super().__init__(dataset, history, failure, **matrices)
        self.history.last = None
        # TODO: FastData seria um Data com zero history, para uma suposta
        #  melhora de desempenho.

    def updated(self, transformation, failure='keep', **matrices):
        """Recreate Data object with updated matrices, history and failure.

        Parameters
        ----------
        transformation
            Transformation object. None will generate a DirtyData object.
        failure
            The failure caused by the given transformation, if it failed.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous failures
        matrices
            Changed/added matrices and updated values.

        Returns
        -------
        New Data object (it keeps references to the old one for performance).
        """
        new_matrices = self.matrices.copy()
        if failure == 'keep':
            failure = self.failure

        # Translate shortcuts.
        for name, value in matrices.items():
            new_name, new_value = self._translate(name, value)
            new_matrices[new_name] = new_value

        notransf = NoTransformation
        notransf.uuid = self.history.uuid + transformation.uuid
        history = History([notransf])

        return FastData(dataset=self.dataset,
                        history=history,
                        failure=failure, **new_matrices)
