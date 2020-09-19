# import aiuna.mixin.serialization as ser
#
# import cruipto.uuid as u
# import aiuna.transformer.transformer as tr
#
#
# class PHolder(tr.Transformer):  # TODO: Find a better name? Skiper?
#     """Placeholder for a component to appear in history but do nothing.
#
#     Optionally a transformation 'idholder_func' can be passed, e.g. to freeze data.
#     """
#
#     ispholder = True
#
#     def __init__(self, component: t.Union[str, ser.withSerialization], *args):
#         self._uuid = u.UUID.identity
#         super().__init__(component)
#
#     def _transform_impl(self, data: t.Data) -> t.Result:
#         return {}
#
#     def _uuid_impl(self):
#         return self._uuid
