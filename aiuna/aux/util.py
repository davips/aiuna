from typing import Union, Tuple, Any


def flatten(lst):
    return [item for sublist in lst for item in sublist]
