import json

from pjdata.aux.encoders import CustomJSONEncoder


class Printable:
    _pretty_printing = True

    def __init__(self, jsonable):
        self.jsonable = jsonable

    def enable_pretty_printing(self):
        self._pretty_printing = True

    def disable_pretty_printing(self):
        self._pretty_printing = True

    def __str__(self, depth=''):
        if not self._pretty_printing:
            return super().__str__()

        js = json.dumps(self.jsonable, cls=CustomJSONEncoder,
                        sort_keys=True, indent=4)
        return js.replace('\n', '\n' + depth)

    __repr__ = __str__  # TODO: is this needed?
