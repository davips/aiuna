from aiuna.content.data import Data
from aiuna.history import History
from cruipto.uuid import UUID


class UUIDData(Data):
    """Exactly like Data, but without matrices and infos.

     The only available information is the UUID."""

    def __init__(self, uuid):
        if isinstance(uuid, str):
            uuid = UUID(uuid)
        super().__init__(uuid, {}, history=History([]), hollow=True)

    def _uuid_impl(self) -> UUID:
        return self._uuid

    def __getattr__(self, item):
        if item not in ["id"]:
            raise Exception("This a UUIDData object. It has no fields!")

    # else:
    #     return self.__getattribute__(item)


class Root(type):
    """Singleton to feed Data iterators."""

    history: History = History([])
    uuid = UUID()
    id = uuid.id
    uuids: dict = {}
    stream = None
    matrices = {}
    failure: str = None
    time = None
    timeout = None
    ishollow = False
    storage_info = None
    inner = None

    @staticmethod
    def hollow(transformer):
        """A light Data object, i.e. without matrices."""
        # noinspection PyCallByClass,PyTypeChecker
        return Data.hollow(Root, transformer)

    # @staticmethod
    # def transformedby(transformer):
    #     """Return this Data object transformed by func.
    #
    #     Return itself if it is frozen or failed.        """
    #     result = transformer._transform_impl(Root)
    #     if isinstance(result, dict):
    #         return Root.replace(transformer=(transformer,), **result)
    #     return result

    @staticmethod
    def replace(transformer, **kwargs):
        # noinspection PyCallByClass,PyTypeChecker
        return Data.replace(Root, transformer, **kwargs)

    @staticmethod
    def _replace(transformer, **kwargs):
        # noinspection PyCallByClass,PyTypeChecker,PyProtectedMember
        return Data._replace(Root, transformer, **kwargs)

    def __new__(mcs, *args, **kwargs):
        raise Exception("Root is a singleton and shouldn't be instantiated")

    def __bool__(self):
        return False
