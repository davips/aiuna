import json
import traceback
from functools import lru_cache, cached_property
from typing import Union, Iterator

import arff
import numpy as np

from aiuna.compression import pack
from aiuna.history import History
from aiuna.mixin.exceptionhandling import asExceptionHandler
from aiuna.mixin.linalghelper import fields2matrices, evolve_id, mat2vec
from aiuna.mixin.timing import withTiming
from cruipto.uuid import UUID
from transf.customjson import CustomJSONEncoder, CustomJSONDecoder
from transf.mixin.identification import withIdentification
from transf.mixin.printing import withPrinting


# TODO: iterable data like dict


class Data(asExceptionHandler, withIdentification, withPrinting, withTiming):
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
        should be marked with the mutability suffix '_' like in 'elapsed_';
        so they stay outside matrix, but still available as Data attributes.
        They are not stored by conventional storages.
        User-content enabled ones like OkaSt may provide that.
    """
    _Xy = None

    # todos fields (stream, inner e matrices) aparecem como atributo
    # Os metafields são subconjunto das matrices e sempre existem, mesmo sem serem providos.
    #  tipos de metafields:

    # nunca lazy
    #       não alteráveis externamente
    internal = ["changed"]  # <- TODO implementar changed (=onde step mexeu)

    #       usuário os define, e o self[] depende deles pra começar:
    strict = ["limit", "comparable"]

    # ??????
    #       não alteráveis externamente e dependem de outros campos rodarem (e por isso lazies(?), ou erro se acessados antes da hora(?), ou com estado que indica espera(?)):
    reserved = ["failure", "timeout", "elapsed"]

    metafields = reserved + strict

    # aparecem na impressão... inner e metafields (quando não None).

    _matrices_m = {}

    def __init__(self, uuid, uuids, history, stream=None, storage_info=None, inner=None, **matrices):
        # comparable: Fields precedence when comparing which data is greater.
        self._jsonable = {"uuid": uuid, "uuids": uuids}

        # Move mutable fields from matrices to self.
        for k in list(matrices.keys()):
            if k.endswith("_m"):
                self._matrices_m[k] = self.__dict__[k] = matrices.pop(k)

        # Put interesting fields inside representation for printing; and mark them as None if needed.
        if storage_info:
            self._jsonable["storage_info"] = storage_info
        if inner:
            self._jsonable["inner"] = inner
        if matrices:
            self._jsonable["matrices"] = ",".join(matrices.keys())

        # TODO jsonable precisa acordar lazies se contiver fields lazy
        #  (inviavel, pois o usuario nao quer rodar nada, apenas imprimir e ver algum campo);;
        #  ou ser mutante (poderia ser mutante, só preciso verificar se algo imutavel depende dele):
        #  mostra failure=unknown enquanto não é requisitado tudo;
        #  ou (msms coisa? : ) recusar impressão enquanto estiver pendente e alertar usuario.
        for field in self.metafields:
            if field in matrices:
                self.__dict__[field] = self._jsonable[field] = matrices[field]
            else:
                uuids[field] = UUID()
                matrices[field] = None

            # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO:        #  2- mark volatile fields?        #  3- dna property?        #  4- task?
        self.history = history
        self.stream = stream
        self.storage_info = storage_info
        self._matrices = matrices
        self._uuid, self.uuids = uuid, uuids
        self.inner = inner

    @cached_property
    def comparable(self):
        return [field for field in self["comparable"] if field.upper() in self.fields]

    def update(self, step, inner="keep", stream: Union[str, Iterator] = "keep", **fields):
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
        for field in fields:
            if field in self.reserved:
                raise Exception(f"Field {field} cannot be externally set!")
        return self._update(step, inner=inner, stream=stream, **fields)

    # TODO:proibir mudança no inner, exceto por meio do step Inner
    def _update(self, step, stream="keep", inner="keep", **fields):
        if "timeout" in fields:
            if step.isntTimeout:
                print("Only Timeout step can set timeout, not", step.longname)
                exit()
        step = step if isinstance(step, list) else [step]
        if len(step) == 0 and any(not s.endswith("_m") for s in step):
            print("Empty list of steps is not allowed when nonvolatile (i.e. immutable) fields are present:",
                  list(fields.keys()))
            exit()
        if isinstance(self, Picklable) and step:
            raise Exception("Picklable history cannot be updated!")
        history = self.history or History([])
        if step:
            history = history << step
        stream = self.stream if stream == "keep" else stream
        inner = self.inner if isinstance(inner, str) and inner == "keep" else inner

        # Only update matrix uuids for the provided and changed ones!
        matrices = self._matrices.copy()
        changed_matrices = {}
        # REMINDER: conversão saiu de _update() para self[] (que é o novo .field()) para conciliar laziness e aceitação de vetores e escalares
        for k, v in fields.items():
            kup = k.upper()
            if (kup not in matrices) or matrices[kup] is not v:
                changed_matrices[kup] = v
        matrices.update(changed_matrices)
        uuid, uuids = evolve_id(self.uuid, self.uuids, step, changed_matrices)

        return Data(uuid, uuids, history, stream=stream, storage_info=self.storage_info, inner=inner, **matrices)

    @cached_property
    def eager(self):
        """Touch every lazy field by accessing all fields.

        Stream is kept intact"""
        for f in self:
            void = f[f]
        return self

    @cached_property
    def Xy(self):
        if self._Xy is None:
            self._Xy = self["X"], self["y"]
        return self._Xy

    @property
    @lru_cache()
    def fields(self):
        # REMINDER fields se dividem entre _matrices e _matrices_m
        return list(self._matrices.keys() + self._matrices_m.keys())

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
        return 22222222222  # STORAGE_CONFIG['storages'][self.storage_info].fetch_matrix(id)  #TODO

    def _uuid_(self):
        return self._uuid

    def __lt__(self, other):
        """Amenity to ease pipeline result comparisons. 'A > B' means A is better than B."""
        if self._comparable is None:
            return Exception("Impossible to make comparisons. No comparable field was defined!")
        for name in self._comparable:
            return self[name] < other[name]
        return Exception("Impossible to make comparisons. None of the comparable fields are available:", self.comparable)

    def __eq__(self, other):
        # TODO benchmark presence of isinstance here, can be disabled in production version
        return isinstance(other, Data) and self.uuid == other.uuid

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
        raise Exception("Should not be accessed. Use jsonable() instead!")

    def jsonable(self):  # overriding because there are lazy fields in Data, so jsonable is mutable/noncached
        # TODO é possível impedir acesso a estado nao definitivo?
        #   ...e marcar como fresco após itemsetter?
        return self._jsonable

    @cached_property
    def picklable(self):
        """Remove unpicklable parts."""
        return self.picklable_()[0]

    @cached_property
    def unpicklable(self):
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
        newdata = Picklable(self.uuid, self.uuids, history, stream=None, storage_info=self.storage_info, inner=inner, **self._matrices)
        # TODO: como ficam os lazies antes de picklear?
        #  no fetch blz, só falta usar a lista de unpicklables
        #  pra recuperar após passar pela thread.
        #  Mas proibe dar store? ou store tenta ativar todos?
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
        return Data(self.uuid, self.uuids, history, stream, self.storage_info, inner, **self._matrices)

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
        del self._matrices[key]

    @lru_cache()
    def __getitem__(self, key):
        """Safe access to a field, with a friendly error message.

        Parameters
        ----------
        name
            Name of the field.

        Returns
        -------
        Matrix, vector or scalar
        """
        #   TODO: vai ter? =>    block     Whether to wait for the value or to raise FieldNotReady exception if it is not readily available.

        # setar: failure timeout elapsed
        # consultar: limit
        # for k, v in fields2matrices(fields).items():
        em andamento esse metodo inteiro
        try:
            with self.time_limit(maxtime), self.time() as t:
                outdata = self.checked(f, exit_on_error)(marked_data)
            outdata = outdata.update([], elapsed=t)
        except TimeoutException:  # TODO: isso vai sair daqui
            outdata = Timeout(maxtime).process(marked_data)

        # Metafields are always present, at least as a None value.
        if key in self.metafields:
            return self.matrices[key]

        # Check existence of the field.
        matrix_name = key.upper() if len(key) == 1 else key
        if matrix_name not in self.matrices:
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

    def __getattr__(self, item):
        """Create shortcuts to fields."""

        # Handle pandas suffix.
        if item.endswith("_pd"):
            name = item[:-3]
            if name.upper() not in self.fields:
                print(f"Field {name} not found when trying to convert it to pandas. Available ones:", self.fields)
                exit()
            name = name.upper()
            from pandas import DataFrame
            desc = name[:-2] + "d_m" if name.endswith("_m") else name + "d"
            if desc in self.matrices:
                return DataFrame(self.matrices[name], columns=self.matrices[desc])
            else:
                return DataFrame(self.matrices[name])

        # Handle numpy shortcuts
        if item.endswith("w"):
            return self[item[:-1]].shape[0]
        if item.endswith("h"):
            return self[item[:-1]].shape[1]

        # Handle field access
        # ismatrix, ismutable, ismeta = len(item) < 3, item.endswith("_m"), item in self.metafields
        if item in self.fields:
            return self[item]

        # Fallback to methods and other attributes.
        return super().__getattribute__(item)

    def __setitem__(self, key, value):
        print(f"Setting fields directly is not allowed.")
        print(f"HINT: use update(step, {key}=value) providing the accountable step for the change.\nValue:{value}")

    def __iter__(self):
        return iter(self._matrices)

    def __len__(self):
        return len(self._matrices)

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

    def _name_(self):
        return self._uuid

    def _context_(self):
        return self.history ^ "names"


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
