from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Optional

import pjdata.mixin.linalghelper as li
import pjdata.transformer as tr
import pjdata.types as t
from pjdata.mixin.identifiable import Identifiable
from pjdata.mixin.printable import Printable


class Content(Identifiable, Printable, ABC):
    """Parent class of all transformable content objects, like Data and Collection.

    short-lived-TODO: confirmar com Edesio se a largura da documentação se adequa automaticamente ao browser."""

    @property
    @abstractmethod
    def isfrozen(self):
        """Whether this Content object is closed for new transformations."""

    @property
    @abstractmethod
    def failure(self):
        """The pipeline failure that resulted in this Content object, if any.."""

    @property
    @abstractmethod
    def ishollow(self):
        """The pipeline failure that resulted in this Content object, if any.."""

    def transformedby(self, transformer: tr.Transformer):
        """Return this Content object transformed by func.

        Return itself if it is frozen or failed."""
        if self.isfrozen or self.failure:
            return self
        result = transformer.func(self)
        return result.updated(transformers=(transformer,))

    def updated(self: t.DataOrColl,
                transformers: Tuple[tr.Transformer, ...],
                failure: Optional[str] = 'keep',
                frozen: t.Status = 'keep',
                hollow: t.Status = 'keep',  # TODO: dirty/outdated_history
                **fields
                ) -> t.DataOrColl:
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
        transformations
            TODO.
        fields
            Matrices or vector/scalar shortcuts to them.

        Returns
        -------
        New Data object (it keeps references to the old one for performance).
        """
        if failure == 'keep':
            failure = self.failure
        if frozen == 'keep':
            frozen = self.isfrozen is True
        if hollow == 'keep':
            hollow = self.ishollow is True

        matrices = self.matrices.copy()
        matrices.update(li.LinAlgHelper.fields2matrices(fields))

        # klass can be Data or Collection.
        from pjdata.content.specialdata import NoData
        from pjdata.content.data import Data
        klass = Data if self is NoData else self.__class__
        return klass(
            history=tuple(self.history) + tuple(transformers),
            failure=failure, frozen=frozen, hollow=hollow, # outdated_history=True,  <==  TODO
            storage_info=self.storage_info, **matrices
        )
