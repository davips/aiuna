from storage.persistence import Persistence


class Amnesia(Persistence):
    def store(self, data, fields):
        return None

    def fetch(self, data, fields, pipeline=None, lock=False):
        return None
