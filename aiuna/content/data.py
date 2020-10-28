#  Copyright (c) 2020. Davi Pereira dos Santos
#      This file is part of the aiuna project.
#      Please respect the license. Removing authorship by any means
#      (by code make up or closing the sources) or ignoring property rights
#      is a crime and is unethical regarding the effort and time spent here.
#      Relevant employers or funding agencies will be notified accordingly.
#
#      aiuna is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      aiuna is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with aiuna.  If not, see <http://www.gnu.org/licenses/>.
#

import traceback
from functools import lru_cache, cached_property

import arff
import numpy as np

from aiuna.compression import pack
from aiuna.history import History
from linalghelper import evolve_id, mat2vec, field_as_matrix, islazy
from aiuna.mixin.timing import withTiming, TimeoutException
from cruipto.uuid import UUID
from transf.mixin.identification import withIdentification
from transf.mixin.printing import withPrinting
# TODO: iterable data like dict
from transf.step import Step, MissingField
from transf.timeout import Timeout


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
    #           Let         Let                 c/ Tim.                         vários  map,cache,summ
    #           maxtime  comparable  changed failure timeout duratio parntid inner   stream  storage step    history
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
        step = history.last
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

    @cached_property
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
            List of Step objects that transforms this Data object.
        fields
            Matrices or vector/scalar shortcuts to them.

        Returns
        -------
        New Content object (it keeps references to the old one for performance).
        :param step:
        """
        if not isinstance(step, Step):
            raise Exception("Step cannot be of type", type(step))
        if isinstance(step, Timeout):
            changed = ["timeout", "duration"]
        else:
            from aiuna.file import File
            changed = []
            for field, value in fields.items():
                if not islazy(value) and not isinstance(step, File):
                    raise Exception(f"{field} should be callable! Not:", type(value))
                if field in self.triggers + ["changed"]:
                    raise Exception(f"'{field}' cannot be externally set! Step:" + step.longname)
                changed.append(field)

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

    # @cached_property
    # def eager(self):
    #     """Touch every lazy field by accessing all fields.
    #
    #     Stream is kept intact???"""
    #     for f in self:
    #         _ = self[f]
    #     return self

    @cached_property
    def Xy(self):
        return self["X"], self["y"]

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

    def __rlshift__(self, other):
        if other.isclass:
            other = other()
        return other.process(self)

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
        self.step = newdata.step
        self.parent_uuid = newdata.parent_uuid
        self.field_funcs_m = newdata.field_funcs_m

        # REMINDER: cache invalidation seems unneeded according to tests, but we will do it anyway...
        for attr in self.__dict__.values():
            if callable(attr) and hasattr(attr, "cacheclear"):
                attr.cacheclear()

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
        kup = key.upper() if len(key) == 1 else key
        # print("GET", key, " <<<<<<<<<<<<<<<<<<<<<<", self.field_funcs_m[kup], islazy(self.field_funcs_m[kup]) and self.field_funcs_m[kup].__name__)

        # Is it an already evaluated field?
        if not islazy(self.field_funcs_m[kup]):
            if len(kup) > 1:
                return self.field_funcs_m[kup]

            # Format single-letter field according to capitalization.
            if kup.islower():
                return mat2vec(self.field_funcs_m[kup.upper()])
            return self.field_funcs_m[kup]

        # Is it a lazy field...

        #   ...from storage? Just call it, without timing or catching exceptions as failures.
        if "_from_storage_" in self.field_funcs_m[kup].__name__:
            self.field_funcs_m[kup] = field_as_matrix(self.field_funcs_m[kup]())
            return self.field_funcs_m[kup]

        #   ...yet to be processed?
        try:
            with self.time_limit(self.maxtime):
                t, value = self.time(lambda: field_as_matrix(key, self.field_funcs_m[kup]()))
                self._duration += t
                self.field_funcs_m[kup] = value
        except TimeoutException:
            self.mutate(Timeout(self.maxtime) << self)
        except Exception as e:
            self._failure = self.step.translate(e, self)
            self.field_funcs_m[kup] = None  # REMINDER None means interrupted
        return self.field_funcs_m[kup]

    def __getattr__(self, item):
        """Create shortcuts to fields."""
        # TODO y não funciona

        # Handle pandas suffix.
        if item.endswith("_pd"):
            name = item[:-3]
            if name.upper() not in self.field_funcs_m:
                print(f"Field {name} not found when trying to convert it to pandas. Available ones:",
                      self.field_funcs_m)
                exit()
            name = name.upper()
            from pandas import DataFrame
            desc = name[:-2] + "d_m" if name.endswith("_m") else name + "d"
            if desc in self.field_funcs_m:
                return DataFrame(self.field_funcs_m[name], columns=self.field_funcs_m[desc])
            else:
                return DataFrame(self.field_funcs_m[name])

        # Handle numpy shortcuts
        if item.endswith("w"):
            return self[item[:-1]].shape[0]
        if item.endswith("h"):
            return self[item[:-1]].shape[1]

        # Handle field access
        if item in self.field_funcs_m:
            return self[item]

        # Handle missing known fields
        if item in ["inner", "stream"]:
            raise MissingField(f"Field '{item}' not provided by steps" + str(self.history ^ "name"), self, item)

        # Fallback to methods and other attributes.
        return super().__getattribute__(item)

    def __delitem__(self, key):
        from aiuna.delete import Del
        self.mutate(Del(field=key) << self)

    def __setitem__(self, key, value):
        # process mutation
        from aiuna.let import Let
        self.mutate(Let(field=key, value=value) << self)

    # * ** -
    # @ cache
    # & | ^ // %
    # -d +d
    # ~ sample
    # REMINDER: the detailed History is unpredictable, so it is impossible to provide a useful plan() based on future steps
    # def plan(self, step):

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

    @lru_cache()
    def field_dump(self, name):
        """Cached compressed content for a given field.

        It is useful to cache in memory when more than one backend is used to store Data objects."""
        return pack(self[name])

    # @property
    # @lru_cache()
    # def ids_lst(self):  #TODO ainda precisa?
    #     return [self.uuids[name].id for name in self.names]
    #
    # @property
    # @lru_cache()
    # def ids_str(self):  #TODO ainda precisa?
    #     return ','.join(self.ids_lst)
    #
    # @property
    # @lru_cache()
    # def names_str(self):  #TODO ainda precisa?
    #     return ','.join(self.names)

    # @cached_property
    # def picklable(self):
    #     """Remove unpicklable parts."""
    #     return self.picklable_()[0]
    #
    # @cached_property
    # def unpicklable(self):
    #     """Restore unpicklable parts."""
    #     return self.unpicklable_([{}])

    # # noinspection PyDefaultArgument
    # def picklable_(self, unpicklable_parts=[]):
    #     """Remove unpicklable parts, but return them together as a list of dicts, one dict for each nested inner objects."""
    #     if isinstance(self, Picklable):
    #         return self, unpicklable_parts
    #     unpicklable_parts = unpicklable_parts.copy()
    #     history = History(self.history.aslist)
    #     unpicklable_parts.append({"stream": self.stream})
    #     if self.inner:
    #         inner, unpicklable_parts = self.inner.picklable_(unpicklable_parts)
    #     else:
    #         inner = None
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
    #         return self
    #     if self.stream:
    #         raise Exception("Inconsistency: this picklable Data object contains a stream!")
    #     # make a copy, since we will change history and stream directly; and convert to right class
    #     stream = unpicklable_parts and "stream" in unpicklable_parts[0] and unpicklable_parts[0]["stream"]
    #     if not isinstance(self.history[0], dict):
    #         raise Exception("Pickable Data should have a History of dicts instead of", type(self.history[0]))
    #     inner = self.inner and self.inner.unpicklable
    #     return Data(self.uuid, self.uuids, self.history, stream, self.storage_info, inner, **self._matrices)


def untranslate_type(name):
    if isinstance(name, list):
        return name
    if name in ["real", "int"]:
        return "NUMERIC"
    else:
        raise Exception("Unknown type:", name)
