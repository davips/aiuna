from functools import lru_cache

import numpy as np

from pjdata.abc.abstractdata import AbstractData
from pjdata.aux.compression import pack_data
from pjdata.aux.encoders import uuid
from pjdata.aux.serialization import serialize
from pjdata.history import History
from pjdata.mixin.linalghelper import LinAlgHelper
from pjdata.mixin.printable import Printable
from pjdata.step.transformation import Transformation


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

    def __init__(self, history=None, failure=None, frozen=False, **matrices):
        jsonable = {'history': history, 'failure': failure}
        jsonable.update(**matrices)
        super().__init__(jsonable=jsonable)

        if history is None:
            # Calculate unique hash for the matrices.
            packs = ''.encode()
            for mat in matrices:
                packs += pack_data(mat)
            matrices_hash = uuid(packs, prefix='')

            if 'name' in matrices:
                matrices['name'] += '_' + matrices_hash[:6]

            class New:
                """Fake New transformer."""
                name = 'New'
                path = 'pjml.tool.data.flow.new'
                uuid = 'f' + matrices_hash
                config = matrices
                jsonable = {'_id': f'{name}@{path}', 'config': config}
                serialized = serialize(jsonable)

            transformer = New()
            # New transformations are always represented as 'u', no matter
            # which step.
            transformation = Transformation(transformer, 'u')
            history = History([transformation])

        self.history = history
        self.failure = failure
        self.isfrozen = frozen
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

    @property
    @lru_cache()
    def frozen(self):
        return self.__class__(
            history=self.history.extended([]),
            failure=self.failure, frozen=True,
            **self.matrices
        )

    def updated(self, transformations, failure='keep', frozen=None, **matrices):
        """Recreate Data object with updated matrices, history and failure.

        Parameters
        ----------
        frozen
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
        if frozen is None:
            frozen = self.isfrozen

        # Translate shortcuts.
        for name, value in matrices.items():
            new_name, new_value = self._translate(name, value)
            new_matrices[new_name] = new_value

        return self.__class__(
            history=self.history.extended(transformations),
            failure=failure, frozen=frozen,
            **new_matrices
        )

    @property
    @lru_cache()
    def fields(self):
        return list(self._fields.keys())

    @property
    @lru_cache()
    def hollow(self):
        return self.hollow_extended([])

    def hollow_extended(self, transformations):
        """A light Data object, i.e. without matrices."""
        from pjdata.specialdata import HollowData
        kwargs = {}
        if 'name' in self.matrices:
            kwargs['name'] = self.name
        if 'desc' in self.matrices:
            kwargs['desc'] = self.desc
        return HollowData(history=self.history.extended(transformations),
                          failure=self.failure, **kwargs)

    # @classmethod
    # @lru_cache()
    # def phantom_by_uuid(cls, uuid):
    #     """A light PhantomData object, without matrices."""
    #     return UUIDData(uuid)

    # @lru_cache()
    # def phantom_extended(self, transformations):
    #     """A light PhantomData object, without matrices."""
    #     return HollowData(
    #         history=self.history.extended(transformations),
    #         failure=self.failure
    #     )

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
        """First character indicates the step of the last transformation."""
        return self.history.last.step, self.history.uuid

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


class MissingField(Exception):
    pass
