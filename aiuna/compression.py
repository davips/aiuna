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


import _pickle as pickle
import json
from functools import lru_cache
from random import random

import lz4.frame as lz
import numpy as np
import zstandard as zs
# Things that should be calculated only once.
# ##################################################
from akangatu.transf.config import safety
# TODO: make a permanent representative dictionary and check if it
#  reduces compression time and size of textual info like transformations.
from garoupa.encoders import integers2bytes, bytes2integers


###@lru_cache()
def compression_dict():  # TODO: update dictionary
    txt_comming_from_a_file_for_training_of_compressor = "aasfdkjgd kajgsdf af kajgakjsg fkajgs df\n" * 653
    samples = [
        (str(random()) + s).encode()
        for s in txt_comming_from_a_file_for_training_of_compressor.split("\n")
    ]
    return zs.train_dictionary(dict_size=99999999, samples=samples, threads=-1)

# ##################################################

class HashableBinary:
    def __init__(self, n, obj):
        self.n = n
        self.obj = obj

    def __hash__(self):
        return self.n


def fpack(data, field):
    return memopack(HashableBinary(data.uuids[field].n, data[field]))


# ###@lru_cache()
def memopack(hashable_binary):
    return pack(hashable_binary.obj)


#compression_lock = new_lock()


def pack(obj):

        cctx = zs.ZstdCompressor(threads=-1)
        cctxdic = zs.ZstdCompressor(threads=-1, dict_data=compression_dict(), write_dict_id=False)

        cctxdec = zs.ZstdDecompressor()
        cctxdicdec = zs.ZstdDecompressor(dict_data=compression_dict())

    # with safety():
        if isinstance(obj, np.ndarray) and str(obj.dtype) == "float64" and len(obj.shape) == 2:
            # X, ...
            h, w = obj.shape
            fast_reduced = lz.compress(obj.reshape(w * h), compression_level=1)
            header = integers2bytes(obj.shape)
            return b"F" + header + cctx.compress(fast_reduced)
        elif isinstance(obj, (list, set, str, int, float, bytearray, bool)):
            # steps, ...
            js = json.dumps(obj, sort_keys=True, ensure_ascii=False)
            return b"J" + cctx.compress(js.encode())
        elif isinstance(obj, str):
            return b"T" + cctxdic.compress(obj.encode())  # b'T'+0s==1409286144
        elif isinstance(obj, bytes):
            fast_reduced = lz.compress(obj, compression_level=1)
            return b"B" + cctx.compress(fast_reduced)
        elif callable(obj):
            raise Exception("Cannot compress callable", type(obj))
        else:
            # print(f"Unknown type {type(obj)}{'-' + str(obj.dtype) if 'ndarray' in str(type(obj)) else ''} to compress, using pickle...")
            # categorical ndarrays, ...
            pickled = pickle.dumps(obj)  # 1169_airlines explodes here with RAM < ?
            fast_reduced = lz.compress(pickled, compression_level=1)
            return b"P" + cctx.compress(fast_reduced)  # b'P'+0s==1342177280


def unpack(dump_with_header):
        cctx = zs.ZstdCompressor(threads=-1)
        cctxdic = zs.ZstdCompressor(threads=-1, dict_data=compression_dict(), write_dict_id=False)

        cctxdec = zs.ZstdDecompressor()
        cctxdicdec = zs.ZstdDecompressor(dict_data=compression_dict())

    # with safety():
        header = dump_with_header[:1]
        dump = dump_with_header[1:]
        if header == b"P":
            decompressed = lz.decompress(cctxdec.decompress(dump))
            return pickle.loads(decompressed)
        elif header == b"T":
            return cctxdicdec.decompress(dump).decode()
        elif header == b"B":
            return lz.decompress(cctxdec.decompress(dump))
        elif header == b"F":
            header = dump_with_header[1:9]
            dump = dump_with_header[9:]
            decompressed = lz.decompress(cctxdec.decompress(dump))
            [h, w] = bytes2integers(header)
            return np.reshape(np.frombuffer(decompressed), newshape=(h, w))
        elif header == b"J":
            return json.loads(cctxdec.decompress(dump).decode())
        else:
            raise Exception("Unknown compression format:", header, dump[:300])

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
#                       shuffle=blosc.NOSHUFFLE, cname='zstd', clevel=3)


# def unpack_object(dump):  #blosc is buggy
#     import blosc
#     decompressed = blosc.decompress(dump)
#     fast_decompressed = lz.decompress(decompressed)
#     return pickle.loads(fast_decompressed)
