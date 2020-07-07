import typing as t
from typing import Dict, Tuple, Optional

import numpy as np  # type: ignore
from numpy import ndarray

import pjdata.transformer.transformer as tr


def _as_vector(mat: ndarray) -> ndarray:
    size = max(mat.shape[0], mat.shape[1])
    try:
        return mat.reshape(size)
    except Exception as e:
        raise Exception(f"Expecting a matrix {mat}, as a column or row vector...")


def _as_column_vector(vec: ndarray) -> ndarray:
    return vec.reshape(len(vec), 1)


def mat2vec(m: ndarray, default: ndarray = None) -> ndarray:
    return default if m is None else _as_vector(m)


def _mat2sca(m: ndarray, default: float = None) -> Optional[float]:
    return default if m is None else m[0][0]


def field_as_matrix(field_value):
    """Given a field, return its corresponding matrix or itself if it is a list."""

    # Matrix given directly.
    if isinstance(field_value, ndarray) and len(field_value.shape) == 2:
        return field_value

    # Vector.
    if isinstance(field_value, ndarray) and len(field_value.shape) == 1:
        return _as_column_vector(field_value)

    # Scalar.
    if isinstance(field_value, int):
        return np.array(field_value, ndmin=2)

    if isinstance(field_value, list):
        return field_value

    if callable(field_value):
        return field_value

    raise Exception("Unknown field type: ", type(field_value))


def fields2matrices(fields):
    matrices = {}
    for name, value in fields.items():
        if len(name) == 1:
            name = name.upper()
        matrices[name] = field_as_matrix(value)
    return matrices


def evolve(uuid, transformers, truuid):
    for transformer in transformers:
        uuid *= transformer.uuid(truuid)  # TODO: toda operaçao de uuid transformadora deve chamar com trdata
    return uuid


def evolve_id(uuid, uuids, transformers, matrices, truuid):
    """Return UUID/UUIDs after transformations."""

    # Update matrix UUIDs.
    uuids_ = uuids.copy()
    for name, value in matrices.items():
        # If it is a new matrix, assign a UUID for its birth.
        # TODO:
        #  Perform benchmark to evaluate if using pack(X) as identity here is too
        #  slow. Having a start identical to that of creation.py seems
        #  good, but it can be slow for big matrices created after transf.
        #  However, it is not usual. E.g. Xbig -> Ubig.
        #  It is needed to avoid different UUIDs for the same content.
        #  A faster/dirtier choice would be data.uuid*matrix_name as birth.
        #  UPDATE:
        #  It seems like ZStd also doesn't like to be inside a thread, here
        #  and at pickleserver it gives the same error at the same time:
        #  'ZstdError: cannot compress: Src size is incorrect'

        # TODO: UPDATED 10/jun
        #   Accessing fields just to calculate UUID defeats the purpose of lazy fields
        #   (including lazy data from cururu and stream).
        #   Vou colocar o cálculo rápido baseado em data.uuid*matrix_name,
        #   a desvantagem é não ter o início da matriz compatível com o início em File,
        #   mas talvez possamos mudar File pra ficar igual.

        muuid = uuids.get(name, uuid * u.UUID(bytes(name, "latin1")))  # <-- fallback value

        # Transform UUID.
        muuid = evolve(muuid, transformers, truuid)
        uuids_[name] = muuid

    # Update UUID.
    uuid = evolve(uuid, transformers, truuid)

    return uuid, uuids_
