from functools import lru_cache

import numpy as np

from pjdata.abc.abstractdata import AbstractData
from pjdata.aux.encoders import int2tiny
from pjdata.mixin.identifyable import Identifyable
from pjdata.mixin.linalghelper import LinAlgHelper
from pjdata.dataset import NoDataset
from pjdata.history import History
from pjdata.mixin.printable import Printable


class Data(AbstractData, LinAlgHelper, Printable):
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
        Matrix names should have a single uppercase character, e.g.:
        X=[
           [23.2, 35.3, 'white'],
           [87.0, 52.7, 'brown']
        ]
        Y=[
           'rabbit',
           'mouse'
        ]
        They can be, ideally, numpy arrays (e.g. storing is optimized).
        A matrix name followed by a 'd' indicates its description, e.g.:
        Xd=['weight', 'height', 'color']
        Yd=['class']
        A matrix name followed by a 't' indicates its types ('ord', 'int',
        'real', 'cat'*).
        * -> A cathegorical/nominal type is given as a list of nominal values:
        Xt=['real', 'real', ['white', 'brown']]
        Yt=[['rabbit', 'mouse']]
    """

    # Some mappings from vector/scalar to the matrix where it is stored.
    _vec2mat_map = {i: i.upper() for i in ['y', 'z', 'v', 'w']}
    _sca2mat_map = {i: i.upper() for i in ['r', 's', 't']}

    def __init__(self, dataset, history=None, failure=None, **matrices):
        jsonable = {'dataset': dataset, 'history': history, 'failure': failure}
        jsonable.update(**matrices)
        super().__init__(jsonable=jsonable)

        if history is None:
            history = History([])
        self.history = history
        self.dataset = dataset
        self.name = dataset.name
        self.failure = failure
        self.matrices = matrices
        self._fields = matrices.copy()
        # self.content_matrices =
        # [v for k, v in matrices.items() if len(k) == 1]

        # Add vector shortcuts.
        for k, v in self._vec2mat_map.items():
            if v in matrices and (
                    matrices[v].shape[0] == 1 or matrices[v].shape[1] == 1):
                self._fields[k] = self._matrix_to_vector(matrices[v])

        # Add scalar shortcuts.
        for k, v in self._sca2mat_map.items():
            if v in matrices and matrices[v].shape == (1, 1):
                self._fields[k] = self._matrix_to_scalar(matrices[v])

        self.__dict__.update(self._fields)

    def updated(self, transformations, failure='keep', **matrices):
        """Recreate Data object with updated matrices, history and failure.

        Parameters
        ----------
        transformations
            List of Transformation objects.
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

        return self.__class__(dataset=self.dataset,
                              history=self.history.extended(transformations),
                              failure=failure, **new_matrices)

    @property
    @lru_cache()
    def phantom(self):
        """A light PhantomData object, without matrices."""
        return PhantomData(dataset=self.dataset, history=self.history,
                           failure=self.failure)

    @classmethod
    @lru_cache()
    def phantom_by_uuid(cls, uuid):
        """A light PhantomData object, without matrices."""
        return UUIDData(uuid)

    @lru_cache()
    def phantom_extended(self, transformations):
        """A light PhantomData object, without matrices."""
        return PhantomData(dataset=self.dataset,
                           history=self.history.extended(transformations),
                           failure=self.failure)

    @property
    @lru_cache()
    def consistent_with_dataset(self):
        """Check if dataset field descriptions are compatible with provided
        matrices.
        """
        raise NotImplementedError

    def field(self, field, component=None):
        if field not in self._fields:
            name = component.name if 'name' in dir(component) else component
            raise MissingField(
                f'\n=================================================\n'
                f'Last transformation:\n{self.history.last} ... \n'
                f' Data object <{self}>\n'
                f' last transformed by '
                f'{self.history.last and self.history.last.name} does '
                f'not provide field\n {field} needed by {name} .\n'
                f'Available fields: {list(self._fields.keys())}')
        return self._fields[field]

    @property
    @lru_cache()
    def Xy(self):
        return self.field('X'), self.field('y')

    def _uuid_impl(self):
        """First character indicates the step of the last transformation,
        or 'd' if none."""
        if self.history.last is None:
            return 'd', self.dataset.uuid + self.history.uuid
        else:
            return self.history.last.step, \
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


class PhantomData(Data):
    """Exactly like Data, but without the matrices."""

    @property
    def consistent_with_dataset(self):
        return True

    def __getattr__(self, item):
        if 0 < len(item) < 3:
            raise Exception('This a phantom Data object. It has no matrices.')
        else:
            return self.__getattribute__(item)


class UUIDData(PhantomData):
    """Exactly like Data, but only with UUID."""

    def __init__(self, uuid):
        super().__init__(NoDataset)
        self._uuid = uuid

    def _uuid_impl(self):
        return 'uuid', self._uuid


class NoData(type):
    dataset = NoDataset
    history = History([])
    name = dataset.name
    uuid = Identifyable.nothing
    sid = uuid[:10]
    failure = None
    phantom = PhantomData(dataset=dataset, history=history, failure=failure)

    def updated(self, transformations, failure='keep'):
        nodata = NoData
        nodata.failure = failure
        return nodata

    def __new__(cls, *args, **kwargs):
        raise Exception('NoData is a singleton and shouldn\'t be instantiated')

    def __bool__(self):
        return False


class MissingField(Exception):
    pass
