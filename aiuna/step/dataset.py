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
from functools import cached_property

import numpy as np
from pandas import Categorical
from sklearn import datasets

from aiuna.content.creation import new, translate_type
from aiuna.content.root import Root
from akangatu.transf.dataindependentstep_ import DataIndependentStep_


class Dataset(DataIndependentStep_):
    def __init__(self, name="iris"):
        """
        Fetches/loads datasets from sklearn (for now):
        boston
        breast_cancer
        diabetes
        load_digits
        iris
        linnerud
        wine

        olivetti_faces
        20newsgroups
        20newsgroups_vectorized
        lfw_people
        lfw_pairs
        covtype
        rcv1
        kddcup99
        california_housing

        :param config:
        """
        super().__init__(name=name)
        if hasattr(datasets, "load_" + name):
            self.loader = getattr(datasets, "load_" + name)
        elif hasattr(datasets, "fetch_" + name):
            self.loader = getattr(datasets, "fetch_" + name)
        else:
            raise Exception("Unknown", name)

    def _process_(self, data):
        if data is not Root:
            msg = f"{self.name} only accepts Root as Data. Use Dataset(...).data or Sink instead {type(data)}"
            raise Exception(msg)
        return self.data

    @cached_property
    def data(self):
        d = self.loader(as_frame=True)
        classes = list(map(str, d.target_names))
        X, y = d.data.to_numpy(), np.array([str(l) for l in Categorical.from_codes(d.target, classes)])
        Xd, Yd = d.feature_names, [d.target.name]
        Xt, Yt = [translate_type(str(c)) for c in d.frame.dtypes], [classes]
        return new(X=X, y=y, Xd=Xd, Yd=Yd, Xt=Xt, Yt=Yt)

    def _uuid_(self):  # override uuid to match with New and File
        return self.data.step_uuid
