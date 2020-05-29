from dataclasses import dataclass
from functools import lru_cache
from itertools import cycle

# class End(type):
#     pass
from pjdata.data import Data
from pjdata.specialdata import NoData


class Collection:
    """

    Evidently, a iterator cannot be shared between Collection objects!
    """

    def __init__(self, iterator, finalizer, finite=True, debug_info=None):
        # TODO: it is possible to restart a collection, but I am not sure it
        #  has any use.
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
        if self.debug_info:
            self.debug('asks for pendurado... Tipo:', type(self._last_args),
                       'Parametros:', self._last_args)

        # TODO: precisei parar de checar para voltar a funcionar!!
        # if self.finite and not self._finished:
        #     raise Exception('Data object not ready!')

        result = self.finalizer(*self._last_args)
        self.debug('...got pendurado.')
        return result

    # def join(self):
    #     """Call this when this is a twin of an ended iterator."""
    #     # TODO: smells like gambiarra
    #     self._finished = True
    #     try:
    #         next(self)
    #         next(self.iterator)
    #     except:
    #         pass

    def debug(self, *msg):
        if self.debug_info:
            print(self.debug_info, '>>>', *msg)

    # @property
    # def allfrozen(self):
    #     raise Exception('não sabemos se será preciso!')
    #
    # def _uuid_impl(self):
    #     raise Exception('não sabemos se será preciso!')
    # def restart(self):
    #     pass


@dataclass(frozen=True)
class AccResult:
    """Accumulator for iterators that send args to finalizer()."""
    value: Data = NoData
    acc: list = None

    @property
    def both(self):
        return self.value, self.acc
