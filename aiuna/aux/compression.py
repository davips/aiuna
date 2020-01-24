import _pickle as pickle

import lz4.frame as lz
import numpy as np
import zstandard as zs


# TODO: make a permanent representative dictionary and check if it
#  reduces compression time and size of textual info like transformations:
#  dict_data = zs.train_dictionary(131072, samples)
#  cctx = zs.ZstdCompressor(dict_data=dict_data)
#  cctx.compress(fast_reduced)


def pack_data(obj):
    if isinstance(obj, np.ndarray) and str(obj.dtype) == 'float64':
        h, w = obj.shape
        fast_reduced = lz.compress(obj.reshape(w * h), compression_level=1)
    else:
        pickled = pickle.dumps(obj)  # 1169_airlines explodes here with RAM < ?
        fast_reduced = lz.compress(b'Obj' + pickled, compression_level=1)
    cctx = zs.ZstdCompressor(threads=-1)
    return cctx.compress(fast_reduced)


def unpack_data(dump, w=None, h=None):
    cctx = zs.ZstdDecompressor()
    decompressed = cctx.decompress(dump)
    fast_decompressed = lz.decompress(decompressed)
    if fast_decompressed[:3] == b'Obj':
        return pickle.loads(fast_decompressed[3:])
    else:
        return np.reshape(np.frombuffer(fast_decompressed), newshape=(h, w))


def pack_object(obj):
    """
    Nondeterministic (fast) parallel compression!
    Due to multithreading, blosc is nondeterministic and useless for UUIDs.
    :param obj:
    :return:
    """
    import blosc
    pickled = pickle.dumps(obj)
    fast_reduced = lz.compress(pickled, compression_level=1)
    return blosc.compress(fast_reduced,
                          shuffle=blosc.NOSHUFFLE, cname='zstd', clevel=3)


def unpack_object(dump):
    import blosc
    decompressed = blosc.decompress(dump)
    fast_decompressed = lz.decompress(decompressed)
    return pickle.loads(fast_decompressed)
