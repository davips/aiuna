#  Copyright (c) 2020. Davi Pereira dos Santos
#  This file is part of the aiuna project.
#  Please respect the license - more about this in the section (*) below.
#
#  aiuna is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  aiuna is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with aiuna.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.


# import traceback
#
#
# class asExceptionHandler:
#     def checked(self, f, exit_on_error):
#     """Error is different from failure."""
#
#     def func(data):
#         try:
#             return f(data)
#         except Exception as e:
#             msg = str(e)
#             if "n_co, n_features)=" in msg:
#                 pass  # We can improve msgs here, or just pass it as failure as it is.
#             else:
#                 # Handle errors, i.e. unpredictable failures.
#                 if "type object 'Root' has no attribute" in msg:
#                     msg = "Root data is the origin of all data and has no information: " + msg
#                 if exit_on_error:
#                     raise e
#                     # traceback.print_tb(e.__traceback__)
#                     # print(msg)
#                     # exit()
#             return data.failed(self, msg)
#
#     return func
#
# # numpy.warnings.filterwarnings("ignore")
# # numpy.warnings.filterwarnings("always")
