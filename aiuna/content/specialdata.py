from aiuna.content.data import Data
from aiuna.history import History
from cruipto.uuid import UUID


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
    def hollow(step):
        """A light Data object, i.e. without matrices."""
        # noinspection PyCallByClass,PyTypeChecker
        return Data.hollow(Root, step)

    @staticmethod
    def replace(step, **kwargs):
        # noinspection PyCallByClass,PyTypeChecker
        return Data.replace(Root, step, **kwargs)

    @staticmethod
    def _replace(step, **kwargs):
        # noinspection PyCallByClass,PyTypeChecker,PyProtectedMember
        return Data._replace(Root, step, **kwargs)

    def __new__(mcs, *args, **kwargs):
        raise Exception("Root is a singleton and shouldn't be instantiated")

    def __bool__(self):
        return False

