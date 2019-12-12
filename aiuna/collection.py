from typing import Iterator

from pjdata.data import Data
from itertools import repeat

from pjdata.history import History


class Collection:
    """An optimized list of Data objects (TODO: optimize).

    To be used through concurrent components:
        Expand, Map, Reduce


    Attributes
    ----------

    Parameters
    ----------
    datas
        Usually, a list of Data objects.
        When 'datas' is a single Data object, this collection will replicate it
        infinitelly.
    history
        History object of transformations.
    failure
        The cause, when the provided history leads to a failure.
    dataset
        The user can set a dataset if convenient.
    """
    _almost_infinity = 10_000_000_000

    def __init__(self, datas, history=None, failure=None, dataset=None):
        if history is None:
            history = History([])
        self.history = history
        self.failure = failure
        self.dataset = dataset

        self.infinite = False
        if isinstance(datas, Data):
            self.infinite = True
            self.datas = repeat(datas, times=self._almost_infinity)
            self.size = self._almost_infinity
        else:
            self.datas = datas
            self.size = len(datas)
        self.current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.current_index += 1
        if self.current_index >= self.size:
            self.current_index = 0
            raise StopIteration('No more Data objects left.')
        if isinstance(self.datas, Iterator):
            return next(self.datas)
        else:
            return self.datas[self.current_index]

    def __str__(self):
        return '\n'.join(str(data) for data in self.datas)

    def updated(self, transformation, datas, failure='keep'):
        """Recreate Collection object with updated history, failure and datas.

        Parameters
        ----------
        transformation
            Transformation object.
        failure
            The failure caused by the given transformation, if it failed.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous failures
        datas
            New list of Data object.

        Returns
        -------
        New Collection object (it may keep some references for performance).
        """
        if failure == 'keep':
            failure = self.failure

        return Collection(datas=datas,
                          history=self.history.extended(transformation),
                          failure=failure, dataset=self.dataset)
