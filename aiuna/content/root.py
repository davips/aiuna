from aiuna.content.data import Data
from aiuna.history import History
from cruipto.uuid import UUID


class Root(Data):
    def __call__(self, *args, **kwargs):
        raise Exception("Root data is a singleton and cannot be instantiated!")


Root = Root(UUID(), {}, History([]), UUID())
