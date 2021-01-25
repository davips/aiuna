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

from garoupa.uuid import UUID

from aiuna.leaf import Leaf
from akangatu.transf.mixin.printing import withPrinting


class History(withPrinting):
    isleaf = False

    def __init__(self, step=None, nested=None, uuid=None):
        """Optimized iterable "list" of Leafs (wrapper for a step or a dict) based on structural sharing."""
        if step:
            if nested:
                raise Exception("History cannot be built from both 'step' and 'nested'!")
            self._last = step
            self.uuid = step.uuid
            self.nested = [Leaf(step)]
        elif nested:
            if uuid is None:
                raise Exception("History cannot be built from 'nested' without 'uuid'!")
            self._last = nested[-1].last
            self.uuid = uuid
            self.nested = nested
        else:
            self._last = None
            self.uuid = UUID.identity
            self.nested = []

    @property
    def id(self):
        return self.uuid.id

    @property
    def last(self):
        if self._last is None:
            raise Exception("Empty history has no last item.")
        return self._last

    ###@cached_property
    @property
    def aslist(self):
        return [step.asdict for step in self]

    def _asdict_(self):
        return {step.id: step.desc for step in self}

    def __add__(self, other):
        return History(nested=[self, other], uuid=self.uuid * other.uuid)

    def __lshift__(self, step):
        h = History(step)
        return History(nested=[self, h], uuid=self.uuid * h.uuid)

    def traverse(self, node):
        # TODO: remove recursion due to python conservative limits for longer histories (AL, DStreams, ...)
        if node.isleaf:
            yield node.asstep
        else:
            for tup in node.nested:
                yield from self.traverse(tup)

    def __iter__(self):
        yield from self.traverse(self)

    def __xor__(self, attrname):
        """Shortcut ^ to get an attribute along all steps."""
        # touch properties to avoid problems (is this really needed?)
        # void = [a.name + a.longname for a in self.traverse(self)]   #TODO voltar essa linha?
        return list(map(lambda x: getattr(x, attrname), self.traverse(self)))

    def __eq__(self, other):
        return self.uuid == other.uuid
