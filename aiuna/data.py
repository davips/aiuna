from encoders import uuid
from history import History
from identifyable import Identifyable


class Data(Identifyable):
    def __init__(self, dataset, history=None, failure=None, **matrices):
        """
        Immutable lazy data for all machine learning scenarios we could imagine.
        :param dataset: Original dataset.
        :param history: list of transformations, i.e. tuples (transformer,
        operation) like [(<transformer1>, 'a'), (<transformer2>, 'a')]
        :param failure: the cause, when provided history leads to a failure
        :param matrices: dictionary like {X: <numpy array>, Y: <numpy
        array>}. Matrix names should have a single character!
        """
        self.__dict__.update(matrices)

        if history is None:
            history = History([])
        self.history = history
        self.dataset = dataset
        self.failure = failure
        self.matrices = matrices

        # # Shortcuts
        # self.y = ...
        # self.Xy = self.X, self.y

    def updated(self, transformation, **kwargs):
        """
        Recreate Data object with updated matrices.
        :param transformation: transformation (pipeline or transformation)
        :param kwargs: changed/added matrices and updated values
        :return: new Data object
        """
        new_matrices = self.matrices.copy()
        new_matrices.update(kwargs)
        return Data(dataset=self.dataset,
                    history=self.history.transformations.append(transformation),
                    failure=self.failure, **new_matrices)

    def check_against_dataset(self):
        """
        Check if dataset field descriptions are compatible with provided
        matrices.
        """
        raise NotImplementedError

    def _uuid_impl(self):
        return self.dataset.uuid() + self.history.uuid()
