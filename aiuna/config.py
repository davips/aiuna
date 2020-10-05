import json
from contextlib import contextmanager
from multiprocessing import Lock as PLock
from threading import Lock as TLock

# Some global state, so we need to make it thread-safe; with a context manager.
threadLock = TLock()
processLock = PLock()


@contextmanager
def safety():
    with threadLock, processLock:
        yield



try:
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    CONFIG = {}

CACHE = {}


def globalcache(method):  # TODO: make it LRU
    def wrapper(step, data):
        # global CACHE
        key = step.id + data.id
        if key in CACHE:
            return CACHE[key]
        CACHE[key] = method(step, data)
        return CACHE[key]

    return wrapper
