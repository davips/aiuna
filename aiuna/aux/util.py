from typing import Union, Tuple, Any


class _meta(type):
    def __getattr__(self, item):
        return lambda x: x.__getattribute__(item)


class _(metaclass=_meta):
    def __class_getitem__(cls, item):
        return lambda x: x[item]


def flatten(lst):
    return [item for sublist in lst for item in sublist]
