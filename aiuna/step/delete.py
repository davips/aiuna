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


from aiuna.content.data import Data
from garoupa.uuid import UUID
from akangatu.transf.dataindependentstep_ import DataIndependentStep_


class Del(DataIndependentStep_):
    def __init__(self, field):
        super().__init__(field=field)
        self.field = field

    def _process_(self, data):
        fields = data.field_funcs_m.copy()
        del fields[self.field]
        fields["changed"] = []

        uuids = data.uuids.copy()
        del uuids[self.field]
        uuids["changed"] = UUID(b"[]")

        return Data(data.uuid * self.uuid, uuids, data.history << self, **fields)
