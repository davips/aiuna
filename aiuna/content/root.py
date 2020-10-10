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
    def update(step, **kwargs):
        # noinspection PyCallByClass,PyTypeChecker
        return Data.update(Root, step, **kwargs)

    @staticmethod
    def _update(step, **kwargs):
        # noinspection PyCallByClass,PyTypeChecker,PyProtectedMember
        return Data._update(Root, step, **kwargs)

    def __new__(mcs, *args, **kwargs):
        raise Exception("Root is a singleton and shouldn't be instantiated")

    def __bool__(self):
        return False

