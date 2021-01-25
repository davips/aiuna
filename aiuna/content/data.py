#  Copyright (c) 2020. Davi Pereira dos Santos
#  This file is part of the aiuna project.
#  Please respect the license - more about this in the section (*) below.
#
#  aiuna is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  aiuna is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with aiuna.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.

import traceback
from functools import lru_cache, cached_property
from pprint import pprint

import arff
import numpy as np
from pandas import DataFrame, Series

from aiuna.content.creation import new, translate_type
from aiuna.mixin.timing import withTiming, TimeoutException
from garoupa.avatar23 import colors
from garoupa.uuid import UUID
from akangatu.linalghelper import evolve_id, mat2vec, field_as_matrix, islazy
from akangatu.transf.mixin.identification import withIdentification
from akangatu.transf.mixin.printing import withPrinting
from akangatu.transf.noop import NoOp
from akangatu.transf.step import Step, MissingField
from akangatu.transf.timeout import Timeout


class Data(withIdentification, withPrinting, withTiming):
    """Immutable lazy data for most machine learning scenarios.
# comparable: Fields precedence when comparing which data is greater.
    Parameters
    ----------
    history
        A History objects that represents a sequence of steps.
    storage_info
        An alias to a global Storage object for lazy matrix fetching.
    matrices  TODO trocar pra fields
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
        should be marked with the mutability suffix '_' like in 'duration_';
        so they stay outside matrix, but still available as Data attributes.
        They are not stored by conventional storages.
        User-content enabled ones like OkaSt may provide that.
    """

    # muda em                           update  iniget  iniget  iniget  init    step.new()      get     update
    #       Let         Let                 c/ Tim.                         vários  map,cache,summ
    #       maxtime  comparable  changed failure timeout duratio parntid inner   stream  storage step    history
    # updatekwargs:x        x
    # protegid/automat:                 x       x       x       x       x                       x       nonkw   x
    # transformavel x       x                                                   x       x
    # ____________________________________________________________________________________________________________________
    # initargs                          x       x       x       x       calculado               x       x
    # _fields_m:                                                x
    # ____________________________________________________________________________________________________________________
    # updtargs:                                                                 x       x               x
    # armazen:  field       f           f       f       f       run     col     col     s+bool          x
    # não lazy: x           x           [dispara lazies?              ] x               it/dblz x       x

    # REMINDER todos fields entram obrig lazy no update() porque podem ativar o consumo de stream antes da hora.
    # REMINDER tudo lazy adotado inicialmente pq ajuda o cache a saber o que vai ser feito (e usuario a puxar do DB) sem precisar mexer com uuid
    # REMINDER changed precisa vir do update() pq não sabemos se algum lazy veio do step anterior
    triggers = ["failure", "timeout", "duration"]
    maxtime, comparable = None, None
    _duration = 0

    def __hash__(self):
        return id(self)

    # def __hash__(self):
    #     return self.uuid.n  # não sei pq , mas não tá herdando hash de withIdentification

    def __init__(self, uuid, uuids, history, **fields):
        if "changed" not in fields:
            print(uuids.keys())
            print(fields.keys())
            raise Exception("Field 'changed' is mandatory as a kwarg, alongside its UUID inside uuids.")
        self.changed = fields["changed"]
        self.field_funcs_m = fields
        self._uuid, self.uuids = uuid, uuids
        try:
            step = history.last
        except:
            step = NoOp()
        self.step_func_m = step
        # lazy lambda name format: "_stepuuid..._from_storage_storageuuid..."
        self.step_uuid = step.uuid if isinstance(step, Step) else UUID(step.name[1:24])
        self.parent_uuid = uuid / self.step_uuid
        self.history = history

        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO lembrar por que concluí que "stream and inner shold also be lazy"

    @property
    def step(self):
        if islazy(self.step_func_m):
            self.step_func_m = self.step_func_m()
        return self.step_func_m

    ###@cached_property
    @property
    def changed_asdict(self):
        """Evaluate and return all fields in 'changed'."""
        return {lazy_field: self.field_funcs_m[lazy_field] for lazy_field in self.changed}

    @property
    def failure(self):
        """First touch all fields in 'changed' (which are necessarily lazy), and only then return the failure, if any."""
        _ = self.changed_asdict
        return self._failure

    @property
    def timeout(self):
        """First touch all fields in 'changed' (which are necessarily lazy), and only then return whether there was a timeout."""
        _ = self.changed_asdict
        return self._timeout

    @property
    def duration(self):
        """First touch all fields in 'changed' (which are necessarily lazy), and only then return duration value."""
        _ = self.changed_asdict
        return self._duration
        # TODO como duration viria do storage?

    @property
    def hasinner(self):
        return "inner" in self.field_funcs_m

    @property
    def hasstream(self):
        return "stream" in self.field_funcs_m

    def _asdict_(self):
        raise Exception("Should not be accessed. Use asdict property instead!")

    # TODO  verificar se algo imutavel depende do asdict (que vai ser mutavel)
    @property
    def asdict(self):  # overriding because there are lazy fields in Data, so asdict is mutable and noncached
        dic = {"uuid": self.uuid, "uuids": self.uuids,
               "step": self.step_func_m.name if islazy(self.step_func_m) else self.step_func_m.asdict}
        if self.hasinner:
            dic["inner"] = self.field_funcs_m["inner"].__name__ if islazy(self.inner) else self.inner.asdict
        if self.hasstream:
            dic["stream"] = "iterator"
        dic.update(self.field_funcs_m)
        return dic

    def inners(self):
        data = self
        while True:
            yield data
            if not data.hasinner:
                break
            data = data.inner

    def update(self, step, **fields):
        """Recreate an updated Data object.

        Parameters
        ----------
        steps
            Step object that process this Data object.
        fields
            Matrices or vector/scalar shortcuts to them.

        Returns
        -------
        New Data object (it keeps references to the old one for performance).
        :param step:
        """
        if not isinstance(step, Step):
            raise Exception("Step cannot be of type", type(step))
        if isinstance(step, Timeout):
            changed = ["timeout", "duration"]
        else:
            from aiuna.step.file import File
            from aiuna.step.new import New
            changed = []
            for field, value in fields.items():
                if not islazy(value) and not isinstance(step, (File, New)):
                    raise Exception(f"{field} should be callable! Not:", type(value))
                if field in self.triggers + ["changed"]:
                    raise Exception(f"'{field}' cannot be externally set! Step:" + step.longname)
                changed.append(field)
        changed = list(sorted(changed))

        # Only update field uuids for the provided and changed ones!
        updated_fields = {"changed": changed}
        # REMINDER: conversão saiu de _update() para self[] (que é o novo .field()) para conciliar laziness e aceitação de vetores e escalares
        for k, v in fields.items():
            kup = k.upper() if len(k) == 1 else k
            if (kup not in self.field_funcs_m) or self.field_funcs_m[kup] is not v:
                updated_fields[kup] = v
        uuid, uuids = evolve_id(self.uuid, self.uuids, step, updated_fields)

        newfields = self.field_funcs_m.copy()
        newfields.update(updated_fields)
        return Data(uuid, uuids, self.history << step, **newfields)

    ###@cached_property
    @property
    def eager(self):
        """Touch every lazy field by accessing all fields.

        Stream is kept intact???"""
        for f in self:
            _ = self[f]
        return self

    ###@cached_property
    @property
    def Xy(self):
        return self["X"], self["y"]

    @property
    def uuid(self):
        return self._uuid

    @property
    def id(self):
        return self._uuid.id

    @property
    def _uuid_(self):
        return self._uuid

    def __lt__(self, other):
        """Amenity to ease pipeline result comparisons. 'A > B' means A is better than B."""
        if self.comparable is None:
            return Exception("Impossible to make comparisons. No comparable field was defined!")
        for name in self.comparable:
            if name in self.field_funcs_m:
                return self[name] < other[name]
        return Exception("Impossible to make comparisons. None of the comparable fields are available:",
                         self.comparable)

    def __eq__(self, other):
        # TODO benchmark presence of isinstance here, can be disabled in production version
        return isinstance(other, Data) and self.uuid == other.uuid

    # REMINDER Data is mutable in rare occasions: setitem/delitem/

    ###@lru_cache
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

    # def __rlshift__(self, other):
    #     if other.isclass:
    #         other = other()
    #     return other.process(self)

    def __rshift__(self, other):
        if other.isclass:
            other = other()
        return other.process(self)

    def __add__(self, other):
        """Merge two Data objects"""
        # se mexeram na mesma matriz, vale a segunda.
        # Dá pra emendar com o histórico da segunda, desde que o uuid final seja recalculado e que
        # operações de ajuste (Copy) preservem as matrizes pedidas pela segunda no inicio da divergencia (normalmente após File/New).
        # Assume que haver matrizes extra não altera resultado de um step (o que é sensato, pois step não deve fazer "inspection")
        # se foi misto,
        raise Exception("Not implemented: should solve conflicts to merge history of two data objects.")

    def mutate(self, newdata):
        """Inplace swapping of this Data object by another

        UUID and __hash__ will change."""
        self._uuid = newdata.uuid
        self.uuids = newdata.uuids
        self.step_func_m = newdata.step_func_m
        self.step_uuid = newdata.step_uuid
        self.parent_uuid = newdata.parent_uuid
        self.field_funcs_m = newdata.field_funcs_m
        self.history = newdata.history

        # TODO: use this instead?
        # self.__dict__ = newdata.__dict__

        # # REMINDER: cache invalidation seems unneeded according to tests
        # for attr in self.__dict__.values():
        #     if callable(attr) and hasattr(attr, "cacheclear"):
        #         attr.cacheclear()

    ###@lru_cache()
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
        # Format single-letter field according to capitalization.
        if len(key) == 1:
            kup = key.upper()
            if key.islower():
                return mat2vec(self[kup])
        else:
            kup = key

        # Is it an already evaluated field?
        if not islazy(self.field_funcs_m[kup]):
            return self.field_funcs_m[kup]

        # Is it a lazy field...
        #   ...from storage? Just call it, without timing or catching exceptions as failures.
        if "_from_storage_" in self.field_funcs_m[kup].__name__:
            self.field_funcs_m[kup] = field_as_matrix(key, self.field_funcs_m[kup]())
            return self.field_funcs_m[kup]

        #   ...yet to be processed?
        try:
            with self.time_limit(self.maxtime):
                t, value = self.time(lambda: field_as_matrix(key, self.field_funcs_m[kup]()))
                self._duration += t
                self.field_funcs_m[kup] = value
        except TimeoutException:
            self.mutate(self >> Timeout(self.maxtime))
        except Exception as e:
            self._failure = self.step.translate(e, self)
            self.field_funcs_m[kup] = None  # REMINDER None means interrupted
        return self.field_funcs_m[kup]

    def __getattr__(self, item):
        """Create shortcuts to fields."""

        if item.startswith("__"):
            return super().__getattribute__(item)

        # Handle field access
        if item in self.field_funcs_m or item.upper() in self.field_funcs_m:
            return self[item]

        # Handle missing known fields
        if item in ["inner", "stream"]:
            raise MissingField(f"Field '{item}' not provided by steps" + str(self.history ^ "name"), self, item)

        # Fallback to methods and other attributes.
        return super().__getattribute__(item)

    def __delitem__(self, key):
        from aiuna.step.delete import Del
        self.mutate(self >> Del(field=key))

    def __setitem__(self, key, value):
        # process mutation
        from aiuna.step.let import Let
        self.mutate(self >> Let(field=key, value=value))

    def items(self):
        # TODO quais ficam de fora de fields? são importantes pra iterar?
        for k in self:
            yield k, self[k]

    def __iter__(self):
        yield from self.field_funcs_m

    def __len__(self):
        return len(self.field_funcs_m)  # TODO idem

    def _name_(self):
        return self._uuid

    def _context_(self):
        return self.history ^ "names"

    @staticmethod
    def from_pandas(X_pd: DataFrame, y_pd: Series):
        X, y = X_pd.to_numpy(), y_pd.to_numpy().astype("float")
        Xd, Yd = X_pd.columns.tolist(), [y_pd.name]
        Xt, Yt = [translate_type(str(c)) for c in X_pd.dtypes], list(sorted(set(y)))
        return new(X=X, y=y, Xd=Xd, Yd=Yd, Xt=Xt, Yt=Yt)

    # @property
    # ###@lru_cache()
    # def ids_lst(self):  #TODO ainda precisa?
    #     return [self.uuids[name].id for name in self.names]
    #
    # @property
    # ###@lru_cache()
    # def ids_str(self):  #TODO ainda precisa?
    #     return ','.join(self.ids_lst)
    #
    # @property
    # ###@lru_cache()
    # def names_str(self):  #TODO ainda precisa?
    #     return ','.join(self.names)

    # ###@cached_property
    @property
    # def picklable(self):
    #     """Remove unpicklable parts."""
    #     return self.picklable_()[0]
    #
    # ###@cached_property
    @property
    # def unpicklable(self):
    #     """Restore unpicklable parts."""
    #     return self.unpicklable_([{}])

    # # noinspection PyDefaultArgument
    # def picklable_(self, unpicklable_parts=[]):
    #     """Remove unpicklable parts, but return them together as a list of dicts, one dict for each nested inner objects."""
    #     if isinstance(self, Picklable):
    #     return self, unpicklable_parts
    #     unpicklable_parts = unpicklable_parts.copy()
    #     history = History(self.history.aslist)
    #     unpicklable_parts.append({"stream": self.stream})
    #     if self.inner:
    #     inner, unpicklable_parts = self.inner.picklable_(unpicklable_parts)
    #     else:
    #     inner = None
    #     newdata = Picklable(self.uuid, self.uuids, history, stream=None, storage_info=self.storage_info, inner=inner, **self._matrices)
    #     # TODO: como ficam os lazies antes de picklear?
    #     #  no fetch blz, só falta usar a lista de unpicklables
    #     #  pra recuperar após passar pela thread.
    #     #  Mas proibe dar store? ou store tenta ativar todos?
    #     return newdata.eager, unpicklable_parts

    # def unpicklable_(self, unpicklable_parts):
    #     """Rebuild an unpicklable Data.
    #
    #     History is desserialized, if given as str.
    #     """
    #     # REMINDER: Persistence/threading actions can be nested, so self can be already unpicklable
    #     if not isinstance(self, Picklable):
    #     return self
    #     if self.stream:
    #     raise Exception("Inconsistency: this picklable Data object contains a stream!")
    #     # make a copy, since we will change history and stream directly; and convert to right class
    #     stream = unpicklable_parts and "stream" in unpicklable_parts[0] and unpicklable_parts[0]["stream"]
    #     if not isinstance(self.history[0], dict):
    #     raise Exception("Pickable Data should have a History of dicts instead of", type(self.history[0]))
    #     inner = self.inner and self.inner.unpicklable
    #     return Data(self.uuid, self.uuids, self.history, stream, self.storage_info, inner, **self._matrices)

    @property
    def icon(self):
        """Information to create an icon for this Data object."""
        return {"id": self.id, "step": self.step.asdict_rec, "colors": colors(self.id)}

    # ###@cached_property
    @property
    def past(self):
        """Map ancestor_id -> afterstep/icon_colors. Last item refers to the current Data object."""
        from aiuna.content.root import Root
        dic = {}
        d = Root
        for s in list(self.history) + [NoOp()]:
            dic[d.id] = {"step": s.asdict_rec, "colors": colors(d.id)}
            d >>= s
        return dic


