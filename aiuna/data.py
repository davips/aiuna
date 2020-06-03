from functools import lru_cache
from typing import Any, Tuple, Optional, Union

from pjdata.aux.compression import pack
from pjdata.aux.uuid import UUID
from pjdata.config import STORAGE_CONFIG
from pjdata.mixin.identifyable import Identifyable
from pjdata.mixin.linalghelper import LinAlgHelper
from pjdata.mixin.printable import Printable
from pjdata.step.transformer import Transformer


class Data(Identifyable, LinAlgHelper, Printable):
    """Immutable lazy data for most machine learning scenarios.

    Parameters
    ----------
    history
        A tuple of Transformer objects.
    failure
        The reason why the workflow that generated this Data object failed.
    frozen
        Indicate wheter the workflow ended earlier due to a normal
        component behavior.
    hollow
        Indicate whether this is a Data object intended to be filled by
        Storage.
    storage_info
        An alias to a global Storage object for lazy matrix fetching.
    matrices
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

    def __init__(self, history: Tuple[Transformer],
                 failure: Optional[str],
                 frozen: Union[str, bool], hollow: Union[str, bool],
                 storage_info: Optional[str] = None,
                 **matrices):
        super().__init__(jsonable=matrices)
        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO:
        #  'name' and 'desc'
        #  volatile fields
        #  dna property?

        self.history = history
        self.failure = failure
        self.isfrozen = frozen
        self.ishollow = hollow
        self.storage_info = storage_info
        self.matrices = matrices

        # Calculate UUIDs.
        self._uuid, self.uuids = self._evolve_id(UUID(), {}, history, matrices)

    def updated(self, transformers: Tuple[Transformer],
                failure: Optional[str] = 'keep',
                frozen: Union[str, bool] = 'keep', hollow: Union[str, bool] = 'keep',
                **fields):
        """Recreate a updated, frozen or hollow Data object.

        Parameters
        ----------
        transformers
            List of Transformer objects that transforms this Data object.
        failure
            Updated value for failure.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous
             failures
        frozen
            Whether the resulting Data object should be frozen.
        hollow
            Indicate whether the provided transformers list is just a
            simulation, meaning that the resulting Data object is intended
            to be filled by a Storage.
        fields
            Matrices or vector/scalar shortcuts to them.

        Returns
        -------
        New Data object (it keeps references to the old one for performance).
        """

        from pjdata.specialdata import NoData

        if failure == 'keep':
            failure = self.failure
        if frozen == 'keep':
            frozen = self.isfrozen
        if hollow == 'keep':
            hollow = self.ishollow

        matrices = self.matrices.copy()
        matrices.update(self._fields2matrices(fields))

        # klass can be Data or Collection.
        klass = Data if self is NoData else self.__class__
        return klass(
            history=tuple(self.history) + tuple(transformations),
            failure=failure, frozen=frozen, hollow=hollow,
            storage_info=self.storage_info, **matrices
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
    def hollow(self: Any, transformations):
        """temporary hollow (only Persistence can fill it)         """
        return self.updated(transformations=transformations, hollow=True)

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

    def transformedby(self, func):
        """Return this Data object transformed by func.

        Return itself if it is frozen or failed."""
        if self.isfrozen or self.failure:
            return self
        return func(self)

    @lru_cache()
    def _fetch_matrix(self, id):
        if self.storage_info is None:
            raise Exception(f'There is no storage set to fetch {id})!')
        return STORAGE_CONFIG['storages'][self.storage_info].fetch_matrix(id)

    def _remove_unsafe_prefix(self, item):
        """Handle unsafe (i.e. frozen) fields."""
        if item.startswith('unsafe'):
            # User knows what they are doing.
            return item[6:]

        if self.failure or self.isfrozen or self.ishollow:
            raise Exception('Cannot access fields from Data objects that come '
                            f'from a failed/frozen/hollow pipeline!\n'
                            f'HINT: use unsafe{item}.'
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

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)

class MissingField(Exception):
    pass
