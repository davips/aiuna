from pjdata.aux.identifyable import Identifyable


class History(Identifyable):
    def __init__(self, transformations):
        """
        Immutable history of transformations.
        :param transformations: list of transformations
        """
        self.transformations = transformations
        self.last = self.transformations and self.transformations[-1]

    def extended(self, transformation):
        return History(self.transformations + [transformation])

    def _uuid_impl(self):
        uuids = ""
        for transf in self.transformations:
            uuids = uuids + transf.uuid
        return uuids

    def __str__(self):
        return '\n'.join(list(map(str, self.transformations)))