def untranslate_type(name):
    if isinstance(name, list):
        return name
    if name in ["real", "int"]:
        return "NUMERIC"
    raise Exception("Unknown type:", name)


""" importante TODO

-({a0, a1} + {b0, b1}) = a0 | a1 | + {b0, b1} 


    step =    an infinitely nested unit set (INUS)    A = {{ ... {a} ... }}; or,
              a set of steps                          D = {A, B, C}

    A * B                     product            (** cached product)
    A + B                     union
    A | B                     stack
    +S                        summation (union) of all unit sets in stack S
    -A                        stacking (disunion) of all unit sets in set A

    Properties (A: set, S: stack, a: INUS)
    +A = error
    -S = error
    -a = a

    -(A | B) = +A | +B
    s0 | s1 | s2              sequence s0,s1,s2
    s0 | ...                  sequence s0,s0,...,s0
    +S                        sequence s0,s1,...,sn
    +(A|B) = {a0,a1,b0,b1}
    -{a0,a1,b0,b1} = (A|B)

    ~                         sample
    ~~                        ?

    @ cache
    & | ^ // %
    -step -> hold
    ~step -> sample
     ...
    +step -> permite ser destrutivo?

    d.hash * A.hash * B.hash / e.hash
    s.id
    update() deveria aceitar qq obj com: {hash, id ?} ou aceitar hexmd5?

    ###########################################
    aceitar repetições de step, melhorar hash ou forçar sanduiches de step recheados com algo inerte?
    coisas a considerar no hash:
          embaralhamento?
          AB != BA
          AAAAA sem colisão
          AA != I
    ###########################################

    ------------------------
    def alternativa, que enfraquece o uso dos ops unários:
    A unit set is equivalent to its contained element.
    A stack of a single element is the element itself.
    ------------------------
"""
