import json


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
        raise Exception(
            f'Problems materializing {name}@{path} with config\n{config}')


def _dict_to_transformer(dic):
    """Convert recursively a dict to a transformer."""
    if 'transformer' not in dic:
        raise Exception('Provided dict does not represent a transformer.')
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
