from collections.abc import MutableMapping


class Lazies(MutableMapping):
    """Expose values of a dict as they were being called.

    See https://stackoverflow.com/a/3387975/9681577 about extending dicts."""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[key]()

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)
