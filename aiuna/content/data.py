# data
import json
import traceback
from functools import lru_cache, cached_property
from typing import Optional, TYPE_CHECKING, Iterator, Union, Literal, Dict, List

import arff

from pjdata.mixin.identification import withIdentification
from pjdata.mixin.printing import withPrinting

import pjdata.aux.compression as com
import pjdata.aux.uuid as u
import pjdata.mixin.linalghelper as li
import pjdata.transformer.transformer as tr
from pjdata.aux.util import Property
from pjdata.config import STORAGE_CONFIG
import pjdata.history as h
import numpy as np


def new():
    # TODO: create Data from matrices
    raise NotImplementedError


class Data(withIdentification, withPrinting):
    """Immutable lazy data for most machine learning scenarios.

    Parameters
    ----------
    history
        A History objects that represents a sequence of Transformations objects.
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

    _Xy = None

    def __init__(self, uuid=u.UUID.identity, uuids=None, history=h.History([]), failure=None, frozen=False, hollow=False, stream=None, target="s,r", storage_info=None, historystr=None, trdata=None, **matrices):
        # target: Fields precedence when comparing which data is greater.
        if uuids is None:
            uuids = {}
        if historystr is None:
            historystr = []
        self._jsonable = {"uuid": uuid, "history": history, "uuids": uuids}
        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO:
        #  1- 'name' and 'desc'
        #  2- volatile fields
        #  3- dna property?
        #  4- task?

        self.target = target.split(",")
        self.history = history
        self._failure = failure
        self._frozen = frozen
        self._hollow = hollow
        self.stream = stream
        self._target = [field for field in self.target if field.upper() in matrices]
        self.storage_info = storage_info
        self.matrices = matrices
        self._uuid, self.uuids = uuid, uuids
        self.historystr = historystr
        self.trdata = trdata

    def _jsonable_impl(self):
        return self._jsonable

    def replace(self, transformers, truuid=u.UUID.identity, failure="keep", frozen="keep", stream="keep", trdata="keep", **fields):
        """Recreate an updated Data object.

        Parameters
        ----------
        frozen
        transformers
            List of Transformer objects that transforms this Data object.
        failure
            Updated value for failure.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous
             failures
        fields
            Matrices or vector/scalar shortcuts to them.
        stream
            Iterator that generates Data objects.

        Returns
        -------
        New Content object (it keeps references to the old one for performance).
        :param trdata:
        :param transformers:
        :param stream:
        :param frozen:
        :param failure:
        :param truuid:
        """
        if not isinstance(transformers, list):
            transformers = [transformers]
        if failure == "keep":
            failure = self.failure
        if frozen == "keep":
            frozen = self.isfrozen
        if stream == "keep":
            stream = self.stream
        if isinstance(trdata, str):
            trdata = self.trdata
        matrices = self.matrices.copy()
        matrices.update(li.fields2matrices(fields))

        uuid, uuids = li.evolve_id(self.uuid, self.uuids, transformers, matrices, truuid)

        # noinspection Mypy
        if self.history is None:
            self.history = h.History([])
        return Data(
            history=self.history << transformers,
            failure=failure,
            frozen=frozen,
            hollow=self.ishollow,
 
