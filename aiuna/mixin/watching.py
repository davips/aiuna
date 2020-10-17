# from aiuna.mixin.exceptionhandling import asExceptionHandler
# from aiuna.mixin.timing import withTiming, TimeoutException
# from transf.timeout import Timeout
#
#
# class withWatching(asExceptionHandler, withTiming):
#     def watched(self, f, exit_on_error, maxtime=None):
#         def func(data):
#             marked_data = data.update([], step_m=self)
#             try:
#                 with self.time_limit(maxtime), self.time() as t:
#                     outdata = self.checked(f, exit_on_error)(marked_data)
#                 outdata = outdata.update([], t_m=t)
#             except TimeoutException:  # TODO: isso vai sair daqui
#                 outdata = Timeout(maxtime).process(marked_data)
#             finally:
#                 outdata = marked_data.update([], step_m=None)  # ou deleta step_m
#             return outdata
#
#         return func
