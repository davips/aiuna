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


# global provisorio
import json

with open('config.json', 'r') as f:
    Global = json.load(f)
Global['default_dump'] = {'engine': 'dump'}
Global['default_sqlite'] = {'engine': 'sqlite'}
Global['storages'] = {}

# TODO: aproveitar gerenciador global do Edesio para embutir thread-safety.