import json

from cruipto.uuid import UUID
from transf.ditransf import DITransf_


class File_(DITransf_):
    def __init__(self, name, path, hashes):
        self._partial_config = {"name": name, "path": path}
        self.hashes = hashes

    def _transform_(self, data):
        raise Exception(f"File_ class is intended for internal use only, when reading ARFFs.")

    def _config_(self):
        config = self._partial_config
        config["hashes"] = self.hashes
        return config

    def _uuid_(self):  # override [to exclude file name/path from identity]
        return UUID(json.dumps({"name": self.name, "path": self.context, "hashes": self.hashes}, ensure_ascii=False, sort_keys=True).encode())
