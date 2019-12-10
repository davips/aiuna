class LinAlgHelper:
    @staticmethod
    def _as_vector(mat):
        s = mat.shape[0]
        return mat.reshape(s)

    @staticmethod
    def _as_column_vector(vec):
        return vec.reshape(len(vec), 1)

    @classmethod
    def _matrix_to_vector(cls, m, default=None):
        return default if m is None else cls._as_vector(m)

    @staticmethod
    def _matrix_to_scalar(m, default=None):
        return default if m is None else m[0][0]
