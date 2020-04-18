import json

from pjdata import PRETTY_PRINTING  # Needed despite IDE warnings!


def enable_global_pretty_printing():
    global PRETTY_PRINTING
    PRETTY_PRINTING = True


def disable_global_pretty_printing():
    global PRETTY_PRINTING
    PRETTY_PRINTING = False
    print('Pretty printing disabled!')


class Printable:

    def __init__(self, jsonable):
        self.jsonable = jsonable
        self.pretty_printing = PRETTY_PRINTING

    def enable_pretty_printing(self):
        self.pretty_printing = True

    def disable_pretty_printing(self):
        self.pretty_printing = False

    def __str__(self, depth=''):
        from pjdata.step.transformation import Transformation
        from pjdata.aux.encoders import CustomJSONEncoder

        # Transformation has a heavy printing because of its serialized
        # Transformer. So we take its serialization directly and put the
        # transformation step during CustomJSONEncoder run.
        if isinstance(self, Transformation):
            jsonable = self
        else:
            jsonable = self.jsonable

        if not self.pretty_printing:
            js = json.dumps(jsonable, cls=CustomJSONEncoder,
                            sort_keys=False, indent=0, ensure_ascii=False)
            return js.replace('\n', '')

        js = json.dumps(jsonable, cls=CustomJSONEncoder,
                        sort_keys=False, indent=4, ensure_ascii=False)
        return js.replace('\n', '\n' + depth)

    __repr__ = __str__  # TODO: is this needed?
