from aiuna.content.data import Data
from cruipto.uuid import UUID
from transf.dataindependentstep_ import DataIndependentStep_


class Del(DataIndependentStep_):
    def __init__(self, field):
        super().__init__(field=field)
        self.field = field

    def _process_(self, data):
        fields = data.field_funcs_m.copy()
        del fields[self.field]
        fields["changed"] = []

        uuids = data.uuids.copy()
        uuids["changed"] = UUID(b"[]")

        return Data(data.uuid, uuids, data.history << self, **fields)
