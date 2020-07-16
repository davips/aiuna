from __future__ import annotations

from functools import lru_cache
from inspect import signature
from typing import Dict, Any, Callable


class Info:
    def __init__(self, items: Dict[str, Any] = None, **kwargs):
        if items is None:
            items = kwargs
        # TODO:
        #   convert iterator items, e.g. 'models' to 'models' and 'imodels'.
        #  This allows the user to access a list before any iteration or even after the iterator is exhausted.
        #  Memory management is already done by lru in each model individually,
        #  so keeping the references is not a burden.

        # Convert zero-arity function items to cached properties.
        lazies = {k: v for k, v in items.items() if callable(v) and not signature(v).parameters}
        _ = [items.pop(k) for k in lazies]
        self._add_lazy_attr(lazies)

        self.__dict__.update(items)

        # Create shortcuts for subtransformers.
        if "enhancers" in items:
            self.transformers = items["enhancers"]
        elif "models" in items:
            self.transformers = items["models"]
        else:
            self.transformers = []

    def _add_lazy_attr(self, lazies: Dict[str, Callable[[], Any]]):
        """Attach prop_fn to instance with name prop_name.
        Assumes that prop_fn takes self as an argument.
        Reference: https://stackoverflow.com/a/1355444/509706

        Alert: Despite having the same class name and all being descendants of the original Info,
        the instances patched by this method will have different classes!
        E.g.
            isinstance(a, Info) -> True
            isinstance(b, Info) -> True
            but
            isinstance(a, type(b)) -> False
        """
        klass = self.__class__
        lazy_props = {k: property(lru_cache(f)) for k, f in lazies.items()}
        child_class = type(klass.__name__, (klass,), lazy_props)
        self.__class__ = child_class
