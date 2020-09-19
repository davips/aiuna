import json

from cruipto.uuid import UUID
from transf.dataindependent import DataIndependent_


class File_(DataIndependent_):
    def __init__(self, name, path, hashes):
        self._partial_config = {"name": name, "path": path}
        self.hashes = hashes

    def _transform_(self, data):
        raise Exception(f"File_ class is intended for internal use only, when reading ARFFs.")

    def _config_(self):
        config = self._partial_config
        config["hashes"] = self.hashes
        return config

    def _uuid_(self):  # override uuid to exclude file name/path from identity
        return UUID(json.dumps(self.hashes).encode())
