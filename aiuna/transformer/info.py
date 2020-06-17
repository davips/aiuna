from __future__ import annotations

import typing
from typing import Dict, Any


class Info:
    def __init__(self, items: Dict[str, Any] = None, **kwargs):
        if items is None:
            items = kwargs
        # TODO: convert items with 'iter' suffix, e.g. 'models_iter' to 'models' and 'imodels'.
        #  This allows the user to access a list without iterating or even after the iterator is exhausted.
        #  Memory management is already done by lru in each model individually,
        #  so keeping the references is not a burden.
        print(items)
        self.__dict__.update(items)
