from __future__ import annotations

from typing import Union, Tuple, List, Callable, Type, Dict, Generator, Iterator

from numpy import ndarray  # type: ignore

import pjdata.content.data as d
import pjdata.content.specialdata as s
from pjdata.mixin.identification import withIdentification

Data = Union[Type[s.NoData], d.Data]  # TODO: <-- check for other types of Data?
# HINT: Multi containing a Sink can produce heterogeneous tuples
DataTup = Tuple[Data, ...]
DataOrTup = Union[Data, DataTup]

Field = Union[List[str], ndarray]  # For Data fields.
Acc = Union[List[Data], List[ndarray], float]  # Possible result types for cumulative streams.

Result = Union[
    # Possible result types for _enhancer_func and _model_func.
    Data,
    Dict[str, Union[None, Field, Iterator[Data], Generator[Data, None, Acc], Callable[[], Field]]],
]

# Type of function transform(). Can return NoData because of Sink.
Transformation = Callable[[Data], Result]

Context = Union[str, withIdentification]
