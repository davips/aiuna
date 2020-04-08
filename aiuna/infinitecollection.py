from itertools import repeat
from pjdata.collection import Collection
from pjdata.finitecollection import FiniteCollection
from pjdata.history import History


class InfiniteCollection(Collection):
    _almost_infinity = 10_000_000_000

    def __init__(self, data, history=None, failure=None):
        super().__init__(history, failure, data)

        # Yes, all Data objects here are exactly the same (immutability):
        self._datas = repeat(data, times=self._almost_infinity)
        self.size = self._almost_infinity
        self.has_nones = False

        self._uuids = next(self._datas).uuid

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
            raise Exception('11111111112222222222 444444444444')
            # return InfiniteCollection(
            #     data=self.original_data,
            #     history=self.history.extended(transformations),
            #     failure=failure, dataset=self.dataset
            # )

        # TODO: to require changes on Xt and Xd when X is changed.
        return FiniteCollection(
            datas=datas,
            history=self.history.extended(transformations),
            failure=failure,
            original_data=self.original_data
        )

    def last_transformation_replaced(self, transformation):
        """Replace last transformation in history for convenience.

        Provided transformation should be equivalent to the replaced one for
        consistency.
        """
        return InfiniteCollection(
            self.original_data,
            history=History(self.history[:-1] + [transformation]),
            failure=self.failure
        )

    def __str__(self):
        return 'Infinite collection!' + \
               str(self.history) + ' ' + \
               str(self.failure) + ' '
