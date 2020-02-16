from functools import lru_cache

from pjdata.aux.encoders import uuid
from pjdata.aux.identifyable import Identifyable
from pjdata.mixin.printable import Printable


class History(Identifyable, Printable):
    def __init__(self, transformations):
        """
        Immutable history of transformations.
        :param transformations: list of transformations
        """
        super().__init__(jsonable=transformations)
        self.transformations = transformations
        self.size = len(self.transformations)
        if self.size == 0:
            # print('Empty history!')
            self.last = None
        else:
            self.last = self.transformations[-1]

    def extended(self, transformation):
        if not isinstance(transformation, list):
            transformation = [transformation]
        return History(self.transformations + transformation)

    def _uuid_impl(self):
        uuids = ""
        for transf in self.transformations:
            uuids = uuids + transf.uuid
        return uuids

    @property
    @lru_cache()
    def id(self):
        """Non unique identifier.

        Similar to as uuid except that it does not consider which training
        data was used in apply step.

        Useful for checking consistency between expected and actual
        transformations."""
        ids = ""
        for transf in self.transformations:
            ids = ids + transf.transformer_uuid
        return uuid(ids.encode())

    def __getitem__(self, item):
        return self.transformations[item]
