from transf.dataindependentstep_ import DataIndependentStep_


class Del(DataIndependentStep_):
    isclass = True
    isoperator = False

    def __init__(self, field):
        super().__init__(field=field)
        self.field = field

    def _process_(self, data):
        #TODO: mixin withUpdate inside transf, implemented by Data
        não lembro o motivo do todo acima, ler papeis

        d = data.update([])  # just a copy
        del d[self.field]
        return d.update(self)
