from functools import lru_cache


class Collection:

    @property
    def allfrozen(self):
        raise Exception('não sabemos se será preciso!')

    def _uuid_impl(self):
        raise Exception('não sabemos se será preciso!')

    def __init__(self, generator, finalizer, finite=True, debug_info=""):
        self.generator = generator
        self.finalizer = finalizer
        self.finite = finite
        self._last_args = ()
        self._finished = False
        self.debug_info = debug_info

    def __iter__(self):
        return self

    def __next__(self):
        try:
            print(self.debug_info, 'asks for next data...')
            data = next(self.generator)
            print('...and', self.debug_info, 'got', type(data))
            if type(data) == tuple:
                data, *self._last_args = data
            return data
        except StopIteration as e:
            print('...no more data available for', self.debug_info)
            self._finished = True
            raise e from None

    @property
    @lru_cache()
    def data(self):
        print(self.debug_info, 'asks for pendurado. Parametros:',
              self._last_args)
        if self.finite and not self._finished:
            raise Exception('Data object not ready!')
        return self.finalizer(*self._last_args)
