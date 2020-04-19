import _pickle as pickle

import lz4.frame as lz
import numpy as np
import zstandard as zs

# TODO: make a permanent representative dictionary and check if it
#  reduces compression time and size of textual info like transformations.
from pjdata.aux.encoders import intlist2bytes, bytes2intlist


def pack_data(obj):
    if isinstance(obj, np.ndarray) and str(obj.dtype) == 'float64':
        h, w = obj.shape
        b = intlist2bytes(obj.shape)
        fast_reduced = b + lz.compress(obj.reshape(w * h), compression_level=1)
    else:
        pickled = pickle.dumps(obj)  # 1169_airlines explodes here with RAM < ?
        fast_reduced = b'ObjeobjE' + lz.compress(pickled, compression_level=1)
    cctx = zs.ZstdCompressor(threads=-1)
    return cctx.compress(fast_reduced)


def unpack_data(dump):
    cctx = zs.ZstdDecompressor()
    decompressed = cctx.decompress(dump)
    if decompressed[:8] == b'ObjeobjE':
        fast_decompressed = lz.decompress(decompressed[8:])
        return pickle.loads(fast_decompressed)
    else:
        fast_decompressed = lz.decompress(decompressed[8:])
        [h, w] = bytes2intlist(decompressed[:8])
        return np.reshape(np.frombuffer(fast_decompressed), newshape=(h, w))

# def pack_object(obj):  #blosc is buggy
#     """
#     Nondeterministic (fast) parallel compression!
#     Due to multithreading, blosc is nondeterministic and useless for UUIDs.
#     :param obj:
#     :return:
#     """
#     import blosc
#     pickled = pickle.dumps(obj)
#     fast_reduced = lz.compress(pickled, compression_level=1)
#     return blosc.compress(fast_reduced,
#                           shuffle=blosc.NOSHUFFLE, cname='zstd', clevel=3)


# def unpack_object(dump):  #blosc is buggy
#     import blosc
#     decompressed = blosc.decompress(dump)
#     fast_decompressed = lz.decompress(decompressed)
#     return pickle.loads(fast_decompressed)
