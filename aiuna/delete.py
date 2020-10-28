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


from aiuna.content.data import Data
from cruipto.uuid import UUID
from transf.dataindependentstep_ import DataIndependentStep_


class Del(DataIndependentStep_):
    def __init__(self, field):
        super().__init__(field=field)
        self.field = field

    def _process_(self, data):
        fields = data.field_funcs_m.copy()
        del fields[self.field]
        fields["changed"] = []

        uuids = data.uuids.copy()
        uuids["changed"] = UUID(b"[]")

        return Data(data.uuid, uuids, data.history << self, **fields)
