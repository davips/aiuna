# import traceback
#
#
# class asExceptionHandler:
#     def checked(self, f, exit_on_error):
#         """Error is different from failure."""
#
#         def func(data):
#             try:
#                 return f(data)
#             except Exception as e:
#                 msg = str(e)
#                 if "n_co, n_features)=" in msg:
#                     pass  # We can improve msgs here, or just pass it as failure as it is.
#                 else:
#                     # Handle errors, i.e. unpredictable failures.
#                     if "type object 'Root' has no attribute" in msg:
#                         msg = "Root data is the origin of all data and has no information: " + msg
#                     if exit_on_error:
#                         raise e
#                         # traceback.print_tb(e.__traceback__)
#                         # print(msg)
#                         # exit()
#                 return data.failed(self, msg)
#
#         return func
#
# # numpy.warnings.filterwarnings("ignore")
# # numpy.warnings.filterwarnings("always")
