from pjdata.aux.identifyable import Identifyable


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


class NoDataset(type):
    name = 'NoDataset'
    from pjdata.aux.encoders import int2tiny
    uuid = 'N' + int2tiny(0)

    def __new__(cls, *args, **kwargs):
        raise Exception(
            'NoDataset is a singleton and shouldn\'t be instantiated')
