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


from akangatu.transf.step import Step


class Leaf:
    """Contains a step or a dict, answers for both."""
    isleaf, _dict, _step = True, None, None

    def __init__(self, step):
        if isinstance(step, dict):
            self._dict = step
        else:
            self._step = step

    @property
    def asstep(self):
        if self._step is None:
            self._step = Step.fromdict(self._dict)
        # self._step = self._step() if lazy(self._step) else self._step
        return self._step

    @property
    def asdict(self):
        if self._dict is None:
            self._dict = self._step.asdict
        return self._dict

    def __getattr__(self, item):
        if item in ["asstep", "asdict"]:
            return super().__getattribute__(item)
        return getattr(self.asstep, item)

    def __getitem__(self, item):
        return self.asdict[item]

    def _asdict_(self):
        return self._dict
