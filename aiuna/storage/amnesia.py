from storage.persistence import Persistence


class Amnesia(Persistence):
    def store(self, data, fields, check_dup=True):
        return None

    def fetch(self, data, fields, transformation=None, lock=False):
        return None
