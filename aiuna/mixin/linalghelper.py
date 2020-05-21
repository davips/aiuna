from numpy.core.multiarray import ndarray
import numpy as np


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
    def _convert(cls, field_value):
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

        raise Exception('Unknown field type ', type(field_value))
