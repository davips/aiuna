# data
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


def new():
    # TODO: create Data from matrices
    raise NotImplementedError


class Data(AbsData, withPrinting):
    """Immutable lazy data for most machine learning scenarios.

    Parameters
    ----------
    history
        A History objects that represents a sequence of Transformations objects.
    failure
        The reason why the workflow that generated this Data object failed.
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

        Volatile fields, i.e., those that are not a deterministic result,
        should be marked with the mutability suffix '_m' like in t_m (for time);
        so they stay outside matrix, but still available as Data attributes.
    """

    _Xy = None

    def __init__(self, uuid, uuids, history, hollow=False, stream=None, target="s,r", storage_info=None, inner=None, **matrices):
        # target: Fields precedence when comparing which data is greater.
        self._jsonable = {"uuid": uuid, "uuids": uuids}

        # Move mutable fields from matrices to self.
        for k in list(matrices.keys()):
            if k.endswith("_m"):
                self.__dict__[k] = matrices.pop(k)

        # Put interesting fields inside representation for printing; and mark them as None if needed.
        if "failure" in matrices:
            self.failure = self._jsonable["failure"] = matrices["failure"]
        else:
            self.failure = None
        if "timeout" in matrices:
            self.timeout = self._jsonable["timeout"] = matrices["timeout"]
            if self.timeout and all(st.isntTimeout for st in step):
                print("Cannot set timeout")
        else:
            self.timeout = None

        if hollow:
            self._jsonable["hollow"] = hollow
        if target:
            self._jsonable["target"] = target
        if storage_info:
            self._jsonable["storage_info"] = storage_info
        if inner:
            self._jsonable["inner"] = inner
        if matrices:
            self._jsonable["matrices"] = ", ".join(matrices.keys())

        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO:        #  2- mark volatile fields?        #  3- dna property?        #  4- task?
        self.target = target.split(",") if isinstance(target, str) else target
        self.history = history
        self._hollow = hollow
        self.stream = stream
        self._target = [field for field in self.target if field.upper() in matrices]
        self.storage_info = storage_info
        self.matrices = matrices
        self._uuid, self.uuids = uuid, uuids
        self._inner = inner

    def replace(self, step: Union[Step, List[Step]], inner: Optional[AbsData] = "keep", stream: Union[str, Iterator] = "keep", **fields):
        """Recreate an updated Data object.

        Parameters
        ----------
        steps
            List of Step objects that transforms this Data object.
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
        :param inner:
        :param step:
        :param stream:
        """
        return self._replace(step, inner=inner, stream=stream, **fields)

    # TODO:proibir mudança no inner, exceto por meio do step Inner
    def _replace(self, step, hollow: bool = "keep", stream="keep", inner: Optional[AbsData] = "keep", **fields):
        step = step if isinstance(step, list) else [step]
        if isinstance(self, Picklable) and step:
            raise Exception("Picklable history cannot be updated!")
        history = self.history or History([])
        if step:
            history = history << step
        hollow = self.ishollow if hollow == "keep" else hollow
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

        kw = {"hollow": hollow, "stream": stream, "storage_info": self.storage_info}
        from aiuna.content.specialdata import Root
        klass = Data if self is Root else self.__class__
        return klass(uuid, uuids, history, **kw, inner=inner, **matrices)

    def timed(self, t):
        return self._replace([], t_m=t)

    def failed(self, step, failure):
        return self._replace(step, failure=failure)

    @cached_property
    def eager(self):
        """Touch every lazy field.

        Stream is kept intact"""
        for k, v in self.matrices.items():
            if callable(v):
                self.matrices[k] = v()
        return self

    @lru_cache()
    def hollow(self, step):
        """Create a temporary hollow Data object (only Persistence can fill it).
        Notice: uuid is changed."""
        return self._replace(step, hollow=True)

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
        name = self._remove_unsafe_prefix(name, context)
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
            raise Exception("Unexpected lower letter:", m, "requested by", comp)

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

    @property
    def ishollow(self):
        return self._hollow

    @lru_cache()
    def _fetch_matrix(self, id):
        if self.storage_info is None:
            raise Exception(f"There is no storage set to fetch: {id})!")
        return 22222222222  # STORAGE_CONFIG['storages'][self.storage_info].fetch_matrix(id)

    def _remove_unsafe_prefix(self, item, step="undefined"):
        """Handle unsafe (i.e. failed data with) fields."""
        if item.startswith('unsafe'):
            # User knows what they are doing.
            return item[6:]

        if self.failure or self.timeout or self.ishollow:
            print(f"Step {step} cannot access fields ({item}) from Data objects that come from a "
                  f"failed/timedout/hollow pipeline! HINT: use unsafe{item}. \n"
                  f"HINT2: To calculate training accuracy the 'train' Data should be inside the 'test' tuple; use Copy "
                  f"for that."
                  )
            if self.failure:
                print("failed", self.failure)
            if self.timeout:
                print("timeout")
            if self.ishollow:
                print("hollow")

        return item

    def _uuid_(self):
        return self._uuid

    def _inner_(self):
        return self._inner

    def __getattr__(self, item):
        """Create shortcuts to fields, still passing through sanity check."""
        # if item == "Xy":
        #     return self.Xy
        if 0 < (len(item) < 3 or item.startswith('unsafe')):
            return self.field(item, context="[direct access through shortcut]")

        # print('getting attribute...', item)
        return super().__getattribute__(item)

    def __lt__(self, other):
        """Amenity to ease pipeline result comparisons. 'A > B' means A is better than B."""
        for name in self._target:
            return self.field(name, context="[comparison between Data objects 1]") < other.field(name, context="[comparison between Data objects 2]")
        return Exception("Impossible to make comparisons. None of the target fields are available:", self.target)

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
        newdata = Picklable(self.uuid, self.uuids, history, self.ishollow,
                            stream=None, target=self.target, storage_info=self.storage_info, inner=inner, **self.matrices)
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
        return Data(self.uuid, self.uuids, history, self.ishollow, stream, self.target, self.storage_info, inner, **self.matrices)


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
