from pjdata.aux.decorator import classproperty
from pjdata.aux.serialization import serialize
from pjdata.aux.util import Property
from pjdata.aux.uuid import UUID
from pjdata.mixin.serialization import WithSerialization


class FakeFile(WithSerialization):
    path = 'pjml.tool.data.flow.file'

    def __init__(self, filename, description, original_hashes):
        clean = filename.replace('.ARFF', '').replace('.arff', '')
        split = clean.split('/')
        config = {
            'name': filename.split('/')[-1],
            'path': '/'.join(split[:-1]) + '/',
            'description': description,
            'hashes': original_hashes
        }
        transformer_info = {'_id': f'{self.name}@{self.path}', 'config': config}
        self.serialized = serialize({'info': transformer_info, 'enhance': True, 'model': True})
        self.cfserialized = serialize(transformer_info)

    def _cfuuid_impl(self):
        return UUID(self.cfserialized.encode())

    def _name_impl(self):
        return 'File'

    def _uuid_impl(self):
        return UUID(self.serialized.encode())
