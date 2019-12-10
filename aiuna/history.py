from pjdata.aux.identifyable import Identifyable


class History(Identifyable):
    def __init__(self, transformations):
        """
        Immutable history of transformations.
        :param transformations: list of transformations
        """
        self.transformations = transformations

    def _uuid_impl(self):
        uuids = ""
        for transf in self.transformations:
            uuids = uuids + transf.uuid()
        return uuids
