from transf.absdata import AbsData
from transf.dataindependentstep_ import DataIndependentStep_


class Del(DataIndependentStep_):
    isclass = True
    isoperator = False

    def __init__(self, field):
        super().__init__({"field": field})
        self.field = field

    def _process_(self, data: AbsData):
        d = data.replace([])  # just a copy
        del d.matrices[self.field]
        return d.replace(self)
