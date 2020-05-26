from pjdata.aux.uuid import UUID

from pjdata.data import Data


class UUIDData(Data):
    """Exactly like Data, but without matrices and infos.

     The only available information is the UUID."""

    def __init__(self, uuid):
        super().__init__(tuple(), failure=False, frozen=False, hollow=True)
        self._uuid = uuid

    def _uuid_impl(self):
        return self._uuid

    def __getattr__(self, item):
        if 0 < len(item) < 3:
            raise Exception(
                'This a UUIDData object. It has no fields!'
            )
        else:
            return self.__getattribute__(item)


class NoData(type):
    """Singleton to feed Data generators."""
    uuid = UUID()
    id = uuid.id
    uuids = {}
    history = []
    matrices = {}
    failure = None
    isfrozen = False
    ishollow = False
    allfrozen = False
    storage_info = None

    @staticmethod
    def hollow(transformations):
        """A light Data object, i.e. without matrices."""
        return Data.hollow(NoData, transformations)

    #
    # # name = "No data"
    # # desc = ''
    # sid = uuid.pretty[:6]
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

    @staticmethod
    def _fields2matrices(fields):
        from pjdata.mixin.linalghelper import LinAlgHelper
        return LinAlgHelper._fields2matrices(fields)
    #
    # def __new__(mcs, *args, **kwargs):
    #     raise Exception('NoData is a singleton and shouldn\'t be instantiated')
    #
    # def __bool__(self):
    #     return False
