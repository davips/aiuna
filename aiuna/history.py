from functools import cached_property

from aiuna.leaf import Leaf
from transf.mixin.printing import withPrinting


class History(withPrinting):
    isleaf = False

    def __init__(self, steps, nested=None):
        """Optimized iterable "list" of Leafs (wrapper for a step or a dict) based on structural sharing."""
        self.nested = nested or list(map(Leaf, steps))

    @cached_property
    def last(self):
        return self._findlast(self)

    def aslist(self):
        return [step.asdict for step in self]

    def _asdict_(self):
        return {step.id: step.desc for step in self}

    def __add__(self, other):
        return History([], nested=[self, other])

    def __lshift__(self, steps):
        if steps:
            return History([], nested=[self, History(steps)])
        return self

    def traverse(self, node):
        # TODO: remove recursion due to python conservative limits for longer histories (AL, DStreams, ...)
        if node.isleaf:
            yield node.step
        else:
            for tup in node.nested:
                yield from self.traverse(tup)

    def _findlast(self, node) -> str:
        # TODO: remove recursion due to python conservative limits for longer histories (AL, DStreams, ...)
        if node.isleaf:
            return node
        else:
            # print(node.nested)
            return self._findlast(node.nested[-1])

    def __iter__(self):
        yield from self.traverse(self)

    def __xor__(self, attrname):
        """Shortcut ^ to get an attribute along all steps."""
        # touch properties to avoid problems (is this really needed?)
        void = [a.name + a.longname for a in self.traverse(self)]
        return list(map(lambda x: getattr(x, attrname), self.traverse(self)))
