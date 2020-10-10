import json
import traceback
from functools import lru_cache, cached_property
from typing import Union, Iterator, List, Optional

import arff
import numpy as np

from aiuna.compression import pack
from aiuna.history import History
from aiuna.mixin.linalghelper import fields2matrices, evolve_id, mat2vec
from cruipto.uuid import UUID
from transf.absdata import AbsData
from transf.customjson import CustomJSONEncoder, CustomJSONDecoder
from transf.mixin.printing import withPrinting
from transf.step import Step


# TODO: iterable data like dict
class Data(AbsData, withPrinting):
    """Immutable lazy data for most machine learning scenarios.

    Parameters
    ----------
    history
        A History objects that represents a sequence of Transformations objects.
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

        Volatile fields, i.e., those that can be lost due to their nondeterministic nature,
        should be marked with the mutability suffix '_m' like in 't_m' (for time) or 'step_m' (for current step);
        so they stay outside matrix, but still available as Data attributes.
        They are not stored by conventional storages.
        User-content enabled ones like OkaSt may provide that.
    """

    _Xy = None
    metafields = ["failure", "timeout", "comparable"]

    def __init__(self, uuid, uuids, history, stream=None, storage_info=None, inner=None, **matrices):
        # comparable: Fields precedence when comparing which data is greater.
        self._jsonable = {"uuid": uuid, "uuids": uuids}

        # Move mutable fields from matrices to self.
        for k in list(matrices.keys()):
            if k.endswith("_m"):
                self.__dict__[k] = matrices.pop(k)

        # Put interesting fields inside representation for printing; and mark them as None if needed.
        if storage_info:
            self._jsonable["storage_info"] = storage_info
        if inner:
            self._jsonable["inner"] = inner
        if matrices:
            self._jsonable["matrices"] = ",".join(matrices.keys())
        if "failure" in matrices:
            self.failure = self._jsonable["failure"] = matrices["failure"]
        else:
            self.failure = None
            uuids["failure"] = UUID()
            matrices["failure"] = None  # TODO: None significa semfalha, então objeto Error() significaria nãoobtido nesse e em outros campos

        if "timeout" in matrices:
            self.timeout = self._jsonable["timeout"] = matrices["timeout"]
        else:
            self.timeout = None
            uuids["timeout"] = UUID()
            matrices["timeout"] = None

        if "comparable" in matrices:
            self.comparable = self._jsonable["comparable"] = matrices["comparable"]
        else:
            self.comparable = ""
            uuids["comparable"] = UUID()
            matrices["comparable"] = []

            # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO:        #  2- mark volatile fields?        #  3- dna property?        #  4- task?
        self.history = history
        self.stream = stream
        self._comparable = [field for field in self.comparable if field.upper() in matrices]
        self.storage_info = storage_info
        self.matrices = matrices
        self._uuid, self.uuids = uuid, uuids
        self._inner = inner

    def update(self, step: Union[Step, List[Step]], inner: Optional[AbsData] = "keep", stream: Union[str, Iterator] = "keep", **fields):
        """Recreate an updated Data object.

        Parameters
        ----------
        steps
            List of Step objects that transforms this Data object.
        fields
            Matrices or vector/scalar shortcuts to them.
        stream
            Iterator that generates Data objects.

        Returns
        -------
        New Content object (it keeps references to the old one for performance).
        :param inner:
        :param step:
        :param stream:
        """
        return self._update(step, inner=inner, stream=stream, **fields)

    # TODO:proibir mudança no inner, exceto por meio do step Inner
    def _update(self, step, stream="keep", inner: Optional[AbsData] = "keep", **fields):
        if "timeout" in fields:
            if step.isntTimeout:
                print("Only Timeout step can set timeout, not", step.longname)
                exit()
        step = step if isinstance(step, list) else [step]
        if len(step) == 0 and any(not s.endswith("_m") for s in step):
            print("Empty list of steps is not allowed when nonvolatile (i.e. immutable) fields are present:", list(fields.keys()))
            exit()
        if isinstance(self, Picklable) and step:
            raise Exception("Picklable history cannot be updated!")
        history = self.history or History([])
        if step:
            history = history << step
        stream = self.stream if stream == "keep" else stream
        inner = self.inner if isinstance(inner, str) and inner == "keep" else inner

        # Only update matrix uuids for the provided and changed ones!
        matrices = self.matrices.copy()
        changed_matrices = {}
        for k, v in fields2matrices(fields).items():
            if (k not in matrices) or matrices[k] is not v:
                changed_matrices[k] = v
        matrices.update(changed_matrices)
        uuid, uuids = evolve_id(self.uuid, self.uuids, step, changed_matrices)

        from aiuna.content.root import Root
        klass = Data if self is Root else self.__class__
        return klass(uuid, uuids, history, stream=stream, storage_info=self.storage_info, inner=inner, **matrices)

    @cached_property
    def eager(self):
        """Touch every lazy field.

        Stream is kept intact"""
        for k, v in self.matrices.items():
            if callable(v):
                self.matrices[k] = v()
        return self

    @lru_cache()
    def field(self, name, block=False, context="undefined"):
        """
        Safe access to a field, with a friendly error message.

        Parameters
        ----------
        name
            Name of the field.
        block
            Whether to wait for the value or to raise FieldNotReady exception if it is not readily available.
        context
            Scope hint about origin of the problem.

        Returns
        -------
        Matrix, vector or scalar
        """
        # TODO: better organize this code
        if name in self.metafields:
            return self.matrices[name]
        mname = name.upper() if len(name) == 1 else name

        # Check existence of the field.
        # for a in self.history:
        #     print(a.name)
        if mname not in self.matrices:
            comp = context.name if "name" in dir(context) else context
            print(
                # f"\n\nLast transformation:\n{self.history.last} ... \n"
                f" Data object <{self.uuid}>...last transformed by "
                f"\n{self.history ^ 'longname'}\n does not provide field {name} needed by {comp} .\nAvailable matrices: {list(self.matrices.keys())}")
            # raise MissingField
            exit()

        m = self.matrices[mname]

        # Fetch from storage?...
        if isinstance(m, UUID):
            if self.storage_info is None:
                comp = context.name if "name" in dir(context) else context
                raise Exception("Storage not set! Unable to fetch " + m.id, "requested by", comp)
            print(">>>> fetching field:", name, m.id)
            self.matrices[mname] = m = self._fetch_matrix(m.id)

        # TODO: make all Steps lazy (to enable use with fields produced by and inside streams?
        # Fetch previously deferred value?...
        if callable(m):
            if block:
                raise NotImplementedError("Waiting of values not implemented yet!")
            self.matrices[mname] = m = m()
            # pprint(self.__dict__, indent=2)  # HINT: list all content from an object

        # Just return formatted according to capitalization...
        if not name.islower():
            return m
        elif name in ["r", "s"]:
            return mat2vec(m)
        elif name in ["y", "z"]:
            return mat2vec(m)
        elif name in ["p"]:
            return mat2vec(m)
        else:
            comp = context.name if "name" in dir(context) else context
            raise Exception("Unexpected lower letter:", name, "requested by", comp)

    @cached_property
    def Xy(self):
        if self._Xy is None:
            self._Xy = self.field("X"), self.field("y")
        return self._Xy

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
        if isinstance(self.history, History):
            return ",".join(transf.id for transf in self.history)
        return ",".join(self.history.keys())

    @lru_cache()
    def field_dump(self, name):
        """Cached compressed matrix for a given field.
        Useful for optimized persistence backends for Cache (e.g. more than one backend)."""
        return pack(self.field(name, context="[dump]"))

    @property
    @lru_cache()
    def matrix_names_str(self):
        return ','.join(self.matrix_names)

    @lru_cache()
    def _fetch_matrix(self, id):
        if self.storage_info is None:
            raise Exception(f"There is no storage set to fetch: {id})!")
        return 22222222222  # STORAGE_CONFIG['storages'][self.storage_info].fetch_matrix(id)

    def _uuid_(self):
        return self._uuid

    def _inner_(self):
        return self._inner

    def __getattr__(self, item):
        """Create shortcuts to fields, still passing through sanity check."""
        # if item == "Xy":
        #     return self.Xy
        if len(item) < 3 or item in self.metafields:
            return self.field(item, context="[direct access through shortcut]")

        if item.endswith("_pd"):
            name = item[:-3]
            if name.upper() not in self.matrices:
                print(f"Field {name} not found when trying to convert it to pandas. Available ones:", self.matrix_names)
                exit()
            name = name.upper()
            from pandas import DataFrame
            desc = name + "d"
            if desc in self.matrices:
                return DataFrame(self.matrices[name], columns=self.matrices[desc])
            else:
                return DataFrame(self.matrices[name])

        # print('getting attribute...', item)
        return super().__getattribute__(item)

    def __lt__(self, other):
        """Amenity to ease pipeline result comparisons. 'A > B' means A is better than B."""
        for name in self._comparable:
            return self.field(name, context="[comparison between Data objects 1]") < other.field(name, context="[comparison between Data objects 2]")
        return Exception("Impossible to make comparisons. None of the comparable fields are available:", self.comparable)

    def __eq__(self, other):
        # Checks removed for speed (isinstance is said to be slow...)
        # from aiuna.content.specialdata import Root
        # if other is not Root or not isinstance(other, Data):  # TODO: <-- check for other types of Data?
        #     return False
        return other is not None and self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)

    @lru_cache
    def arff(self, relation, description):
        Xt = [untranslate_type(typ) for typ in self.Xt]
        Yt = [untranslate_type(typ) for typ in self.Yt]
        dic = {
            "description": description,
            "relation": relation,
            "attributes": list(zip(self.Xd, Xt)) + list(zip(self.Yd, Yt)),
            "data": np.column_stack((self.X, self.Y)),
        }
        try:
            return arff.dumps(dic)
        except:
            traceback.print_exc()
            print("Problems creating ARFF")
            print("Types:", Xt, Yt)
            print("Sample:", self.X[0], self.Y[0])
            print("Expected sizes:", len(Xt), "+", len(Yt))
            print("Real sizes:", len(self.X[0]), "+", len(self.Y[0].shape))
            exit(0)

    def _jsonable_(self):
        return self._jsonable

    @cached_property
    def picklable(self) -> AbsData:
        """Remove unpicklable parts."""
        return self.picklable_()[0]

    @cached_property
    def unpicklable(self) -> AbsData:
        """Restore unpicklable parts."""
        return self.unpicklable_([{}])

    # noinspection PyDefaultArgument
    def picklable_(self, unpicklable_parts=[]):
        """Remove unpicklable parts, but return them together as a list of dicts, one dict for each nested inner objects."""
        if isinstance(self, Picklable):
            return self, unpicklable_parts
        unpicklable_parts = unpicklable_parts.copy()
        # REMINDER: use json here because it traverse into internal steps, and the str form will be needed anyway by SQL storages
        history = {step.id: json.dumps(step, sort_keys=True, ensure_ascii=False, cls=CustomJSONEncoder) for step in self.history}
        unpicklable_parts.append({"stream": self.stream})
        if self.inner:
            inner, unpicklable_parts = self.inner.picklable_(unpicklable_parts)
        else:
            inner = None
        newdata = Picklable(self.uuid, self.uuids, history, stream=None, storage_info=self.storage_info, inner=inner, **self.matrices)
        return newdata.eager, unpicklable_parts

    def unpicklable_(self, unpicklable_parts):
        """Rebuild an unpicklable Data.

        History is desserialized, if given as str.
        """
        # REMINDER: Persistence/threading actions can be nested, so self can be already unpicklable
        if not isinstance(self, Picklable):
            return self
        if self.stream:
            raise Exception("Inconsistency: this picklable Data object contains a stream!")
        # make a copy, since we will change history and stream directly; and convert to right class
        stream = unpicklable_parts and "stream" in unpicklable_parts[0] and unpicklable_parts[0]["stream"]
        if not isinstance(self.history, dict):
            raise Exception("Pickable Data should have a dict instead of", type(self.history))
        lst = [json.loads(stepstr, cls=CustomJSONDecoder) for stepstr in self.history.values()]
        history = History(lst)
        inner = self.inner and self.inner.unpicklable
        return Data(self.uuid, self.uuids, history, stream, self.storage_info, inner, **self.matrices)

    def __rlshift__(self, other):
        if other.isclass:
            other = other()
        return other.process(self)

    def __rshift__(self, other):
        if other.isclass:
            other = other()
        return other.process(self)

    def __add__(self, other):
        # se mexeram na mesma matriz, vale a segunda.
        # Dá pra emendar com o histórico da segunda, desde que o uuid final seja recalculado e que
        # operações de ajuste (Copy) preservem as matrizes pedidas pela segunda no inicio da divergencia (normalmente após File/New).
        # Assume que haver matrizes extra não altera resultado de um step (o que é sensato, pois step não deve fazer "inspection")
        # se foi misto,
        raise Exception("Not implemented: should solve conflicts to merge history of two data objects.")

    def __delitem__(self, key):
        # record destruction where needed
        from aiuna.delete import Del
        d = Del(field=key) << self
        self._uuid = d.uuid
        self.history = d.history

        # make destruction
        del self.uuids[key]
        del self.matrices[key]

        # REMINDER: invalidation not needed according to tests, I guess it is per instance
        # # invalidate all caches
        # for method in self.__dict__.values():
        #     if callable(method) and hasattr(method, "cacheclear"):
        #         method.cacheclear()

    # * ** - @
    # & | ^ // %
    # -d +d ~
    # REMINDER: the detailed History is unpredictable, so it is impossible to provide a useful plan() based on future steps
    # def plan(self, step):
    #     step = step if isinstance(step, list) else [step]


class MissingField(Exception):
    pass


def untranslate_type(name):
    if isinstance(name, list):
        return name
    if name in ["real", "int"]:
        return "NUMERIC"
    else:
        raise Exception("Unknown type:", name)


class Picklable(Data):
    """This class avoid the problem of an unpicklable Data and its picklable incarnation having the same hash.
    [Despite being _eq_uals]."""

    def __hash__(self):
        return -1 * self.uuid.n  # TODO check if this is correct, and if it is really needed
