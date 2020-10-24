from linalghelper import islazy
from transf.step import Step


class Leaf:
    """Contains a step or a dict, answers for both."""
    isleaf, _dict, _step = True, None, None

    def __init__(self, step):
        if isinstance(step, dict):
            self._dict = step
        else:
            self._step = step

    @property
    def asstep(self):
        if self._step is None:
            self._step = Step.fromdict(self._dict)
        # self._step = self._step() if lazy(self._step) else self._step
        return self._step

    @property
    def asdict(self):
        if self._dict is None:
            self._dict = self._step.asdict
        return self._dict

    def __getattr__(self, item):
        if item in ["asstep", "asdict"]:
            return super().__getattribute__(item)
        return getattr(self.asstep, item)

    def __getitem__(self, item):
        return self.asdict[item]

    def _asdict_(self):
        return self._dict
