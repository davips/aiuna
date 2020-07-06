from dataclasses import dataclass
from typing import List

from pjdata.transformer.transformer import Transformer


@dataclass
class Leaf:
    transformer: Transformer
    isleaf = True

    def __str__(self):
        return self.transformer


class History:
    isleaf = False

    def __init__(self, transformers: List[Transformer], nested=None):
        """Optimized iterable based on structural sharing."""
        self.nested = nested or list(map(Leaf, transformers))

    def __add__(self, other):
        return History([], nested=[self, other])

    def __lshift__(self, transformers):
        return History([], nested=[self, History(transformers)])

    def traverse(self, node):
        # TODO: remove recursion due to python conservative limits for longer histories (AL, DStreams, ...)
        if node.isleaf:
            yield node.transformer
        else:
            for tup in node.nested:
                yield from self.traverse(tup)

    def __iter__(self):
        yield from self.traverse(self)

    def clean(self):
        for transformer in self:
            if not transformer.ispholder:
                yield transformer

    def __str__(self):
        return '§[' + ', '.join(map(str, self.clean)) + ']'
