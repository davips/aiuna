from functools import lru_cache

import numpy as np

from pjdata.abc.abstractdata import AbstractData
from pjdata.aux.compression import pack_data
from pjdata.aux.encoders import UUID
from pjdata.mixin.linalghelper import LinAlgHelper
from pjdata.mixin.printable import Printable


class Data(AbstractData, LinAlgHelper, Printable):
    """Immutable lazy data for all machine learning scenarios one imagine.

    Attributes
    ----------
    matrices
        A dictionary, like {X: <numpy array>, Y: <numpy array>}.
        Matrix names should start with an uppercase letter and
        have at most two letters.
    fields
        Shorcuts 'matrices', but seeing each column-vector matrix as a vector
        and each single element matrix as a scalar.

    Parameters
    ----------
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

    def __init__(self, **matrices):
        kwargs = matrices
        super().__init__(jsonable=kwargs)

        # Divide kwargs.
        matrices = {}
        settings = {}
        for k, v in kwargs.items():
            if len(k) < 3:
                matrices[k] = v
            else:
                settings[k] = v

        # TODO: what to do with 'name' and 'desc'?

        if 'uuid' not in settings:
            # TODO: Implement the rare case where the user creates Data:
            raise NotImplementedError
            # Intended for Data and matrices created directly by the user.
            # self.history = []
            # self._uuid = UUID()
            #
            # # Calculate unique hash for the matrices.
            # packs = ''.encode()
            # for mat in matrices:
            #     packs += pack_data(mat)  # TODO: store uuids for each matrix
            # matrices_hexhash = hexuuid(packs)
            # matrices_hash = tiny_md5(matrices_hexhash)
            #
            # if 'name' in matrices:
            #     matrices['name'] += '_' + matrices_hash[:6]
            #
            # class New:
            #     """Fake New transformer."""
            #     name = 'New'
            #     path = 'pjml.tool.data.flow.new'
            #     uuid = matrices_hash
            #     hexuuid = matrices_hexhash
            #     config = matrices
            #     jsonable = {'_id': f'{name}@{path}', 'config': config}
            #     serialized = serialize(jsonable)
            #
            # transformer = New()
            # # New transformations are always represented as 'u', no matter
            # # which step.
            # transformation = Transformation(transformer, 'u')
            # history = [transformation]

        self.history = settings['history']
        self._uuid = settings['uuid']
        self.uuids = settings['uuids']

        self.failure = settings.get('failure', None)
        self.matrices = matrices
        self._fields = matrices.copy()

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
        frozen
        transformations
            List of Transformation objects.
        failure
            The failure caused by the given transformation, if it failed.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous failures
        matrices
            Changed/added matrices and updated values.

        dataset
            Original dataset where data was extract from.
        history
            History object of transformations.
        failure
            The cause, when the provided history leads to a failure.

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

        # Update UUID digests.
        new_digests = {}
        for field in new_matrices:
            new_uuid = self.uuids.get(field, UUID())

            # Transform new fields' UUID.
            if field in matrices:
                for transformation in transformations:
                    new_uuid += transformation.uuid00

            new_digests[field] = new_uuid

        # Update UUID.
        new_uuid = self.uuid00
        for transformation in transformations:
            new_uuid += transformation.uuid00

        return self.__class__(
            history=self.history + transformations,
            failure=failure,
            digests=new_digests,
            uuid=new_uuid,
            **new_matrices
        )

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

    @property
    @lru_cache()
    def field_names(self):
        return list(self._fields.keys())

    @lru_cache()
    def field_dump(self, field):
        """Lazily compressed matrix for a given field.
        Useful for optimized persistence backends for Cache."""
        return pack_data(self.field(field))

    @property
    @lru_cache()
    def frozen(self):
        from pjdata.specialdata import FrozenData
        return FrozenData(self)

    @property
    def allfrozen(self):
        return False

    @property
    @lru_cache()
    def hollow(self):
        return self.hollow_extended([])

    def hollow_extended(self, transformations):
        """A light Data object, i.e. without matrices."""
        from pjdata.specialdata import HollowData
        kwargs = {}
        if 'name' in self.matrices:  # TODO: see TODO in init
            kwargs['name'] = self.name
        if 'desc' in self.matrices:
            kwargs['desc'] = self.desc
        return HollowData(history=self.history.extended(transformations),
                          failure=self.failure, **kwargs)

    @property
    @lru_cache()
    def consistent_with_dataset(self):
        """Check if dataset field descriptions are compatible with provided
        matrices.
        """
        raise NotImplementedError

    def _uuid_impl00(self):
        return self._uuid

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
