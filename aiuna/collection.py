from itertools import repeat
from typing import Iterator

from pjdata.abc.abstractdata import AbstractData
from pjdata.history import History


class Collection(AbstractData):
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

    def __init__(self, history, failure, original_data):
        # TODO: is collection printable?
        if history is None:
            history = History([])
        self.history = history
        self.failure = failure
        self.next_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_index == self.size:
            self.next_index = 0
            raise StopIteration('No more Data objects left. Restarted!')
        nex = next(self._datas) if isinstance(self._datas, Iterator) else \
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

    def updated(self, transformations, datas=None, failure='keep'):
        """Recreate Collection object with updated history, failure and datas.

        Parameters
        ----------
        transformations
            List of Transformation objects.
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

        if datas is None:
            if self.infinite:
                datas = next(self._datas)
            else:
                datas = self._datas
        # TODO: to require changes on Xt and Xd when X is changed.
        return Collection(datas=datas,
                          history=self.history.extended(transformations),
                          failure=failure, dataset=self.dataset)

    def last_transformation_replaced(self, transformation):
        """Replace last transformation in history for convenience.

        Provided transformation should be equivalent to the replaced one for
        consistency.
        """
        return Collection(datas=self._datas,
                          history=History(self.history[:-1] + [transformation]),
                          failure=self.failure, dataset=self.dataset)

    def _uuid_impl(self):
        if self.infinite:
            uuids = next(self._datas).uuid
        else:
            uuids = ""
            for data in self._datas:
                uuids = uuids + data.uuid
        if self.history.last is None:
            return 'c', self.history.uuid + self._uuids
        else:
            return self.history.last.step.upper(), \
                   self.history.uuid + self._uuids

    @property
    def all_nones(self):
        if self._all_nones is None:
            self._all_nones = not any(self._datas)
        return self._all_nones

    @property
    @lru_cache()
    def isfinite(self):
        from pjdata.finitecollection import FiniteCollection
        return isinstance(self, FiniteCollection)
