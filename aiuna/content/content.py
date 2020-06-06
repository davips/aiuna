from abc import ABC, abstractmethod

from pjdata.mixin.identifiable import Identifiable
from pjdata.mixin.printable import Printable


class Content(Identifiable, Printable, ABC):
    """Parent class of all transformable content objects, like Data and Collection.

    short-lived-TODO: confirmar com Edesio se a largura da documentação se adequa automaticamente ao browser."""

    @abstractmethod
    @property
    def isfrozen(self):
        """Whether this Content object is closed for new transformations."""
