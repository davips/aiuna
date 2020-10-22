from aiuna.content.data import Data
from cruipto.uuid import UUID
from transf.noop import NoOp


class Root(Data):
    def __call__(self, *args, **kwargs):
        raise Exception("Root data is a singleton and cannot be instantiated!")


# 06YIZJGwpbx9nPR4asgVOMo is the uuid of the empty list []           UUID(b"[]").id
Root = Root(UUID(), {"changed": UUID("06YIZJGwpbx9nPR4asgVOMo")}, NoOp(), changed=[])
