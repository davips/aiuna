from information.encoders import uuid


class Dataset:
    def __init__(self, name, description, **fields):
        """
        Metadata of original datasets.
        :param name: name of the dataset (preferably concatenated with the
        hash of its data to avoid conflicting names)
        :param description: purpose of the dataset
        :param fields: a dictionary explaining the attributes of each field:
        {'I': 'image',
         'X': {'weight':'float', 'heigth':'float'},
         'Y': ['gender']}
        """

        # Add lazy cache for uuid
        self._uuid = None
        self.name = name
        self.description = description

    def uuid(self):
        """
        Lazily calculated unique identifier for this dataset.
        :return:
        """
        if self._uuid is None:
            self._uuid = uuid(self.name.encode())
        return self._uuid
