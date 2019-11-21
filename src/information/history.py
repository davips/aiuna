from information.encoders import uuid


class History:
    def __init__(self, transformations):
        """
        Immutable history of transformations.
        :param transformations: list of transformations
        """

        # Add lazy cache for uuid
        self._uuid = None
        self.transformations = transformations

    def uuid(self):
        """
        Lazily calculated unique identifier for this history.
        :return: unique identifier
        """
        if self._uuid is None:
            uuids = ""
            for transf in self.transformations:
                uuids = uuids + uuid(transf)
            self._uuid = uuid(uuids.encode())
        return self._uuid
