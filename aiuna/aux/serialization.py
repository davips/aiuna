import json

from pjdata.aux.customjsonencoder import CustomJSONEncoder


def serialize(obj):
    return json.dumps(obj, cls=CustomJSONEncoder, sort_keys=True, ensure_ascii=False)


def deserialize(txt):
    return _dict_to_component(json.loads(txt))


def serialized_to_int(txt):
    import hashlib
    return int(hashlib.md5(txt.encode()).hexdigest(), 16)


def materialize(name, path, config):
    """Instantiate a component.

    Returns
    -------
    A ready to use component.
    """
    class_ = _get_class(path, name)
    try:
        return class_(**config)
    except Exception as e:
        print(e)
        raise Exception(
            f'Problems materializing {name}@{path} with config\n{config}')


def _dict_to_component(dic):
    """Convert recursively a dict to a component."""
    if 'component' not in dic:
        raise Exception('Provided dict does not represent a component.')
    name, path = dic['_id'].split('@')
    cfg = dic['config']
    if 'component' in cfg:
        cfg['component'] = _dict_to_component(cfg['component'])

    return materialize(name, path, cfg)


def _get_class(module, class_name):
    import importlib
    module = importlib.import_module(module)
    class_ = getattr(module, class_name)
    return class_
