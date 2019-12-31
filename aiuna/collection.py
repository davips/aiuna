from typing import Iterator

from pjdata.data import Data
from itertools import repeat

from pjdata.history import History


class Collection:
    """An optimized list of Data objects (TODO: optimize).

    To be used through concurrent transformers:
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
            data = datas
            self.infinite = True
            self._datas = repeat(data.copy, times=self._almost_infinity)
            self.size = self._almost_infinity
            self.has_nones = False
        else:
            self._datas = datas
            self.size = len(datas)
            self.has_nones = not all(datas)

        self.next_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_index == self.size:
            self.next_index = 0
            raise StopIteration('No more Data objects left. Restarted!')
        nex = next(self._datas)() if isinstance(self._datas, Iterator) else \
            self._datas[self.next_index]
        self.next_index += 1
        return nex

    def __str__(self):
        if self.infinite:
            return 'Infinite collection!' + \
                   str(self.history) + ' ' + \
                   str(self.failure) + ' ' + \
                   str(self.dataset)
        return '\n'.join(str(data) for data in self._datas)

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
