from functools import lru_cache, cached_property

from transf.serialization import serialize
from cruipto.uuid import UUID
from aiuna.mixin.serialization import WithSerialization


class FakeFile(WithSerialization):
    path = "pjml.tool.data.flow.file"

    def __init__(self, filename, original_hashes):
        clean = filename.replace(".ARFF", "").replace(".arff", "")
        split = clean.split("/")
        self.config = {
            "name": filename.split("/")[-1],
            "path": "/".join(split[:-1]) + "/",
            "hashes": original_hashes,
        }
        self.info_for_transformer = {"id": f"{self.name}@{self.path}", "config": self.config}
        self.jsonable = {"info": self.info_for_transformer, "enhance": True, "model": True}
        self.hasenhancer, self.hasmodel = True, True

    @cached_property
    def cfserialized(self):
        return serialize(self.info_for_transformer)

    def _cfuuid_impl(self, data=None):
        return UUID(serialize(self.config["hashes"]).encode())

    def _name_impl(self):
        return "File"

    def _uuid_impl(self):
        return UUID(self.serialized.encode())
