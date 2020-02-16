import json

from pjdata.aux.encoders import CustomJSONEncoder


class Printable:
    _pretty_printing = True

    def __init__(self, jsonable):
        self.jsonable = jsonable

    def enable_pretty_printing(self):
        self._pretty_printing = True

    def disable_pretty_printing(self):
        self._pretty_printing = False

    def __str__(self, depth=''):
        if not self._pretty_printing:
            js = json.dumps(self.jsonable, cls=CustomJSONEncoder,
                            sort_keys=False, indent=0, ensure_ascii=False)
            return js.replace('\n', '')

        js = json.dumps(self.jsonable, cls=CustomJSONEncoder,
                        sort_keys=False, indent=4, ensure_ascii=False)
        return js.replace('\n', '\n' + depth)

    __repr__ = __str__  # TODO: is this needed?
