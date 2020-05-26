from numpy.core.multiarray import ndarray
import numpy as np

from pjdata.aux.compression import pack
from pjdata.aux.uuid import UUID


class LinAlgHelper:
    @staticmethod
    def _as_vector(mat):
        size = max(mat.shape[0], mat.shape[1])
        try:
            return mat.reshape(size)
        except Exception as e:
            print(e)
            raise Exception(
                f'Expecting matrix {mat} as a column or row vector...')

    @staticmethod
    def _as_column_vector(vec):
        return vec.reshape(len(vec), 1)

    @classmethod
    def _mat2vec(cls, m, default=None):
        return default if m is None else cls._as_vector(m)

    @staticmethod
    def _mat2sca(m, default=None):
        return default if m is None else m[0][0]

    @classmethod
    def _field_as_matrix(cls, field_value):
        """Given a field, return its corresponding matrix.
        """

        # Matrix given directly.
        if isinstance(field_value, ndarray) and len(field_value.shape) == 2:
            return field_value

        # Vector.
        if isinstance(field_value, ndarray) and len(field_value.shape) == 1:
            return cls._as_column_vector(field_value)

        # Scalar.
        if isinstance(field_value, int):
            return np.array(field_value, ndmin=2)

        if isinstance(field_value, list):
            return field_value

        raise Exception('Unknown field type ', type(field_value))

    @classmethod
    def _fields2matrices(cls, fields):
        matrices = {}
        for name, value in fields.items():
            if len(name) == 1:
                name = name.upper()
            matrices[name] = cls._field_as_matrix(value)
        return matrices

    @staticmethod
    def _evolve_id(uuid, uuids, transformations, matrices):
        """Return UUID/UUIDs after transformations."""

        # Update matrix UUIDs.
        uuids_ = uuids.copy()
        for name, value in matrices.items():
            # If it is a new matrix, assign a UUID for its birth.
            # TODO:
            #  Benchmark to evaluate if using pack(X) as identity here is too
            #  slow. Having a start identical to that of data_creation seems
            #  good, but it can be slow for big matrices created after transf.
            #  However, it is not usual. E.g. Xbig -> Ubig.
            #  It is needed to avoid different UUIDs for the same content.
            #  A faster/dirtier choice would be data.uuid*matrix_name as birth.
            #  UPDATE:
            #  It seems like ZStd also doesn't like to be inside a thread, here
            #  and at pickleserver it gives the same error at the same time:
            #  'ZstdError: cannot compress: Src size is incorrect'
            muuid = uuids.get(
                name, UUID(pack(value))
                # name, self.uuid * UUID(bytes(name, 'latin1'))  # faster
            )

            # Transform UUID.
            muuid = evolve(muuid, transformations)
            uuids_[name] = muuid

        # Update UUID.
        uuid = evolve(uuid, transformations)

        return uuid, uuids_


def evolve(uuid, transformations):
    for transformation in transformations:
        uuid *= transformation.uuid
    return uuid
