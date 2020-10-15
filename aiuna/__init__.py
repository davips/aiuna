# import numpy
# # TODO:check circular imports when "import aiuna" is not used
# from ._version import __version__  # noqa: ignore
# from .content.data import Data
# from .content.root import Root
# from .creation import new
# from .file import File
#
# # noinspection PyUnusedName
# PRETTY_PRINTING = True
#
# # ================================================================================================
# # Autoimport main classes and default vars to ease assignment and didactic start for data/d, e.g.:
# #       d << File(...)
# #       d << File(...) << d
#
# # vars
# __builtins__["Root"] = __builtins__["d"] = __builtins__["data"] = Root
#
# # modules
# __builtins__["np"] = numpy
#
# # helper functions and classes
# autoimport = [new, Data, File]
#
# # autoimporting...
# for item in autoimport:
#     __builtins__[item.__name__] = item
#
# # ================================================================================================
