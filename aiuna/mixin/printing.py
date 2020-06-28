import json
from abc import abstractmethod
from functools import cached_property

def enable_global_pretty_printing():
    PRETTY_PRINTING = True


def disable_global_pretty_printing():
    PRETTY_PRINTING = False


class withPrinting:
    """Mixin class to deal with string printing style"""
    pretty_printing = False
    @cached_property
    def jsonable(self):
        return self._jsonable_impl()

    @abstractmethod
    def _jsonable_impl(self):
        pass

    def enable_pretty_printing(self):
        self.pretty_printing = True

    def disable_pretty_printing(self):
        self.pretty_printing = False

    def __str__(self, depth):
        from pjdata.transformer.transformer import Transformer
        from pjdata.aux.customjsonencoder import CustomJSONEncoder

        jsonable = self.jsonable
        if isinstance(self, Transformer):
            # Taking component out of string for a better printing.
            # jsonable = self.jsonable.copy()
            # jsonable["component"] = json.loads(jsonable["component"])
            jsonable = self.jsonable  # TODO: improve this

        if self.pretty_printing:
            js_str = json.dumps(jsonable, cls=CustomJSONEncoder, sort_keys=False, indent=4, ensure_ascii=False,)
            return js_str.replace("\n", "\n" + depth)

        js_str = json.dumps(jsonable, cls=CustomJSONEncoder, sort_keys=False, indent=0, ensure_ascii=False,)
        return js_str.replace("\n", "")

    __repr__ = __str__
