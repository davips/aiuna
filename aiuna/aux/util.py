from typing import Union, Tuple, Any

from compose import compose


class _meta(type):
    def __getattr__(self, item):
        return lambda x: x.__getattribute__(item)


class _(metaclass=_meta):
    """Shortcut for functional handling of iterables.
 
    _.m = apply map and convert to list (useful for easy printing while debugging)
    _ = item inside iterable (to provide as a function to map)
    Example:
        map(_[4], tuples)
        map(_('My class name applied for all new instances'), classes)
        _.m(_.id, users)
    """

    def __new__(cls, *args, **kwargs):
        return lambda x: x(*args, **kwargs)

    def __class_getitem__(cls, item):
        return lambda x: x[item]

    m = compose(list, map)


def flatten(lst):
    return [item for sublist in lst for item in sublist]
