from aiuna.content.data import Data
from aiuna.history import History
from cruipto.uuid import UUID
from transf.noop import NoOp


class Root(Data):
    def __call__(self, *args, **kwargs):
        raise Exception("Root data is a singleton and cannot be instantiated!")


# 06YIZJGwpbx9nPR4asgVOMo is the uuid of the empty list []
uuids = {"changed": UUID(b"[]")}
Root = Root(UUID(), uuids, History(NoOp()), changed=[])
