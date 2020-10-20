import traceback
from functools import lru_cache, cached_property
from typing import Union, Iterator

import arff
import numpy as np

from aiuna.compression import pack
from aiuna.mixin.linalghelper import evolve_id, mat2vec, field_as_matrix
from aiuna.mixin.timing import withTiming, TimeoutException
from cruipto.uuid import UUID
from transf._ins import Ins
from transf.mixin.identification import withIdentification
from transf.mixin.printing import withPrinting


# TODO: iterable data like dict
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

    # todos fields (stream, inner e matrices) aparecem como atributo
    # Os metafields são subconjunto das matrices e sempre existem, mesmo sem serem providos;
    # ou seja, são arg explicito na assinatura do metodo (se forem mexiveis).

    #  todos atributos:

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

    # REMINDER todos fields entram obrig lazy no update() porque odem ativar o consumo de stream antes da hora.
    # REMINDER tudo lazy adotado inicialmente pq ajuda o cache a saber o que vai ser feito (e usuario a puxar do DB) sem precisar mexer com uuid
    # REMINDER changed precisa vir do update() pq não sabemos se algum lazy veio do step anterior
    triggers = ["failure","timeout","duration"]
    def __init__(self, uuid, uuids, step, inner=None, stream=None, storage=None, **fields):
        if "changed" not in fields:
            raise Exception("Field 'changed' is mandatory as a kwarg, alongside its UUID inside uuids.")

        # Add trigger fields. Each trigger first touch all fields in 'changed' (which are necessarily lazy), and only then return its current value.
        def trigger_func(field):
            def func():
                for lazy_field in fields["changed"]:
                    lazy_field()
                return self[field]
            return func

        for trigger in self.triggers:
            if trigger in fields:
                raise Exception("Cannot manually set field",trigger)
            fields[trigger] =trigger_func(trigger)
            # TODO precisam aparecer em uuids?

        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        self.inner = inner
        self.stream = stream
        self.storage = storage
        self.fields = fields
        self._uuid, self.uuids = uuid, uuids
        self.step=step
        self.parent_uuid = uuid/step.uuid

        #TODO lembrar por que concluí que "stream and inner shold also be lazy"

    def _asdict_(self):
        raise Exception("Should not be accessed. Use asdict() instead!")

    # TODO  verificar se algo imutavel depende do asdict (que vai ser mutavel)
    def asdict(self):  # overriding because there are lazy fields in Data, so asdict is mutable and noncached
        dic = {            "uuid": self.uuid, "uuids": self.uuids, "step":self.step        }
        if self.inner:
            dic["inner"]=self.inner.id
        if self.stream:
            dic["stream"]="cached" if isinstance(self.stream,bool) else "iterator"
        if self.storage:
            dic["storage"]=self.storage.name
        dic.update(self.fields)
        return dic

    def history(self):
        raise NotImplementedError

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
        changed=[]
        for field in fields:
            if field in self.triggers + ["changed", "storage"]:
                raise Exception(f"Field '{field}' cannot be externally set! Step:"+step.longname)
            changed.append(field)

        if "inner" !="keep":
            if not isinstance(step, Ins):
                raise Exception(f"Field 'inner' cannot be set except by step Ins! Step:"+step.longname)
            changed.append("inner")
        else:
            inner = self.inner

        if "stream" !="keep":
            changed.append("stream")
        else:
            stream = self.stream

        # Only update field uuids for the provided and changed ones!
        fields = self.fields.copy()
        changed_fields = {}
        # REMINDER: conversão saiu de _update() para self[] (que é o novo .field()) para conciliar laziness e aceitação de vetores e escalares
        for k, v in fields.items():
            kup = k.upper()
            if (kup not in fields) or fields[kup] is not v:
                changed_fields[kup] = v
        fields.update(changed_fields)
        uuid, uuids = evolve_id(self.uuid, self.uuids, step, changed_fields)

        return Data(uuid, uuids, step, inner, stream, **fields)

    @cached_property
    def eager(self):
        """Touch every lazy field by accessing all fields.

        Stream is kept intact"""
        for f in self:
            void = self[f]
        return self

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
            if name in self.fields:
                return self[name] < other[name]
        return Exception("Impossible to make comparisons. None of the comparable fields are available:", self.comparable)

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
        self.inner = newdata.inner
        self.stream = newdata.stream
        self.storage = newdata.storage
        self.parent_uuid = newdata.parent_uuid
        self.fields = newdata.fields

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

        # Is it a lazy field from storage?
        if isinstance(self.fields[key], UUID):
            if self.storage is None:
                raise Exception(f"Storage not set! Unable to fetch {key}/{self.fields[key]} generated by", self.step)
            print(">>>> fetching field:", key, self.fields[key])
            return self.storage.getfield(key)

        # Is it an already evaluated field?
        if not callable(self.fields[key]):
            if len(key)>1:
                return self.fields[key]

            # Format single-letter field according to capitalization.
            if key.islower():
                return mat2vec(self.fields[key.upper()])
            return self.fields[key]

        # It is a lazy field yet to be processed.
        try:
            with self.time_limit(self.maxtime), self.time() as elapsed:
                key = key.upper() if len(key) == 1 else key
                value = field_as_matrix(self.fields[key]())
            if key not in self.triggers:
                self.duration+=elapsed
            self.fields[key]=value
            return value
        except TimeoutException:
            self.mutate(Timeout(self.maxtime) <<self) #REMINDER None means interrupted
        except Exception as e:
            self.failure=self.step.translate(e)
            self.fields[key]=None#REMINDER None means interrupted

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

    def __iter__(self):
        return iter(self.fields)  # TODO quais ficam de fora mesmo?

    def __len__(self):
        return len(self.fields)


    def _name_(self):
        return self._uuid

    def _context_(self):
        return self.history ^ "names"

    @property
    @lru_cache()
    def ids_lst(self):  #TODO ainda precisa?
        return [self.uuids[name].id for name in self.names]

    @property
    @lru_cache()
    def ids_str(self):  #TODO ainda precisa?
        return ','.join(self.ids_lst)

    @lru_cache()
    def field_dump(self, name):  #TODO ainda precisa?
        """Cached compressed matrix for a given field.
        Useful for optimized persistence backends for Cache (e.g. more than one backend)."""
        return pack(self[name])

    @property
    @lru_cache()
    def names_str(self):  #TODO ainda precisa?
        return ','.join(self.names)

    @lru_cache()
    def _fetch_matrix(self, id):
        if self.storage_info is None:
            raise Exception(f"There is no storage set to fetch: {id})!")
        return 22222222222  # STORAGE_CONFIG['storages'][self.storage_info].fetch_matrix(id)  #TODO


    @cached_property
    def picklable(self):
        """Remove unpicklable parts."""
        return self.picklable_()[0]

    @cached_property
    def unpicklable(self):
        """Restore unpicklable parts."""
        return self.unpicklable_([{}])

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

    def __delitem__(self, key):
        # record destruction where needed
        from aiuna.delete import Del
        d = Del(field=key) << self
        self._uuid = d.uuid
        self.history = d.history

        # make destruction
        del self.uuids[key]
        del self._matrices[key]

        # REMINDER: invalidation seems not needed according to tests, doing it anyway...
        # invalidate all caches
        for attr in self.__dict__.values():
            if callable(attr) and hasattr(attr, "cacheclear"):
                attr.cacheclear()

    def __setitem__(self, key, value):
        # process mutation
        from aiuna.let import Let
        d = Let(field=key, value=value) << self

        # put mutation here
        self._uuid = d.uuid
        self.history = d.history
        self.uuids[key] = d.uuids[key]
        self.matrices[key] = d.matrices[key]

        # REMINDER: invalidation seems not needed according to tests, doing it anyway...
        # invalidate all caches
        for attr in self.__dict__.values():
            if callable(attr) and hasattr(attr, "cacheclear"):
                attr.cacheclear()

    # * ** -
    # @ cache
    # & | ^ // %
    # -d +d
    # ~ sample
    # REMINDER: the detailed History is unpredictable, so it is impossible to provide a useful plan() based on future steps
    # def plan(self, step):


class MissingField(Exception):
    pass


def untranslate_type(name):
    if isinstance(name, list):
        return name
    if name in ["real", "int"]:
        return "NUMERIC"
    else:
        raise Exception("Unknown type:", name)

