# data
import traceback
from functools import lru_cache, cached_property
from typing import Union, Iterator, List, Optional

import arff
import numpy as np
from aiuna.compression import pack

from aiuna.config import STORAGE_CONFIG
from aiuna.history import History
from aiuna.mixin.linalghelper import fields2matrices, evolve_id, mat2vec
from cruipto.uuid import UUID
from transf.absdata import AbsData
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
    """

    _Xy = None

    def __init__(self, uuid, uuids, history, failure=None, time=None, timeout=False, hollow=False, stream=None, target="s,r", storage_info=None, inner=None, **matrices):
        # target: Fields precedence when comparing which data is greater.
        self._jsonable = {"uuid": uuid, "history": history, "uuids": uuids, "inner": inner, "failure": failure}
        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO:        #  2- mark volatile fields?        #  3- dna property?        #  4- task?
        self.target = target.split(",")
        self.history = history
        self._failure = failure
        self.time = time
        self.timeout = timeout
        self._hollow = hollow
        self.stream = stream
        self._target = [field for field in self.target if field.upper() in matrices]
        self.storage_info = storage_info
        self.matrices = matrices
        self._uuid, self.uuids = uuid, uuids
        self._inner = inner

    def replace(self, step: Union[Step, List[Step]],
                time: Union[str, float] = "keep",
                inner: Optional[AbsData] = "keep",
                stream: Union[str, Iterator] = "keep",
                **fields):
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
        :param time:
        """
        return self._replace(step, time=time, inner=inner, stream=stream, **fields)

    # TODO:proibir mudança no inner, exceto por meio do step Inner
    def _replace(self, step, failure="keep", time="keep", timeout: bool = "keep",
                 hollow: bool = "keep", stream="keep", inner: Optional[AbsData] = "keep", **fields):
        history = self.history or History([])
        step = step if isinstance(step, list) else [step]
        failure = self.failure if failure == "keep" else failure
        time = self.time if time == "keep" else time
        timeout = self.timeout if timeout == "keep" else timeout
        hollow = self.ishollow if hollow == "keep" else hollow
        stream = self.stream if stream == "keep" else stream
        inner = self.inner if isinstance(inner, str) else inner
        matrices = self.matrices.copy()

        matrices.update(fields2matrices(fields))
        uuid, uuids = evolve_id(self.uuid, self.uuids, step, matrices)

        kw = {"time": time, "timeout": timeout, "hollow": hollow, "stream": stream, "storage_info": self.storage_info}
        return Data(uuid, uuids, history << step, failure, **kw, inner=inner, **matrices)

    def timed(self, time):
        return self._replace([], time=time)

    def timedout(self, step, time=None):
        return self._replace(step, time=time, timeout=True)

    def failed(self, step, failure):
        return self._replace(step, failure=failure)

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
                f"\n{self.history ^ 'name'} does not "
                f"provide field {name} needed by {comp} .\nAvailable matrices: {list(self.matrices.keys())}")
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

        # Fetch previously deferred value?...
        if callable(m):  # TODO: make all Steps lazy (to enable use with fields produced by and inside streams?
            if block:
                raise NotImplementedError("Waiting of values not implemented yet!")
            self.matrices[mname] = m = m()

        # Just return formatted according to capitalization...
        if not name.islower():
            return m
        elif name in ["r", "s"]:
            return mat2vec(m)
        elif name in ["y", "z"]:
            return mat2vec(m)
        else:
            comp = context.name if "name" in dir(context) else context
            raise Exception("Unexpected lower letter:", m, "requested by", comp)

    # def transformedby(self, step):
    #     """Return this Data object transformed by func.
    #
    #     Return itself if it is frozen or failed."""
    #     # REMINDER: It is preferable to have this method in Data instead of Step because of the different
    #     # data handling depending on the type of content: Data, Root.
    #     if self.isfrozen or self.failure:
    #         step = step.pholder
    #         output_data = self.replace([step])  # TODO: check if Pholder here is what we want
    #         # print(888777777777777777777777)
    #     else:
    #         output_data = step._transform_impl(self)
    #         if isinstance(output_data, dict):
    #             output_data = self.replace(step=[step], **output_data)
    #         # print(888777777777777777777777999999999999999999999999)
    #
    #     # TODO: In the future, remove this temporary check. It has a small cost, but is useful while in development:
    #     # print(type(step))
    #     # print(type(output_data))
    #     if self.uuid * step.uuid != output_data.uuid:
    #         print("Error:", 4444444444444444, step)
    #         print(
    #             f"Expected UUID {self.uuid} * {step.uuid} = {self.uuid * step.uuid} "
    #             f"doesn't match the output_data {output_data.uuid}"
    #         )
    #         print("Histories:")
    #         print(self.history ^ "longname", self.history ^ "uuid")
    #         print(output_data.history ^ "longname", output_data.history ^ "uuid")
    #         # print(u.UUID("ýϔȚźцŠлʉWÚΉїͷó") * u.UUID("4ʊĘÓĹmրӐƉοÝѕȷg"))
    #         # print(u.UUID("ýϔȚźцŠлʉWÚΉїͷó") * u.UUID("1ϺϽΖМȅÏОʌŨӬѓȤӟ"))
    #         print(step.longname)
    #         print()
    #         raise Exception
    #     return output_data

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
        return ",".join(transf.id for transf in self.history)

    @lru_cache()
    def field_dump(self, name):
        """Lazily compressed matrix for a given field.
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
        return STORAGE_CONFIG['storages'][self.storage_info].fetch_matrix(id)

    def _remove_unsafe_prefix(self, item, step="undefined"):
        """Handle unsafe (i.e. failed data with) fields."""
        if item.startswith('unsafe'):
            # User knows what they are doing.
            return item[6:]

        if self.failure or self.timeout or self.ishollow:
            raise Exception(f"Step {step} cannot access fields ({item}) from Data objects that come from a "
                            f"failed/timedout/hollow pipeline! HINT: use unsafe{item}. \n"
                            f"HINT2: To calculate training accuracy the 'train' Data should be inside the 'test' tuple; use Copy "
                            f"for that."
                            )  # TODO: breakdown this msg for each case.
        return item

    def _uuid_(self):
        return self._uuid

    def _inner_(self):
        return self._inner

    @property
    def failure(self):
        return self._failure

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


class MissingField(Exception):
    pass


def untranslate_type(name):
    if isinstance(name, list):
        return name
    if name in ["real", "int"]:
        return "NUMERIC"
    else:
        raise Exception("Unknown type:", name)
