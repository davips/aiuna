from abc import ABC, abstractmethod
from functools import lru_cache


class Identifyable(ABC):
    @property
    @lru_cache()
    def uuid00(self):
        """Lazily calculated unique identifier for this dataset.

        Should be accessed direct as a class member: 'uuid'.

        Returns
        -------
            A unique identifier UUID object.
        """
        from pjdata.aux.encoders import uuid00, UUID
        content = self._uuid_impl00()
        if isinstance(content, UUID):
            return content
        else:
            return uuid00(content.encode())

    @property
    @lru_cache()
    def sid(self):
        """
        Short uuID
        First 8 chars of uuid, usually for printing purposes.
        First collision expect after 12671943 combinations.
        :return:
        """
        return self.uuid00.pretty[:8]

    @abstractmethod
    def _uuid_impl00(self):
        """Specific internal calculation made by each child class.

        Should return a string or a UUID object to be used directly."""
        pass
