from abc import ABC, abstractmethod

from encoders import uuid


class Identifyable(ABC):
    _uuid = None  # lazy cache for uuid

    def uuid(self):
        """
        Lazily calculated unique identifier for this dataset.
        :return: unique identifier
        """
        if self._uuid is None:
            txt = self._uuid_impl()
            if isinstance(txt, tuple):
                txt, prefix = txt
                self._uuid = uuid(txt.encode(), prefix)
            else:
                self._uuid = uuid(txt.encode())
        return self._uuid

    def sid(self):
        """
        Short uuID
        First 10 chars of uuid for printing purposes.
        Max of 1 collision each 1048576 combinations.
        :return:
        """
        return self.uuid()[:10]

    @abstractmethod
    def _uuid_impl(self):
        """
        Specific internal calculation by each child class.
        return: (str-to-hash, prefix)
        """
        pass
