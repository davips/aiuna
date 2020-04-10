from pjdata.data import Data
from pjdata.history import History
from pjdata.mixin.identifyable import Identifyable


class HollowData(Data):
    """Exactly like Data, but without the matrices."""

    @property
    def consistent_with_dataset(self):
        return True

    def __getattr__(self, item):
        if 0 < len(item) < 3:
            raise Exception('This a phantom Data object. It has no matrices.')
        else:
            return self.__getattribute__(item)


class UUIDData(HollowData):
    """Like HollowData, but the only available information is the UUID."""

    def __init__(self, uuid):
        super().__init__([])
        self._uuid = uuid

    def _uuid_impl(self):
        return 'uuid', self._uuid


class NoData(type):
    history = History([])
    name = "No data"
    desc = ''
    uuid = Identifyable.nothing
    sid = uuid[:10]
    failure = None
    hollow = HollowData(history=history, failure=failure)

    @staticmethod
    def hollow_extended(transformations):
        """A light Data object, i.e. without matrices."""
        return HollowData(history=NoData.history.extended(transformations),
                          failure=NoData.failure,
                          name=NoData.name, desc=NoData.desc)

    @staticmethod
    def updated(transformations=None, failure=None):
        if transformations:
            raise Exception(
                'It makes no sense to update transformations for NoData!'
            )
        if failure is None:
            raise Exception(
                'It makes no sense to update NoData without providing failure!'
            )
        nodata = NoData
        nodata.failure = failure
        return nodata

    def __new__(mcs, *args, **kwargs):
        raise Exception('NoData is a singleton and shouldn\'t be instantiated')

    def __bool__(self):
        return False
