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

    def __str__(self):
        return '\n---\n'.join(
            list(map(str, self.transformations))
        )
