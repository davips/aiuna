from information.encoders import unpack_object, pack_object
from storage.persistence import Persistence, LockedEntryException, \
    FailedEntryException, DuplicateEntryException
import _pickle as pickle
from pathlib import Path
from glob import glob


class PickleServer(Persistence):
    def __init__(self, optimize='speed', db='/tmp/'):
        self.db = db
        self.speed = optimize == 'speed'  # vs 'space'

    def store(self, data, fields, check_dup=True):
        file = self.db + data.dataset.name + '-' + data.uuid() + '.dump'

        # Already exists?
        if check_dup and Path(file).exists():
            raise DuplicateEntryException

        self._dump(data, file)

    def fetch(self, data, fields, transformation=None, lock=False):
        transformed_data_stub = data.updated(transformation)
        file = self.db + data.dataset.name + '-' + \
               transformed_data_stub.uuid() + '.dump'

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

    def list_by_name(self, substring):
        datas = []
        for file in glob(self.db + f'*{substring}*-*.dump'):
            data = self._load(file)
            self._erase(data)
            datas.append(data)
        return datas

    def _load(self, file):
        """
        Retrieve a Data object from disk.
        :param file: file dataset
        :return: Data
        """
        f = open(file, 'rb')
        if self.speed:
            return pickle.load(f)
        else:
            return unpack_object(f.read())

    def _dump(self, data, file):
        """
        Dump a Data object to disk.
        :param data: Data
        :param file: file dataset
        :return: None
        """
        f = open(file, 'wb')
        if self.speed:
            pickle.dump(data, f)
        else:
            f.write(pack_object(data))
            f.close()

    def _erase(self, data):
        """
        Remove matrices from Data.
        Keep identity.
        :param data:
        :return:
        """
        matrices = []
        for arg in data.__dict__:
            if len(arg) == 1:
                matrices.append(arg)
        for mat in matrices:
            del data.__dict__[mat]

