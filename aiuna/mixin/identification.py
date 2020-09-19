# ident

from abc import ABC, abstractmethod
from functools import cached_property

from cruipto.uuid import UUID


class withIdentification(ABC):
    """ Identifiable mixin. """
    @cached_property
    def name(self):
        return self._name_impl()

    @abstractmethod
    def _name_impl(self):
        pass

    # cannot use lru for uuid() because we are overriding data._hash_ with uuid --->>> loop
    _uuid = None

    @property  # see comment above
    def uuid(self) -> UUID:
        """Lazily calculated unique identifier for this dataset.

        Should be accessed direct as a class member: 'uuid'.

        Returns
        -------
            A unique identifier UUID object.
        """
        if self._uuid is None:
            content = self._uuid_impl()
            self._uuid = content if isinstance(content, UUID) else UUID(content.encode())
        return self._uuid

    @cached_property
    def id(self):
        """
        Short uuID
        First 8 chars of uuid, usually for printing purposes.
        First collision expect after 12671943 combinations.
        :return:
        """
        return self.uuid.id

    @cached_property
    def sid(self):
        """
        Short uuID
        First 6 chars of uuid, usually for printing purposes.
        :return:
        """
        return self.id[:6]

    @abstractmethod
    def _uuid_impl(self):
        """Specific internal calculation made by each child class.

        Should return a string or a UUID object to be used directly."""
