from aiuna.content.root import Root
from transf.dataindependentstep_ import DataIndependentStep_


class New(DataIndependentStep_):
    isclass = True
    isoperator = False

    def __init__(self, hashes, **matrices):
        super().__init__({"hashes": hashes})
        self.isclass = False
        self.hashes = hashes
        self.matrices = matrices
        self.data = Root.update(self, **self.matrices)

    def _process_(self, data):
        if data is not Root:
            raise Exception(f"{self.name} only accepts Root as Data. Use File(...).data or Sink instead.", type(data))
        return self.data

    def parameters(self):
        return self._config  # TODO:will this work?
