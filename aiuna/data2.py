from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from pjdata.abc.abstractdata import AbstractData
from pjdata.aux.compression import pack
from pjdata.aux.uuid import UUID
from pjdata.mixin.linalghelper import LinAlgHelper
from pjdata.mixin.printable import Printable


def evolve(uuid, transformations):
    for transformation in transformations:
        uuid *= transformation.uuid
    return uuid


# Terminology:
# history -> Data events since birth
# transformations -> new Data events, or from some point in history
#  (both are lists of Transformers)
#
# matrix -> 2D numpy array
# field -> matrix, vector or scalar  (numpy views for easy handling)

class Data2(AbstractData, LinAlgHelper, Printable):
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

    def __init__(self, history, failure, frozen, **fields):
        super().__init__(jsonable=fields)
        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO: what to do with extra info? 'name' and 'desc'?
        #  Do they go to another arg or to a matrix? Are they necessary?

        self.history = history
        self.failure = failure
        self.isfrozen = frozen
        self._fields = fields

        # Convert fields to matrices.
        self._matrices = {}
        for name, value in fields.items():
            self._matrices[name.upper()] = self._convert(value)

        # Complement fields with matrices.
        self._fields.update(self._matrices)

        # Calculate UUIDs.
        self._uuid, self.uuids = self._evolve(history, self._matrices)

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

        # klass can be Data or Collection.
        klass = Data2 if self is NoData else self.__class__
        return klass(
            history=self.history + transformations,
            failure=failure, frozen=frozen, **fields
        )

    @property
    @lru_cache()
    def frozen(self):
        """Acredito que frozen possa fazer três papéis:
            1- pipeline precoce (p. ex. após SVM.enhance)
            2- pipeline falho (após exceção)
            3- mockup p/ ser preenchido e descongelado pelo cururu
         """
        return self.updated(transformations=[], frozen=True)

    def field(self, name, component=None):
        """Safe access to a field, with a friendly error message."""
        name = self._remove_unsafe_prefix(name)

        # Check existence of the field.
        if name not in self._fields:
            comp = component.name if 'name' in dir(component) else component
            raise MissingField(
                f'\n\nLast transformation:\n{self.history[-1]} ... \n'
                f' Data object <{self}>...\n'
                f'...last transformed by '
                f'{self.history[-1] and self.history[-1].name} does not '
                f'provide field {name} needed by {comp} .\n'
                f'Available fields: {list(self._fields.keys())}')

        # Fetch from storage if needed.
        if isinstance(self._fields[name], UUID):
            raise NotImplementedError

        return self._fields[name]

    @property
    @lru_cache()
    def Xy(self):
        return self.field('X'), self.field('y')

    @property
    def allfrozen(self):
        return False

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

        print('just curious...', item)
        return super().__getattribute__(item)

    def _evolve_identity(self, transformations, new_matrices=None):
        """Return this object's UUID/UUIDs after transformations."""
        if new_matrices is None:
            new_matrices = self.matrices

        # Update matrix UUIDs.
        uuids = self.uuids.copy()
        for name, value in new_matrices.items():
            # If it is a new matrix, assign a UUID for its birth.
            # TODO:
            #  Evaluate performance of using pack(X) as identity here:
            #  having a start identical to that of data_creation seems good,
            #  but can be slow.
            #  It avoids different UUIDs for the same content.
            #  A faster/dirtier choice would be data.uuid*matrix_name as birth.
            muuid = self.uuids.get(
                name, UUID(pack(value))
                # name, self.uuid * UUID(bytes(name, 'latin1'))
            )

            # Transform UUID.
            muuid = evolve(muuid, transformations)
            uuids[name] = muuid

        # Update UUID.
        uuid = evolve(self.uuid, transformations)

        return uuid, uuids


class MissingField(Exception):
    pass










class TSumm(TReduce):
    """Given a field, summarizes a Collection object to a Data object.
    The resulting Data object will have only the 's' field. To keep other
    fields, consider using a Keep containing all the concurrent part:
    Keep(Expand -> ... -> Summ).
    The collection history will be exported to the summarized Data object.
    The cells of the given field (matrix) will be averaged across all data
    objects, resulting in a new matrix with the same dimensions.
    """

    def __init__(self, field='R', function='mean', **kwargs):
        super().__init__(self._to_config(locals()),
                         deterministic=True, **kwargs)
        self.field = field

    def _enhancer_impl(self, step='e'):
        def func(collection):
            if collection.has_nones:
                raise Exception(
                    "Warning: You shuld use 'Shrink()' to handling collections "
                    "with None. ")

            data = NoData.updated(
                collection.history,
                failure=collection.failure,
                **collection.original_data.matrices
            )

            if not self.prior and step == 'e':
                return data

            if not self.posterior and step == 'm':
                return data

            res = self.function(collection)
            if isinstance(res, tuple):
                summ = numpy.array(res)
                return data.updated(self.transformations(step), S=summ)
            else:
                return data.updated(self.transformations(step), s=res)
        return TTransformer(func=func)

    def _modeler_impl(self, prior, step='m'):
        return self._enhancer_impl(step)

    # TODO: Não parece interessante reescrever o enhancer e o modeler aqui!
    # Uma solução é o summary detectar se existe ou não o field, se existir ele
    # faz a operação se não existir ele apenas sumariza.
    @lru_cache()
    def enhancer(self):
        return self._enhancer_impl()

    @lru_cache()
    def modeler(self, prior):
        return self._modeler_impl(prior)

    @classmethod
    def _cs_impl(cls):
        params = {
            'function': CatP(choice, items=cls.function_from_name.keys()),
            'field': CatP(choice, items=['z', 'r', 's'])
        }
        return TransformerCS(Node(params))

    def _fun_mean(self, collection):
        return mean([data.field(self.field, self) for data in collection],
                    axis=0)

    def _fun_std(self, collection):
        return std([data.field(self.field, self) for data in collection],
                   axis=0)

    def _fun_mean_std(self, collection):
        # TODO?: optimize calculating mean and stdev together
        values = [data.field(self.field, self) for data in collection]
        if len(values[0].shape) == 2:
            if values[0].shape[0] > 1:
                raise Exception(
                    f"Summ doesn't accept multirow fields: {self.field}\n"
                    f"Shape: {values[0].shape}")
            values = [v[0] for v in values]
        return mean(values, axis=0), std(values, axis=0)