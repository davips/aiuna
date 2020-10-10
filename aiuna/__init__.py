import numpy

from .creation import new
from ._version import __version__  # noqa: ignore
from .content.root import Root
from .file import File
from .content.data import Data

# noinspection PyUnusedName
PRETTY_PRINTING = True

# ================================================================================================
# Autoimport main classes and default vars to ease assignment and didactic start for data/d, e.g.:
#       d << File(...)
#       d << File(...) << d

# vars
__builtins__["Root"] = __builtins__["d"] = __builtins__["data"] = Root

# modules
__builtins__["np"] = numpy

# helper functions and classes
autoimport = [new, Data, File]

# autoimporting...
for item in autoimport:
    __builtins__[item.__name__] = item

# ================================================================================================
