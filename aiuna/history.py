from dataclasses import dataclass
from functools import lru_cache
from typing import List

from pjdata.aux.util import Property
from pjdata.mixin.printing import withPrinting
from pjdata.transformer.transformer import Transformer


class Leaf(withPrinting):
    isleaf = True

    def __init__(self, transformer: Transformer):
        self.transformer_astext = transformer.serialized

    def _jsonable_impl(self):
        return self.transformer_astext


class History(withPrinting):
    isleaf = False

    def __init__(self, transformers: List[Transformer], nested=None):
        """Optimized iterable based on structural sharing."""
        self.nested = nested or list(map(Leaf, transformers))
        # if len(self.nested)==0:
        #     raise Exception

    @Property
    def last(self):
        return self._findlast(self)

    @lru_cache()
    def _jsonable_impl(self):
        return list(self.clean)

    def __add__(self, other):
        return History([], nested=[self, other])

    def __lshift__(self, transformers):
        if transformers:
            return History([], nested=[self, History(transformers)])
        return self

    def traverse(self, node):
        # TODO: remove recursion due to python conservative limits for longer histories (AL, DStreams, ...)
        if node.isleaf:
            yield node.transformer_astext
        else:
            for tup in node.nested:
                yield from self.traverse(tup)

    def _findlast(self, node):
        # TODO: remove recursion due to python conservative limits for longer histories (AL, DStreams, ...)
        if node.isleaf:
            return node.transformer_astext
        else:
            print(node.nested)
            return self._findlast(node.nested[-1])

    def __iter__(self):
        yield from self.traverse(self)

    @Property
    def clean(self):
        for transformer_astext in self:
            if 'PHolder' not in transformer_astext:
                yield transformer_astext
