#  Copyright (c) 2020. Davi Pereira dos Santos
#      This file is part of the aiuna project.
#      Please respect the license. Removing authorship by any means
#      (by code make up or closing the sources) or ignoring property rights
#      is a crime and is unethical regarding the effort and time spent here.
#      Relevant employers or funding agencies will be notified accordingly.
#
#      aiuna is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      aiuna is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with aiuna.  If not, see <http://www.gnu.org/licenses/>.
#


from aiuna.content.root import Root
from transf.dataindependentstep_ import DataIndependentStep_


class New(DataIndependentStep_):
    def __init__(self, hashes, **matrices):
        super().__init__(hashes=hashes)
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
