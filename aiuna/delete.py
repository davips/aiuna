from transf.dataindependentstep_ import DataIndependentStep_
from transf.noop import NoOp


class Del(DataIndependentStep_):
    isclass = True
    isoperator = False

    def __init__(self, field):
        super().__init__(field=field)
        self.field = field

    def _process_(self, data):
        d = data.update(NoOp())  # just a copy
        del d[self.field]
        return d.update(self)
