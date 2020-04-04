from abc import ABC
from functools import lru_cache

from pjdata.mixin.identifyable import Identifyable
from pjdata.aux.serialization import serialize, deserialize


class Transformation(Identifyable, ABC):
    def __init__(self, transformer, step):
        """
        Immutable application or use of a Transformer.
        :param transformer: Transformer/Pipeline
        :param step: 'a'pply or 'u'se
        """
        # Precisei retirar referência ao transformer, para que pickle parasse
        # de dar problema ao carregar um objeto Data do PickleServer. Esse
        # problema começar após a unificação ML com CS, sobrescrenvendo
        # __new__ nos containeres. O erro acontecia quando o pickle tentava
        # recriar Containeres do histórico de Data, mas, por algum motivo
        # tentava fazê-lo sem transformers. Serializei config pelo mesmo motivo.
        if step is None:
            raise Exception(
                'Operation cannot be None! Hint: self._transformation() '
                'should be called only during apply() or use() steps!')
        self.serialized = transformer.serialized
        self.step = step
        self.name = transformer.name
        self.path = transformer.path
        self._config = serialize(transformer)

    @property
    @lru_cache()
    def config(self):
        return deserialize(self._config)


class NoTransformation(type):
    transformer = None
    step = None
    name = None
    path = None
    config = None
    from pjdata.aux.encoders import int2tiny
    uuid = 'T' + int2tiny(0)

    def __new__(cls, *args, **kwargs):
        raise Exception(
            'NoTransformation is a singleton and shouldn\'t be instantiated')

    def __bool__(self):
        return False



def serialize(obj):
    return json.dumps(obj, sort_keys=True)


def deserialize(txt):
    return _dict_to_transformer(json.loads(txt))


def serialized_to_int(txt):
    import hashlib
    return int(hashlib.md5(txt.encode()).hexdigest(), 16)


def materialize(name, path, config):
    """Instantiate a transformer.

    Returns
    -------
    A ready to use component.
    """
    class_ = _get_class(path, name)
    try:
        return class_(**config)
    except Exception as e:
        print(e)
        raise Exception(f'Problems materializing {name}@{path} with\n{config}')


def _dict_to_transformer(dic):
    """Convert recursively a dict to a transformer."""
    if 'id' not in dic:
        raise Exception(f'Provided dict does not represent a transformer {dic}')
    name, path = dic['id'].split('@')
    cfg = dic['config']
    if 'transformer' in cfg:
        cfg['transformer'] = _dict_to_transformer(cfg['transformer'])

    return materialize(name, path, cfg)


def _get_class(module, class_name):
    import importlib
    module = importlib.import_module(module)
    class_ = getattr(module, class_name)
    return class_
