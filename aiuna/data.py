import json
from functools import lru_cache

from pjdata.abc.abstractdata import AbstractData
from pjdata.aux.compression import pack
from pjdata.aux.customjsonencoder import CustomJSONEncoder
from pjdata.aux.uuid import UUID
from pjdata.config import Global
from pjdata.mixin.linalghelper import LinAlgHelper
from pjdata.mixin.printable import Printable


# Terminology:
# history -> Data events since birth
# transformations -> new Data events, or from some point in history
#  (both are lists of Transformers)
#
# matrix -> 2D numpy array
# field -> matrix, vector or scalar  (numpy views for easy handling)

class Data(AbstractData, LinAlgHelper, Printable):
    """Immutable data for all machine learning scenarios one can imagine.

    Attributes
    ----------
    fields
        A dictionary, like {X: <numpy array>, Y: <numpy array>}.
        Matrix names should start with an uppercase letter and
        have at most two letters.
    fields
        Shorcuts 'matrices', but seeing each column-vector matrix as a vector
        and each single element matrix as a scalar.

    Parameters
    ----------
    fields
        A dictionary like {X: <numpy array>, Y: <numpy array>}.
        Matrix names should have a single uppercase character, e.g.:
        X=[
           [23.2, 35.3, 'white'],
           [87.0, 52.7, 'brown']
        ]
        Y=[
           'rabbit',
           'mouse'
        ]
        They can be, ideally, numpy arrays (e.g. storing is optimized).
        A matrix name followed by a 'd' indicates its description, e.g.:
        Xd=['weight', 'height', 'color']
        Yd=['class']
        A matrix name followed by a 't' indicates its types ('ord', 'int',
        'real', 'cat'*).
        * -> A cathegorical/nominal type is given as a list of nominal values:
        Xt=['real', 'real', ['white', 'brown']]
        Yt=[['rabbit', 'mouse']]
    """

    def __init__(self, history, failure, frozen, storage_info=None,
                 **matrices):
        super().__init__(jsonable=matrices)
        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO: what to do with extra info? 'name' and 'desc'?
        #  Do they go to another arg or to a matrix? Are they necessary?

        self.history = history
        self.failure = failure
        self.isfrozen = frozen
        self.ismelting = frozen is Melting
        self.storage_info = storage_info
        self.matrices = matrices

        # Calculate UUIDs.
        self._uuid, self.uuids = self._evolve_id(UUID(), {}, history, matrices)

    def updated(self, transformations, failure='keep', frozen: bool = 'keep',
                **fields):
        """Recreate or freeze a Data object with updated matrices, history and
        failure.

        Parameters
        ----------
        frozen
            Where the resulting Data object should be frozen.
        transformations
            List of Transformation objects.
        failure
            The failure caused by the given transformations, if it failed.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous failures
        fields
            Changed/added matrices and updated values.
        transformations
            History object of transformations.

        Returns
        -------
        New Data object (it keeps references to the old one for performance).
        """
        from pjdata.specialdata import NoData

        if failure == 'keep':
            failure = self.failure
        if frozen == 'keep':
            frozen = self.isfrozen

        matrices = self.matrices.copy()
        matrices.update(self._fields2matrices(fields))

        # klass can be Data or Collection.
        klass = Data if self is NoData else self.__class__
        return klass(
            history=tuple(self.history) + transformations, failure=failure,
            frozen=frozen, storage_info=self.storage_info, **matrices
        )

    @property
    @lru_cache()
    def frozen(self):
        """frozen faz dois papéis:
            1- pipeline precoce (p. ex. após SVM.enhance)
            2- pipeline falho (após exceção)
        um terceiro papel não pode ser feito por ele, pois frozen é uma
        propriedade armazenável de Data:
            3- hollow = mockup p/ ser preenchido pelo cururu
         """
        return self.updated(transformations=tuple(), frozen=True)

    @lru_cache()
    def melting(self, transformations):
        """temporary frozen (only Persistence can melt it)         """
        # noinspection PyTypeChecker
        return self.updated(transformations=transformations, frozen=Melting)

    @lru_cache()
    def field(self, name, component='undefined'):
        """Safe access to a field, with a friendly error message."""
        name = self._remove_unsafe_prefix(name)
        mname = name.upper() if len(name) == 1 else name

        # Check existence of the field.
        if mname not in self.matrices:
            comp = component.name if 'name' in dir(component) else component
            raise MissingField(
                f'\n\nLast transformation:\n{self.history[-1]} ... \n'
                f' Data object <{self}>...\n'
                f'...last transformed by '
                f'{self.history[-1] and self.history[-1].name} does not '
                f'provide field {name} needed by {comp} .\n'
                f'Available matrices: {list(self.matrices.keys())}')

        m = self.matrices[mname]

        # Fetch from storage if needed.
        if isinstance(m, UUID):
            if self.storage_info is None:
                raise Exception('Storage not set! Unable to fetch ' + m.id)
            print('>>>> fetching field', name, m.id)
            self.matrices[mname] = m = self._fetch_matrix(m.id)

        if not name.islower():
            return m

        if name in ['r', 's']:
            return self._mat2sca(m)

        if name in ['y', 'z']:
            return self._mat2vec(m)

    @property
    @lru_cache()
    def Xy(self):
        return self.field('X'), self.field('y')

    @property
    def allfrozen(self):
        return False

    @property
    @lru_cache()
    def matrix_names(self):
        return list(self.matrices.keys())

    @property
    @lru_cache()
    def ids_lst(self):
        return [self.uuids[name].id for name in self.matrix_names]

    @property
    @lru_cache()
    def ids_str(self):
        return ','.join(self.ids_lst)

    @property
    @lru_cache()
    def history_str(self):
        return ','.join(transf.uuid.id for transf in self.history)

    @lru_cache()
    def field_dump(self, name):
        """Lazily compressed matrix for a given field.
        Useful for optimized persistence backends for Cache."""
        return pack(self.field(name))

    @property
    @lru_cache()
    def matrix_names_str(self):
        return ','.join(self.matrix_names)

    @lru_cache()
    def _fetch_matrix(self, id):
        if self.storage_info is None:
            raise Exception(f'There is no storage set to fetch {id})!')
        return Global['storages'][self.storage_info].fetch_matrix(id)

    def _remove_unsafe_prefix(self, item):
        """Handle unsafe (i.e. frozen) fields."""
        if item.startswith('unsafe'):
            return item[6:]

        if self.isfrozen:
            raise Exception('Cannot access fields from Data objects that come '
                            f'from a failed pipeline!\nHINT: use unsafe{item}.'
                            f'\nHINT2: probably an ApplyUsing is missing, '
                            f'around a Predictor.')
        return item

    def _uuid_impl(self):
        return self._uuid

    def __getattr__(self, item):
        """Create shortcuts to fields, still passing through sanity check."""
        if item == 'Xy':
            return self.Xy
        if 0 < (len(item) < 3 or item.startswith('unsafe')):
            return self.field(item, '[direct access through shortcut]')

        # print('just curious...', item)
        return super().__getattribute__(item)


class MissingField(Exception):
    pass


class Melting(type):
    pass
