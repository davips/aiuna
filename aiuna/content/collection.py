from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Iterator, Callable, Union, Any, Tuple

import pjdata.content.data as d
import pjdata.types as t
from pjdata.aux.util import Property
from pjdata.content.content import Content


class Collection(Content):
    """ Evidently, a iterator cannot be shared between Collection objects!
    """

    @property
    def isfrozen(self):
        raise NotImplementedError("should it mean 'all frozen' or 'any frozen'?")  # <-- TODO
        # TODO: what happens when a frozen Data reach a Streamer? Would it be fooled by outdated fields?

    def _uuid_impl(self):
        return self.data.uuid

    def __init__(self,
                 iterator: Iterator,
                 finalizer: Callable[[Any], d.Data],
                 finite: bool = True,
                 debug_info: Optional[str] = None):
        super().__init__(jsonable={'some info to print about colls': None})  # <-- TODO

        # TODO: it is possible to restart a collection, but I am not sure it has any use. Code for that:
        #  if finite:
        #     iterator = cycle(chain(iterator, (x for x in [End])))
        self.iterator = iterator
        self.finalizer = finalizer
        self.finite = finite
        self._last_args = ()
        self._finished = False
        self.debug_info = debug_info

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self.debug_info:
                print()
            self.debug('asks for next data...')
            data = next(self.iterator)

            # TODO: the second part of restarting mode
            # if data is End:
            #     raise StopIteration

            self.debug('...and got', type(data), '\n')
            if isinstance(data, AccResult):
                self.debug('has', type(data.value), 'and', type(data.acc))
                data, *self._last_args = data.both
            return data
        except StopIteration as e:
            if self.debug_info:
                self.debug('...no more data available\n')
            self._finished = True
            raise e from None

    @property
    @lru_cache()
    def data(self):
        self.debug('asks for pendurado... Tipo:', type(self._last_args),
                       'Parametros:', self._last_args)
        self._check_consumption()
        result = self.finalizer(*self._last_args)
        self.debug('...got pendurado.')
        return result

    @property
    @lru_cache()
    def uuid(self):
        return self.data.uuid

    def _check_consumption(self) -> None:
        if self.finite and not self._finished:
            try:
                # Check consumed iterators, but not marked as ended.
                print(type(self.iterator), self.iterator)
                next(self.iterator)
                raise Exception('Data object not ready!')
            except StopIteration as e:
                pass

    def debug(self, *msg: Union[tuple, str]) -> None:
        if self.debug_info:
            print(self.debug_info, '>>>', *msg)

    # @property
    # def allfrozen(self):
    #     raise Exception('não sabemos se será preciso!')
    #

    # def restart(self):
    #     pass


@dataclass(frozen=True)
class AccResult:
    """Accumulator for iterators that send args to finalizer()."""
    value: Optional[t.Data] = None
    acc: Optional[t.Acc] = None

    @Property
    def both(self) -> Tuple[Optional[t.Data], Optional[t.Acc]]:
        return self.value, self.acc
