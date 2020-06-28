from typing import Dict, Tuple, Optional

import numpy as np  # type: ignore
from numpy import ndarray

import pjdata.aux.uuid as u

import pjdata.transformer.transformer as tr


class LinAlgHelper:  # TODO: dismiss this mixin and create a bunch of functions
    @staticmethod
    def _as_vector(mat: ndarray) -> ndarray:
        size = max(mat.shape[0], mat.shape[1])
        try:
            return mat.reshape(size)
        except Exception as e:
            print(e)
            raise Exception(
                f'Expecting matrix {mat} as a column or row vector...')

    @staticmethod
    def _as_column_vector(vec: ndarray) -> ndarray:
        return vec.reshape(len(vec), 1)

    @classmethod
    def _mat2vec(cls, m: ndarray, default: ndarray = None) -> ndarray:
        return default if m is None else cls._as_vector(m)

    @staticmethod
    def _mat2sca(m: ndarray, default: float = None) -> Optional[float]:
        return default if m is None else m[0][0]

    @classmethod
    def _field_as_matrix(cls, field_value: 't.Field') -> 't.Field':
        """Given a field, return its corresponding matrix or itself if it is a list."""

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

        if callable(field_value):
            return field_value

        raise Exception("Unknown field type ", type(field_value))

    @classmethod
    def fields2matrices(cls, fields: Dict[str, 't.Field']) -> Dict[str, 't.Field']:
        matrices = {}
        for name, value in fields.items():
            if len(name) == 1:
                name = name.upper()
            matrices[name] = cls._field_as_matrix(value)
        return matrices


def evolve(uuid: u.UUID, transformers: Tuple[tr.Transformer, ...]) -> u.UUID:
    for transformer in transformers:
        uuid *= transformer.uuid
    return uuid


def evolve_id(
        uuid: u.UUID,
        uuids: Dict[str, u.UUID],
        transformers: Tuple[tr.Transformer, ...],
        matrices: Dict[str, "t.Field"],
) :
    """Return UUID/UUIDs after transformations."""

    # Update matrix UUIDs.
    uuids_ = uuids.copy()
    for name, value in matrices.items():
        muuid = uuids.get(
            name,
            # u.UUID(co.pack(value))
            uuid * u.UUID(bytes(name, 'latin1'))  # faster
        )

        # Transform UUID.
        muuid = evolve(muuid, transformers)
        uuids_[name] = muuid

    # Update UUID.
    uuid = evolve(uuid, transformers)

    return uuid, uuids_
