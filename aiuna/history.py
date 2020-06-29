from typing import Tuple

import pjdata.transformer.transformer as tr
from pjdata.aux.util import _
from pjdata.mixin.printing import withPrinting


class History(withPrinting):
    def __init__(self, *args, tuples: Tuple[tr.Transformer, ...] = None):
        """Optimized tuple based on structural sharing. Ref: https://stackoverflow.com/a/62423033/9681577"""
        self.tuples = args if tuples is None else tuples
        self.size = sum(map(len, self.tuples))

    def extend(self, transformations: tuple):
        return History(tuples=self.tuples + (transformations,))

    def __iter__(self):
        for tup in self.tuples:
            for item in tup:
                yield item

    def __getitem__(self, index):
        if index >= self.size:
            raise IndexError
        for tup in self.tuples:
            if index > len(tup):
                index -= len(tup)
            else:
                return tup[index]

    def __len__(self):
        return self.size

    def _jsonable_impl(self):
        # TODO: create a method for dirty history
        return '§[' + ', '.join(map(str, self)) + ']'
