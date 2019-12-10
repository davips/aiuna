from aux.identifyable import Identifyable


class Dataset(Identifyable):
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
        self.name = name
        self.description = description

    def _uuid_impl(self):
        return self.name

    def __str__(self):
        return f'{self.name} "{self.description}"'
