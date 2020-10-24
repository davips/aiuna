import json
from functools import cached_property
from aiuna.content.root import Root
from aiuna.creation import read_arff
from cruipto.uuid import UUID
from transf.dataindependentstep_ import DataIndependentStep_


class File(DataIndependentStep_):
    def __init__(self, name, path="./", hashes=None):
        self.isclass = False
        if not path.endswith("/"):
            print(path)
            raise Exception("Path should end with '/'", path)
        if name.endswith(".arff"):
            self._partial_config = {"name": name, "path": path}
            self.filename = path + name
        else:
            raise Exception("Unrecognized file extension:", name)
        self._hashes = hashes
        super().__init__(config_func=self._config)

    def _process_(self, data):
        if data is not Root:
            raise Exception(f"{self.name} only accepts Root as Data. Use File(...).data or Sink instead.", type(data))
        return self.data

    def _config(self):
        config = self._partial_config
        config["hashes"] = self.hashes
        return config

    def _uuid_(self):  # override uuid because default uuid is based on config, which includes file name/path
        uuid = UUID(json.dumps({"name": self.name, "path": self.context, "hashes": self.hashes}, ensure_ascii=False, sort_keys=True).encode())
        return uuid

    # REMINDER File cannot be lazy, since it depends on file content to know the uuid which will be used to generate the lazy Data object.
    @cached_property
    def data(self):
        d = read_arff(self.filename)
        self._dataset, self._description, matrices, original_hashes = d["dataset"], d["description"], d["matrices"], d["original_hashes"]
        if self._hashes:
            if self._hashes != original_hashes:
                raise Exception(
                    f"Provided hashes f{self._hashes} differs from hashes of file content: " f"{original_hashes}!")
        else:
            self._hashes = original_hashes

        return Root.update(self, **matrices)

    @cached_property
    def dataset(self):
        if self._hashes is None:
            _ = self.data  # force file reading
        return self._dataset

    @cached_property
    def description(self):
        if self._hashes is None:
            _ = self.data  # force file reading
        return self._description

    @cached_property
    def hashes(self):
        if self._hashes is None:
            _ = self.data  # force calculation of hashes
        return self._hashes

    def parameters(self):
        return self._config()
