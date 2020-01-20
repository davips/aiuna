from abc import ABC, abstractmethod
from functools import lru_cache

from pjdata.aux.encoders import uuid


class Identifyable(ABC):
    @property
    @lru_cache()
    def uuid(self):
        """Lazily calculated unique identifier for this dataset.

        Should be accessed direct as a class member: 'uuid'.

        Returns
        -------
            A unique identifier.
        """
        txt = self._uuid_impl()
        if isinstance(txt, tuple):
            prefix, txt = txt
            if prefix == 'uuid':
                return txt
            return uuid(txt.encode(), prefix=prefix)
        else:
            return uuid(txt.encode())

    @property
    @lru_cache()
    def sid(self):
        """
        Short uuID
        First 8 chars of uuid, usually for printing purposes.
        First collision expect after 12671943 combinations.
        :return:
        """
        return self.uuid[:8]

    @abstractmethod
    def _uuid_impl(self):
        """
        Specific internal calculation by each child class.
        return: (str-to-hash, prefix)
        """
        pass
