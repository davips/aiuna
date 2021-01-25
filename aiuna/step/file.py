#  Copyright (c) 2020. Davi Pereira dos Santos
#  This file is part of the aiuna project.
#  Please respect the license - more about this in the section (*) below.
#
#  aiuna is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  aiuna is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with aiuna.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.
#
#  aiuna is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  aiuna is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with aiuna.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.


import inspect
import json
from functools import cached_property
from aiuna.content.root import Root
from aiuna.content.creation import read_arff, new
from aiuna.step.new import New
from akangatu.transf.dataindependentstep_ import DataIndependentStep_


class File(DataIndependentStep_):
    def __init__(self, name="iris.arff", path="./", hashes=None):
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
            raise Exception(f"{self.name} only accepts Root as Data. Use File(  ).data or Sink instead.", type(data))
        return self.data

    def _config(self):
        config = self._partial_config
        config["hashes"] = self.hashes
        return config

    def _uuid_(self):  # override uuid because default uuid is based on config, which includes unreliable args
        return New(hashes=self.hashes).uuid

    # REMINDER File cannot be lazy, since it depends on file content to know the uuid which will be used to generate
    # the lazy Data object.
    ###@cached_property
    @property
    def data(self):
        d = read_arff(self.filename)
        ds = d["dataset"], d["description"], d["matrices"], d["original_hashes"]
        self._dataset, self._description, matrices, original_hashes = ds
        if self._hashes:
            if self._hashes != original_hashes:
                raise Exception(
                    f"Provided hashes f{self._hashes} differs from hashes of file content: " f"{original_hashes}!")
        else:
            self._hashes = original_hashes

        return new(**matrices)

    ###@cached_property
    @property
    def dataset(self):
        if self._hashes is None:
            _ = self.data  # force file reading
        return self._dataset

    ###@cached_property
    @property
    def description(self):
        if self._hashes is None:
            _ = self.data  # force file reading
        return self._description

    ###@cached_property
    @property
    def hashes(self):
        if self._hashes is None:
            _ = self.data  # force calculation of hashes
        return self._hashes

    def parameters(self):
        return self._config()

    def __call__(self, *args, **kwargs):
        return File(*args, **kwargs)

    # def _context_(self):
    #     return "aiuna.step.file"


file = File()
# TODO: autocomplete vai funcionar para args dos callable?

# TODO: forçar implementação do __call__ em vez de __init__?
