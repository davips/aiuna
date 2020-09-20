from aiuna.creation import read_arff
import json
from functools import cached_property

from aiuna.content.data import Data
from aiuna.content.specialdata import NoData
from aiuna.history import History
from cruipto.uuid import UUID
from transf.ditransf import DITransf_


class File(DITransf_):
    def __init__(self, name, path="./", hashes=None):
        if not path.endswith("/"):
            print(path)
            raise Exception("Path should end with '/'", path)
        if name.endswith(".arff"):
            self._partial_config = {"name": name, "path": path}
            self.filename = path + name
        else:
            raise Exception("Unrecognized file extension:", name)
        self._hashes = hashes

    def _transform_(self, data):
        if data not in [NoData, None]:
            raise Exception(f"Transformer {self.name} only accepts NoData. Use Sink before it if needed.")
        return self.data

    def _config_(self):
        config = self._partial_config
        config["hashes"] = self.hashes
        return config

    def _uuid_(self):  # override uuid to exclude file name/path from identity
        return UUID(json.dumps({"name": self.name, "path": self.context, "hashes": self.hashes}, ensure_ascii=False, sort_keys=True).encode())

    # TODO: check all json dumps

    @cached_property
    def data(self):
        self._dataset, self._description, matrices, original_hashes = read_arff(self.filename)
        if self._hashes:
            if self._hashes != original_hashes:
                raise Exception(f"Provided hashes f{self._hashes} differs from hashes of file content: " f"{original_hashes}!")
        else:
            self._hashes = original_hashes

        return NoData.replace(self, **matrices)

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
