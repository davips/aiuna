import _pickle as pickle
import os
import traceback
from glob import glob
from pathlib import Path
from typing import Optional

from pjdata.types import Data

from cururu.disk import save, load
from cururu.persistence import (
    Persistence,
    LockedEntryException,
    FailedEntryException,
    DuplicateEntryException,
    UnlockedEntryException,
)


class PickleServer(Persistence):
    def __init__(self, db="/tmp/cururu", compress=True):
        self.db = db
        self.compress = compress
        if not Path(db).exists():
            os.mkdir(db)

    def _fetch_impl(self, data: Data, lock: bool = False) -> Optional[Data]:
        # TODO: deal with fields and missing fields?
        filename = self._filename("*", data)

        # Not started yet?
        if not Path(filename).exists():
            print('W: Not started.', filename)
            if lock:
                print("W: Locking...", filename)
                Path(filename).touch()
            return None

        # Locked?
        if Path(filename).stat().st_size == 0:
            print("W: Previously locked by other process.", filename)
            raise LockedEntryException(filename)

        transformed_data = self._load(filename)

        # Failed?
        if transformed_data.failure is not None:
            raise FailedEntryException(transformed_data.failure)

        return transformed_data

    def store(self, data, check_dup=True):
        """The dataset name of data_out will be the filename prefix for
        convenience."""

        # TODO: reput name on Data?
        filename = self._filename("", data)
        # filename = self._filename(data.name, data, training_data_uuid)

        # sleep(0.020)  # Latency simulator.

        # Already exists?
        if check_dup and Path(filename).exists():
            raise DuplicateEntryException("Already exists:", filename)

        locked = self._filename("", data)
        if Path(locked).exists():
            os.remove(locked)

        self._dump(data, filename)

    def list_by_name(self, substring, only_original=True):  # TODO: take advantage of lazy data, instead of using hollow
        datas = []
        path = self.db + f"/*{substring}*-*.dump"
        for file in sorted(glob(path), key=os.path.getmtime):
            data = self._load(file)
            if only_original and data.history.size == 1:
                datas.append(data.hollow(tuple()))
        return datas

    def fetch_matrix(self, id):
        raise NotImplementedError

    def _filename(self, prefix, data):
        zip = "compressed" if self.compress else ""
        # Not very efficient.  TODO: memoize extraction of fields from JSON?
        # uuids = [json.loads(tr)['uuid'][:6] for tr in data.history]
        # rest = f"-".join(uuids) + f".{zip}.dump"
        rest = f"{data.id}.{zip}.dump"
        if prefix == "*":
            query = self.db + "/*" + rest
            lst = glob(query)
            if len(lst) > 1:
                raise Exception("Multiple files found:", query, lst)
            if len(lst) == 1:
                return lst[0]
            else:
                return self.db + "/" + rest
        else:
            return self.db + "/" + prefix + rest

    def _load(self, filename):
        """
        Retrieve a Data object from disk.
        :param filename: file dataset
        :return: Data
        """
        try:
            if self.compress:
                return load(filename)
            else:
                f = open(filename, "rb")
                res = pickle.load(f)
                f.close()
                return res
        except Exception as e:
            traceback.print_exc()
            print("Problems loading", filename)
            exit(0)

    def _dump(self, data, filename):
        """
        Dump a Data object to disk.
        :param data: Data
        :param filename: file dataset
        :return: None
        """
        print("W: Storing...", filename)
        if self.compress:
            save(filename, data)
        else:
            f = open(filename, "wb")
            pickle.dump(data, f)
            f.close()

    def unlock(self, data, training_data_uuid=""):
        filename = self._filename("*", data, training_data_uuid)
        if not Path(filename).exists():
            raise UnlockedEntryException("Cannot unlock something that is not " "locked!", filename)
        print("W: Unlocking...", filename)
        os.remove(filename)
