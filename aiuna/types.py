<<<<<<< HEAD
=======
from __future__ import annotations

from itertools import repeat
from typing import Union, Tuple, List, Literal, Callable, Type, Dict, Generator, Iterator

from numpy import ndarray  # type: ignore

import pjdata.content.data as d
import pjdata.content.specialdata as s

Data = Union[Type[s.NoData], d.Data]
# HINT: Multi containing a Sink can produce heterogeneous tuples
DataTup = Tuple[Data, ...]
DataOrTup = Union[Data, DataTup]

Field = Union[List[str], ndarray]  # For Data fields.
Status = Union[bool, Literal["keep"]]  # For frozen and hollow updates.
Acc = Union[List[Data], List[ndarray], float]  # Possible result types for cumulative streams.

Result = Union[
    # Possible result types for _enhancer_func and _model_func.
    Data,
    Dict[
        str,
        Union[None, Field, Iterator[Data], Generator[Data, None, Acc], Callable[[], Field]]
    ]
]

# Type of function transform(). Can return NoData because of Sink.
Transformation = Callable[[Data], Result]
>>>>>>> 85c3a14... Simplify types and streamers by excluding Collection and Streamer hierarchy classes
