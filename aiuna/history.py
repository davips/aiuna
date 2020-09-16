from __future__ import annotations

import json
from functools import lru_cache
from typing import List, Union

import pjdata.transformer.transformer as tr
from pjdata.aux.util import Property
from pjdata.mixin.printing import withPrinting


class Leaf(withPrinting):
    isleaf = True

    def __init__(self, transformer: Union[str, tr.Transformer]):
        self.transformer = transformer

    def _jsonable_impl(self):
        return self.transformer.jsonable


class History(withPrinting):
    isleaf = False

    def __init__(self, transformers: List[Union[str, tr.Transformer]], nested=None):
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
            yield node.transformer
        else:
            for tup in node.nested:
                yield from self.traverse(tup)

    def _findlast(self, node) -> str:
        # TODO: remove recursion due to python conservative limits for longer histories (AL, DStreams, ...)
        if node.isleaf:
            return node.transformer
        else:
            # print(node.nested)
            return self._findlast(node.nested[-1])

    def __iter__(self):
        yield from self.traverse(self)

    @Property
    def clean(self):
        """Clean version of history. Only the names (of real transformations)."""
        for transformer in self:
            if not transformer.ispholder:
                yield transformer

    def __xor__(self, attrname):
        return list(map(lambda x: x.__dict__[attrname], self.traverse(self)))  # TODO: memoize json?
