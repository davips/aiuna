from functools import lru_cache

import numpy as np

from pjdata.aux.encoders import int2tiny
from pjdata.aux.identifyable import Identifyable
from pjdata.aux.linalghelper import LinAlgHelper
from pjdata.dataset import NoDataset
from pjdata.history import History


class Data(Identifyable, LinAlgHelper):
    """Immutable lazy data for all machine learning scenarios we could
    imagine.

    Attributes
    ----------
    matrices
        A dictionary like {X: <numpy array>, Y: <numpy array>}.
    fields
        Shorcuts 'matrices', but seeing each column-vector matrix as a vector
        and each single element matrix as a scalar.

    Parameters
    ----------
    dataset
        Original dataset where data was extract from.
    history
        History object of transformations.
    failure
        The cause, when the provided history leads to a failure.
    matrices
        A dictionary like {X: <numpy array>, Y: <numpy array>}.
        Matrix names should have a single character!
    """

    # Some mappings from vector/scalar to the matrix where it is stored.
    _vec2mat_map = {i: i.upper() for i in ['y', 'z', 'v', 'w']}
    _sca2mat_map = {i: i.upper() for i in ['r', 's', 't']}

    def __init__(self, dataset, history=None, failure=None, **matrices):
        if history is None:
            history = History([])
        self.history = history
        self.dataset = dataset
        self.failure = failure
        self.matrices = matrices
        self.fields = matrices.copy()

        # Add vector shortcuts.
        for k, v in self._vec2mat_map.items():
            if v in matrices:
                self.fields[k] = self._matrix_to_vector(matrices[v])

        # Add scalar shortcuts.
        for k, v in self._sca2mat_map.items():
            if v in matrices:
                self.fields[k] = self._matrix_to_scalar(matrices[v])

        self.__dict__.update(self.fields)

    def updated1(self, transformation, failure='keep', **matrices):
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

        return Data(dataset=self.dataset,
                    history=self.history.extended(transformation),
                    failure=failure, **new_matrices)

    @property
    @lru_cache()
    def phantom(self):
        """A light PhantomData object, without matrices."""
        return PhantomData(dataset=self.dataset, history=self.history,
                           failure=self.failure)

    @property
    @lru_cache()
    def checked_against_dataset(self):
        """Check if dataset field descriptions are compatible with provided
        matrices.
        """
        raise NotImplementedError

    @property
    @lru_cache()
    def Xy(self):
        return self.__dict__['X'], self.__dict__['y']

    def _uuid_impl(self):
        """First character indicates the operation of the last transformation,
        or 'd' if none."""
        if self.history.last is None:
            return 'd', self.dataset.uuid + self.history.uuid
        else:
            return self.history.last.operation, \
                   self.dataset.uuid + self.history.uuid

    def _translate(self, field, value):
        """Given a field name, return its underlying matrix name and content.
        """
        if field in self._vec2mat_map:
            # Vector.
            return field.upper(), self._as_column_vector(value)
        elif field in self._sca2mat_map:
            # Scalar.
            return field.upper(), np.array(value, ndmin=2)
        else:
            # Matrix given directly.
            return field, value

    def __str__(self):
        return self.dataset.__str__()

    __repr__ = __str__

    fixed = updated1  # Shortcut to avoid conditional Data vs DirtyContent


class PhantomData(Data):
    """Exactly like Data, but without the matrices."""

    def __getattr__(self, item):
        if len(item) == 1 or item == 'Xy':
            raise Exception('This a phantom Data object. It has no matrices.')


class NoData(type):
    dataset = NoDataset
    uuid = 'n' + int2tiny(0)
    failure = None

    def __new__(cls, *args, **kwargs):
        raise Exception('NoData is a singleton and shouldn\'t be instantiated')
