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
from akangatu.transf.dataindependentstep_ import DataIndependentStep_
import numpy as np


class Let(DataIndependentStep_):
    def __init__(self, field, value):
        super().__init__(field=field, value=value)
        self.field = field
        if isinstance(value, (list, np.ndarray)):
            self.value = value
        elif isinstance(value, (float, int)):
            self.value = np.array([[value]])
        else:
            raise Exception("Unknown value type", type(value))

    # TODO accept and store any kind of value in Data, not only 2d ndarrays (and str lists)

    # TODO if it is not jsonable or it is larger than 250 (utf8) chars,
    #    raises exception saying to use Set instead, which will md5-hash it

    def _process_(self, data):
        dic = {self.field: lambda: self.value}
        return data.update(self, **dic)
