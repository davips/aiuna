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
