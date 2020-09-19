# data
import json
import traceback
from functools import lru_cache, cached_property

import arff
import numpy as np

import aiuna.compression as com
import aiuna.history as h
import aiuna.mixin.linalghelper as li
import cruipto.uuid as u
from aiuna.config import STORAGE_CONFIG
from transf.absdata import AbsData
from transf.mixin.printing import withPrinting


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

    def __init__(self, uuid, uuids, history=h.History([]), failure=None, frozen=False, hollow=False, stream=None, target="s,r", storage_info=None, historystr=None, trdata=None, **matrices):
        # target: Fields precedence when comparing which data is greater.
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

        print(truuid)
        uuid, uuids = li.evolve_id(self.uuid, self.uuids, transformers, matrices, truuid)

        # noinspection Mypy
        if self.history is None:
            self.history = h.History([])
        return Data(
            history=self.history << transformers,
            failure=failure,
            frozen=frozen,
            hollow=self.ishollow,
            stream=stream,
            storage_info=self.storage_info,
            uuid=uuid,
            uuids=uuids,
            trdata=trdata,
            **matrices,
        )

    @property
    def jsonable(self):
        return self._jsonable

    @cached_property
    def frozen(self):
        """TODO: Explicar aqui papéis de frozen...
            1- pipeline fim-precoce (p. ex. após SVM.enhance)
            2- pipeline falho (após exceção)
         """
        return Data(
            history=self.history,
            failure=self.failure,
            frozen=True,
            hollow=self.ishollow,
            stream=self.stream,
            storage_info=self.storage_info,
            uuid=self.uuid,
            uuids=self.uuids,
            **self.matrices,
        )

    @cached_property
    def unfrozen(self):  # TODO: check if component Unfreeze is really needed
        return Data(
            history=self.history,
            failure=self.failure,
            frozen=False,
            hollow=self.ishollow,
            stream=self.stream,
            storage_info=self.storage_info,
            uuid=self.uuid,
            uuids=self.uuids,
            **self.matrices,
        )

    @lru_cache()
    def hollow(self, transformer=None):
        """Create a temporary hollow Data object (only Persistence can fill it).

        ps. History is transferred to historystr, uuid is changed."""
        if transformer is None:
            uuid, uuids = self.uuid, self.uuids
        else:
            uuid, uuids = li.evolve_id(self.uuid, self.uuids, (transformer,), self.matrices)
        return Data(
            history=h.History([]),  # TODO: check if history must be updated as well.
            failure=self.failure,
            frozen=self.isfrozen,
            hollow=True,
            stream=self.stream,
            storage_info=self.storage_info,
            uuid=uuid,
            uuids=uuids,
            historystr=self.history.pickable,
            **self.matrices,
        )

    @property
    @lru_cache()
    def pickable(self):
        """Create a pickable Data object (i.e. without History)."""
        if self.history is None:
            self.history = h.History([])
        return Data(
            history=h.History([]),  # TODO: remove IFs history is None?
            failure=self.failure,
            frozen=self.isfrozen,
            hollow=self.ishollow,
            stream=self.stream,
            storage_info=self.storage_info,
            uuid=self.uuid,
            uuids=self.uuids,
            historystr=self.history.pickable,
            **self.matrices,
        )

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
        if mname not in self.matrices:
            comp = context.name if "name" in dir(context) else context
            raise MissingField(
                f"\n\nLast transformation:\n{self.history.last} ... \n"
                f" Data object <{self}>...last transformed by "
                f"{self.history.last} does not "
                f"provide field {name} needed by {comp} \n. Available matrices: {list(self.matrices.keys())}")

        m = self.matrices[mname]

        # Fetch from storage?...
        if isinstance(m, u.UUID):
            if self.storage_info is None:
                comp = context.name if "name" in dir(context) else context
                raise Exception("Storage not set! Unable to fetch " + m.id, "requested by", comp)
            print(">>>> fetching field:", name, m.id)
            self.matrices[mname] = m = self._fetch_matrix(m.id)

        # Fetch previously deferred value?...
        if callable(m):
            if block:
                raise NotImplementedError("Waiting of values not implemented yet!")
            self.matrices[mname] = m = m()

        # Just return formatted according to capitalization...
        if not name.islower():
            return m
        elif name in ["r", "s"]:
            return li.mat2vec(m)
        elif name in ["y", "z"]:
            return li.mat2vec(m)
        else:
            comp = context.name if "name" in dir(context) else context
            raise Exception("Unexpected lower letter:", m, "requested by", comp)

    def transformedby(self, transformer):
        """Return this Data object transformed by func.

        Return itself if it is frozen or failed."""
        # REMINDER: It is preferable to have this method in Data instead of Transformer because of the different
        # data handling depending on the type of content: Data, NoData.
        if self.isfrozen or self.failure:
            transformer = transformer.pholder
            output_data = self.replace([transformer])  # TODO: check if Pholder here is what we want
            # print(888777777777777777777777)
        else:
            output_data = transformer._transform_impl(self)
            if isinstance(output_data, dict):
                output_data = self.replace(transformers=[transformer], **output_data)
            # print(888777777777777777777777999999999999999999999999)

        # TODO: In the future, remove this temporary check. It has a small cost, but is useful while in development:
        # print(type(transformer))
        # print(type(output_data))
        if self.uuid * transformer.uuid != output_data.uuid:
            print("Error:", 4444444444444444, transformer)
            print(
                f"Expected UUID {self.uuid} * {transformer.uuid} = {self.uuid * transformer.uuid} "
                f"doesn't match the output_data {output_data.uuid}"
            )
            print("Histories:")
            print(self.history ^ "longname", self.history ^ "uuid")
            print(output_data.history ^ "longname", output_data.history ^ "uuid")
            # print(u.UUID("ýϔȚźцŠлʉWÚΉїͷó") * u.UUID("4ʊĘÓĹmրӐƉοÝѕȷg"))
            # print(u.UUID("ýϔȚźцŠлʉWÚΉїͷó") * u.UUID("1ϺϽΖМȅÏОʌŨӬѓȤӟ"))
            print(transformer.longname)
            print()
            raise Exception
        return output_data

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
        return com.pack(self.field(name))

    @property
    @lru_cache()
    def matrix_names_str(self):
        return ','.join(self.matrix_names)

    @property
    def isfrozen(self):
        return self._frozen

    @property
    def ishollow(self):
        return self._hollow

    @lru_cache()
    def _fetch_matrix(self, id):
        if self.storage_info is None:
            raise Exception(f"There is no storage set to fetch: {id})!")
        return STORAGE_CONFIG['storages'][self.storage_info].fetch_matrix(id)

    def _remove_unsafe_prefix(self, item, component="undefined"):
        """Handle unsafe (i.e. frozen) fields."""
        if item.startswith('unsafe'):
            # User knows what they are doing.
            return item[6:]

        if self.failure or self.isfrozen or self.ishollow:
            raise Exception(f"Component {component} cannot access fields ({item}) from Data objects that come from a "
                            f"failed/frozen/hollow pipeline! HINT: use unsafe{item}. \nHINT2: probably the model/enhance flags are not being used properly around a Predictor.\n"
                            f"HINT3: To calculate training accuracy the 'train' Data should be inside the 'test' tuple; use Copy "
                            f"for that."
                            )  # TODO: breakdown this msg for each case.
        return item

    def _uuid_(self):
        return self._uuid

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
            return self.field(name) < other.field(name, context="comparison between Data objects")
        return Exception("Impossible to make comparisons. None of the target fields are available:", self.target)

    def __eq__(self, other):
        # Checks removed for speed (isinstance is said to be slow...)
        # from aiuna.content.specialdata import NoData
        # if other is not NoData or not isinstance(other, Data):  # TODO: <-- check for other types of Data?
        #     return False
        return self.uuid == other.uuid

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
            print("Problems creating ARFF", self.filename)
            print("Types:", Xt, Yt)
            print("Sample:", self.X[0], self.Y[0])
            print("Expected sizes:", len(Xt), "+", len(Yt))
            print("Real sizes:", len(self.X[0]), "+", len(self.Y[0].shape))
            exit(0)


class MissingField(Exception):
    pass


def untranslate_type(name):
    if isinstance(name, list):
        return name
    if name in ["real", "int"]:
        return "NUMERIC"
    else:
        raise Exception("Unknown type:", name)
