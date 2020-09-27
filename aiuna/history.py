from functools import lru_cache

from aiuna import config
from transf.mixin.printing import withPrinting

class Leaf(withPrinting):
    isleaf = True

    def __init__(self, step):
        self.step = step

    def _jsonable_(self):
        return self.step.jsonable


class History(withPrinting):
    isleaf = False

    def __init__(self, steps, nested=None):
        """Optimized iterable based on structural sharing."""
        self.nested = nested or list(map(Leaf, steps))
        # if len(self.nested)==0:
        #     raise Exception

    @property
    def last(self):
        return self._findlast(self)

    def _jsonable_(self):
        if config.SHORT_HISTORY:
            return list(self.clean)
        return list(self)

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
            return node.step
        else:
            # print(node.nested)
            return self._findlast(node.nested[-1])

    def __iter__(self):
        yield from self.traverse(self)

    @property
    def clean(self):
        """Clean version of history. Only the names (of real transformations)."""
        for step in self:

            # if not step.isnoop:
                yield step.longname

    def __xor__(self, attrname):
        return list(map(lambda x: x.__dict__[attrname], self.traverse(self)))  # TODO: memoize json?
