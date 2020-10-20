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

from transf.absdata import AbsData
from transf.dataindependentstep_ import DataIndependentStep_
import numpy as np

class Let(DataIndependentStep_):
    isclass = True
    isoperator = False

    def __init__(self, field, value):
        super().__init__(field=field, value=value)
        self.field = field
        self.value = np.array([[value]])

    # TODO accept and store any kind of value in Data, not only 2d ndarrays (and str lists)

    # TODO if it is not jsonable or it is larger than 250 (utf8) chars,
    #        raises exception saying to use Set instead, which will md5-hash it

    def _process_(self, data: AbsData):
        dic = {self.field: self.value}
        return data.replace(self, **dic)
