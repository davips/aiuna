from encoding.encoders import unpack_object, pack_object
from storage.persistence import Persistence, LockedEntryException, \
    FailedEntryException, DuplicateEntryException
import _pickle as pickle
from pathlib import Path


class PickledFile(Persistence):
    def __init__(self, optimize='speed', db='/tmp/'):
        self.db = db
        self.speed = optimize == 'speed' # vs 'space'

    def store(self, data, fields):
        file = data.uuid + '.dump'

        # Already exists?
        if Path(file).exists():
            raise DuplicateEntryException

        self._dump(data, file)

    def fetch(self, data, fields, transformation=None, lock=False):
        transformed_data_stub = data.updated(transformation)
        file = transformed_data_stub.uuid + '.dump'

        # Not started yet?
        if not Path(file).exists():
            print('W: Not started.', file)
            if lock:
                print('W: Locking...', file)
                Path(file).touch()
            return None

        # Locked?
        if Path(file).stat().st_size == 0:
            print('W: Previously locked by other process.', file)
            raise LockedEntryException

        transformed_data = self._load(file)

        # Failed?
        if transformed_data.failure is not None:
            raise FailedEntryException

        return transformed_data

    def _load(self, file):
        """
        Retrieve a Data object from disk.
        :param file: file name
        :return: Data
        """
        f = open(self.db + file, 'rb')
        if self.speed:
            return pickle.load(f)
        else:
            return unpack_object(f.read())

    def _dump(self, data, file):
        """
        Dump a Data object to disk.
        :param data: Data
        :param file: file name
        :return: None
        """
        f = open(self.db + file, 'wb')
        if self.speed:
            pickle.dump(data, f)
        else:
            f.write(pack_object(data))
            f.close()