from aiuna.mixin.identifyable import Identifyable
from aiuna.mixin.printable import Printable


class Dataset(Identifyable, Printable):
    def __init__(self, name, description):
        """
        Metadata of original datasets.
        :param name: name of the dataset (preferably concatenated with the
        hash of its data to avoid conflicting names)
        :param description: purpose of the dataset
        """
        super().__init__(jsonable={'name': name, 'description': description})
        self.name = name
        self.description = description

    def _uuid_impl(self):
        return self.name


class NoDataset(type):
    name = 'NoDataset'
    from cruipto.encoders import int2tiny
    def __new__(cls, *args, **kwargs):
        raise Exception(
            'NoDataset is a singleton and shouldn\'t be instantiated')
