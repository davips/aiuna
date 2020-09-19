from aiuna.content.data import Data
from aiuna.history import History
from cruipto.uuid import UUID


class UUIDData(Data):
    """Exactly like Data, but without matrices and infos.

     The only available information is the UUID."""

    def __init__(self, uuid):
        if isinstance(uuid, str):
            uuid = UUID(uuid)
        super().__init__(uuid, {}, history=History([]), failure=None, frozen=False, hollow=True, stream=None)

    def _uuid_impl(self) -> UUID:
        return self._uuid

    def __getattr__(self, item):
        if item not in ["id"]:
            raise Exception("This a UUIDData object. It has no fields!")

    # else:
    #     return self.__getattribute__(item)


class NoData(type):
    """Singleton to feed Data iterators."""

    uuid = UUID()
    id = uuid.id
    uuids: dict = {}
    history: History = History([])
    stream = None
    matrices = {}
    failure: str = None
    isfrozen = False
    ishollow = False
    storage_info = None
    trdata = None

    @staticmethod
    def hollow(transformer):
        """A light Data object, i.e. without matrices."""
        # noinspection PyCallByClass
        return Data.hollow(NoData, transformer)

    @staticmethod
    def transformedby(transformer):
        """Return this Data object transformed by func.

        Return itself if it is frozen or failed.        """
        result = transformer._transform_impl(NoData)
        if isinstance(result, dict):
            return NoData.replace(transformers=(transformer,), **result)
        return result

    @staticmethod
    def replace(transformers, failure="keep", stream="keep", **fields):
        # noinspection PyCallByClass,PyTypeChecker
        return Data.replace(NoData, transformers, failure=failure, stream=stream, **fields)

    def __new__(mcs, *args, **kwargs):
        raise Exception("NoData is a singleton and shouldn't be instantiated")

    def __bool__(self):
        return False
