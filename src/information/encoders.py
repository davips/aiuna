import _pickle as pickle
import hashlib

import lz4.frame as lz


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


def enc(big, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                      'abcdefghijklmnopqrstuvwxyz'
                      'ÁÂÄÅÆÉÊËÍÎÏÐÑÓÔÖÚÛÜÝÞßáâäåæçéêëíîïðñóôöøúûüýþ'):
    """
    Encode an integer to base-X.
    The default is base107 since it is enough to represent MD5 as 19 chars.
    The selected alphabet contains only numbers and letters. Similar letters
    were arbitrarily removed.
    This alphabet is intended to be printable and seen as part of a single
    word by most linux terminals and editors.
    I would call this subset as the 'subset of the double_click_friendly chars'.

    The following list shows how the alphabet size relates to the number of
    necessary digits to represent the biggest MD5 number (2^128).
    The hexdigest alredy uses 32 digits, so we want less than that.
    Good choices for the alphabet size would be in the range 85-185, since
    values higher than 256 are outside latin1 range.

    alphabet-size number-of-digits comments
    2 128 # crude md5 as binary string
    16 32 # hexdigest as string
    24 28
    41 24 # reducing from 32 to 24 is kind of a improvement
    48 23
    57 22
    69 21
    85 20 # base64 library provides base85, but it is not double_click_friendly
    107 19 # super friendly (our default choice)
    139 18 # not terminator/intellij friendly
    185 17 # not double_click_friendly
    256 16 # would include lots of unprintable characters
    371 15 # 371 and beyond is outside a single byte and latin1
    566 14
    16-bit 4
    32-bit 2 # UTF-8?

    147 is the size of the largest subset of latin1 that is
    double_click_friendly. Latin1 is compatible with UTF-8 and extends ASCII.

    Example alphabets are given below:

    gnome-terminal friendly (147)  [\\ <- escaped slash]
#%&+,-./0123456789=?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_abcdefghijklmnopqrstuvwxyz
~ª²³µ·¹º¼½¾ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ

    gnome-terminal/terminator/intellij friendly (125)
#0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz
ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ

    gnome-terminal/terminator/intellij[ctrl+w] friendly (124)
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz
ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ

    gnome-terminal/terminator/intellij without _ and most similar chars (107)
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
ÁÂÄÅÆÉÊËÍÎÏÐÑÓÔÖÚÛÜÝÞßáâäåæçéêëíîïðñóôöøúûüýþ

    :param alphabet: string with allowed digits
    :param big: an integer, usually a big MD5-like one
    :return: string representing a base-107 number (or any other base,
    depending on the given alphabet length)"""
    l = len(alphabet)
    res = []
    while True:
        res.append(alphabet[big % l])
        big = big // l
        if big == 0:
            break
    return ''.join(res)[::-1]


def dec(digest, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                         'abcdefghijklmnopqrstuvwxyz'
                         'ÁÂÄÅÆÉÊËÍÎÏÐÑÓÔÖÚÛÜÝÞßáâäåæçéêëíîïðñóôöøúûüýþ'):
    """
    Decode digest from base-len(alphabet).
    See enc() for more info.
    :param digest:
    :param alphabet:
    :return:
    """
    res = 0
    last = len(digest) - 1
    base = len(alphabet)
    for i, d in enumerate(digest):
        res += alphabet.index(d) * pow(base, last - i)
    return res


def tiny_md5(hexdigest):
    """
    Converts hex MD5 representation (32 digits in base-16) to a friendly
    shorter one (19 digits in base-113).
    :param hexdigest:
    :return: string with 19 digits
    """
    return enc(int(hexdigest, 16))


def uuid(content, prefix='Ø'):
    """
    Generates a UUID for any reasonably finite universe.
    It is preferred to generate such hash on compressed data,
    since MD5 is much slower for bigger data than the compression itself.
    :param content: encoded content; it can be a packed object, a text, JSON,...
    :param prefix: adds a (preferably single character) prefix to the output,
     adding up to 20 characters
    :return: prefix + (18 or 19) characters
    """
    if content is None:
        return None
    return prefix + tiny_md5(hashlib.md5(content).hexdigest())
