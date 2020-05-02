from dataclasses import dataclass
from functools import partial

from pjdata.aux.encoders import UUID

from pjdata.data import Data


class MockupData(Data):
    """Exactly like Data, but without matrices."""

    def __getattr__(self, item):
        if 0 < len(item) < 3:
            raise Exception(
                'This a MockupData object. It has no matrices nor id.'
            )
        else:
            return self.__getattribute__(item)


class UUIDData(MockupData):
    """Like HollowData, but the only available information is the UUID."""

    def __init__(self, uuid):
        super().__init__()
        self._uuid = uuid

    def _uuid_impl(self):
        return 'uuid', self._uuid


class NoData(type):
    """Singleton to feed Data generators."""
    uuid = UUID()
    uuids = {}
    history = []
    matrices = {}
    failure = None
    isfrozen = False
    allfrozen = False

    @staticmethod
    def mockup(transformations):
        """A light Data object, i.e. without matrices."""
        return Data.mockup(NoData, transformations)

    #
    # # name = "No data"
    # # desc = ''
    # sid = uuid.pretty[:8]
    # # hollow = HollowData(history=[], failure=failure)
    # iscollection = False
    #
    # @staticmethod
    # def mockup(transformations):
    #     """A light Data object, i.e. without matrices."""
    #     return Data.mockup(NoData, transformations)
    #
    @staticmethod
    def updated(transformations, failure='keep', **matrices):
        return Data.updated(NoData, transformations, failure, **matrices)
    #
    # def __new__(mcs, *args, **kwargs):
    #     raise Exception('NoData is a singleton and shouldn\'t be instantiated')
    #
    # def __bool__(self):
    #     return False

