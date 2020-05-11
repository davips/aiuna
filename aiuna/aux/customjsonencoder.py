from json import JSONEncoder

import numpy as np


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if obj is not None:
            from pjdata.aux.uuid import UUID
            if isinstance(obj, np.ndarray):
                return str(obj)
            elif isinstance(obj, UUID):
                return obj.id
            elif not isinstance(
                    obj, (list, set, str, int, float, bytearray, bool)):
                return obj.jsonable

        return JSONEncoder.default(self, obj)
