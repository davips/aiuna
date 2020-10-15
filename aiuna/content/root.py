from aiuna.content.data import Data


class Root(Data):
    def __call__(self, *args, **kwargs):
        raise Exception("Root data is a singleton and cannot be instantiated!")


class MetaRoot(type):
    root = None

    def __new__(mcs, *args, **kwargs):
        if mcs.root is None:
            from cruipto.uuid import UUID
            from aiuna.history import History
            mcs.root = Root(uuid=UUID(), uuids={}, history=History([]))
        return mcs.root
TODO adotar Root simples do StOverfl

# Scala-like companion object for the instantiable class Root at the beginning of this file.
# noinspection PyRedeclaration
class Root(metaclass=MetaRoot):
    """Singleton to feed Data processors."""
