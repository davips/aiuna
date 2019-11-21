from information.encoders import uuid


class Data:
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
            history = []
        self.history = history
        self.dataset = dataset
        self.failure = failure

        # Add lazy cache for uuid
        self._uuid = None

        # # Shortcuts
        # self.y = ...
        # self.Xy = self.X, self.y

    def uuid(self):
        """
        Lazily calculated unique identifier for this dataset.
        :return: unique identifier
        """
        if self._uuid is None:
            txt = (self.dataset.uuid() + self.history.uuid()).encode()
            self._uuid = uuid(txt)
        return self._uuid

    def sid(self):
        """
        Short uuID
        First 10 chars of uuid for printing purposes.
        Max of 1 collision each 1048576 combinations.
        :return:
        """
        return self.uuid()[:10]
