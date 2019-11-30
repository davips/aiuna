from abc import ABC, abstractmethod


class Persistence(ABC):
    """
    This class stores and recovers results from some place.
    The children classes are expected to provide storage in e.g.:
     SQLite, remote/local MongoDB, MySQL server, pickled or even CSV files.
    """

    @abstractmethod
    def store(self, data, fields, check_dup=True):
        """
        :param data: Data to store
        :param fields: list of names of the matrices to store
        :param check_dup: whether to waste time checking duplicates
        :return: None
        :exception DuplicateEntryException
        """
        pass

    @abstractmethod
    def fetch(self, data, fields, transformation=None, lock=False):
        """
        :param data: Data object before being transformed by a Pipeline or a
        string indicating the dataset of a dataset that suffered no transformations
        :param fields: list of names of the matrices to fetch
        :param transformation: Tuple (Pipeline, operation) containing a
        list of transformers and the stage of transformation 'a':apply; 'u':use
        :param lock: whether to mark entry (input data and pipeline combination)
                        as locked, when no data is found for the entry
        :return: Data or None
        :exception LockedEntryException, FailedEntryException
        """
        pass

    @abstractmethod
    def list_by_name(self, substring):
        """
        Convenience method to retrieve a list of currently stored Data
        objects by name.
        :param substring: part of the name to look for
        :return: list of empty Data objects, i.e. without matrices
        """
        pass

class LockedEntryException(Exception):
    """Another node is generating output data for this input data
    and transformation combination."""


class FailedEntryException(Exception):
    """This input data and transformation combination have already failed before."""


class DuplicateEntryException(Exception):
    """This input data and transformation combination have already been inserted
    before."""
