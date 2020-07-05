from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Iterator, TYPE_CHECKING, Literal, Union

import pjdata.aux.uuid as u
import pjdata.content.data as d
import pjdata.types as t
import pjdata.transformer as tr


@dataclass(frozen=True)
class TemporaryData:
    """Temporary class to exist between a transformation and the supply of the responsible transformer."""
    data: t.Data

    def history_updated(self, transformers: Tuple[tr.Transformer, ...]):
        """Complete Data object started by 'updated_()'."""
        return self.data.updated(transformers=transformers)


class UUIDData(d.Data):
    """Exactly like Data, but without matrices and infos.

     The only available information is the UUID."""

    def __init__(self, uuid: u.UUID):
        super().__init__(tuple(), failure=None, frozen=False, hollow=True)
        self._uuid = uuid

    def _uuid_impl(self) -> u.UUID:
        return self._uuid

    def __getattr__(self, item):
        raise Exception(
            'This a UUIDData object. It has no fields!'
        )
    # else:
    #     return self.__getattribute__(item)


class NoData(type):
    """Singleton to feed Data iterators."""
    uuid = u.UUID()
    id = uuid.id
    uuids: dict = {}
    history: List[tr.Transformer] = []
    stream = None
    matrices: Dict[str, t.Field] = {}
    failure: str = None
    isfrozen = False
    ishollow = False
    storage_info = None

    @staticmethod
    def hollow(transformer: tr.Transformer) -> d.Data:
        """A light Data object, i.e. without matrices."""
        # noinspection PyCallByClass
        return d.Data.hollow(NoData, transformer)

    @staticmethod
    def transformedby(transformer: tr.Transformer):
        """Return this Data object transformed by func.

        Return itself if it is frozen or failed.        """
        result = transformer.rawtransform(NoData)
        if isinstance(result, dict):
            return NoData.updated(transformers=(transformer,), **result)
        return result

    @staticmethod
    def updated(
            transformers: Tuple[tr.Transformer, ...],
            failure: Union[str, t.Status] = 'keep',
            stream: Union[Iterator[t.Data], None, Literal["keep"]] = 'keep',
            **fields
    ) -> t.Data:
        # noinspection PyCallByClass
        return d.Data.updated(NoData, transformers, failure, stream, **fields)

    def __new__(mcs, *args, **kwargs):
        raise Exception('NoData is a singleton and shouldn\'t be instantiated')

    def __bool__(self):
        return False
