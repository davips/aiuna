import json
import math
from hashlib import md5

# noinspection PyUnresolvedReferences
import arff
import numpy as np
import sklearn.datasets as ds

from aiuna.mixin.linalghelper import fields2matrices
from aiuna.new import New


def new(**fields):
    matrices = dict(fields2matrices(fields).items())
    hashes = {k: md5(json.dumps(v, sort_keys=True, ensure_ascii=False).encode() if isinstance(v, list) else v.tobytes()).hexdigest() for k, v in matrices.items()}
    return New(hashes, **matrices).data


# noinspection PyPep8Naming
def read_arff(filename):
    """
    Create  from ARFF file.

    Assume X,y classification task and last attribute as target.

    Parameters
    ----------
    filename
        path of the dataset

    Returns
    -------
    (dict of matrix hashes and metainfo)
    """
    # Load file.
    file = open(filename, "r")
    dic = arff.load(file, encode_nominal=False)  # ['description', 'relation', 'attributes', 'data']
    name = dic["relation"]
    description = dic["description"]
    file.close()

    # Extract attributes and targets.
    Arr = np.array(dic["data"])
    Att = dic["attributes"][0:-1]
    TgtAtt = dic["attributes"][-1]

    # Extract X values (numeric when possible), descriptions and types.
    X = Arr[:, 0:-1]
    Xd = [tup[0] for tup in Att]
    Xt = [translate_type(tup[1]) for tup in Att]
    if len(nominal_idxs(Xt)) == 0:
        X = X.astype(float)

    # Extract Y values (assumes categorical), descriptions and types.
    Y = np.ascontiguousarray(Arr[:, -1].reshape((Arr.shape[0], 1)))
    Yd = [TgtAtt[0]]
    Yt = [translate_type(TgtAtt[1])]

    # Calculate pseudo-unique hash for X and Y, and a pseudo-unique name.
    matrices = {"X": X, "Y": Y, "Xd": Xd, "Yd": Yd, "Xt": Xt, "Yt": Yt}
    original_hashes = {k: md5(json.dumps(v, sort_keys=True, ensure_ascii=False).encode() if isinstance(v, list) else v.tobytes()).hexdigest() for k, v in matrices.items()}
    return {"dataset": name, "description": description, "matrices": matrices, "original_hashes": original_hashes}


def translate_type(name):
    if isinstance(name, list):
        return name
    name = name.lower()
    if name in ["numeric", "real", "float"]:
        return "real"
    elif name in ["integer", "int"]:
        return "int"
    else:
        raise Exception("Unknown type:", name)


def read_csv(filename, target='class'):
    raise NotImplementedError
    df = pd.read_csv(filename)  # 1169_airlines explodes here with RAM < 6GiB
    return read_data_frame(df, filename, target)


def random_classification_dataset(n_attributes, n_classes, n_instances):
    """
    Generate a syntetic Data object for a classification task.
    :param n_attributes:
    :param n_classes:
    :param n_instances:
    :return:
    """
    n = int(math.sqrt(2 * n_classes))
    X, y = ds.make_classification(
        n_samples=n_instances, n_features=n_attributes, n_classes=n_classes, n_informative=n + 1
    )
    raise NotImplementedError
    name = "RndData-" + uuid(pickle.dumps((X, y)))
    dataset = Dataset(name, "rnd", X=enumerate(n_attributes * ["rnd"]), Y=["class"])
    return Data(dataset, X=X, Y=as_column_vector(y))


def as_column_vector(vec):
    return vec.reshape(len(vec), 1)


def nominal_idxs(M):
    return [idx for idx, val in list(enumerate(M)) if isinstance(val, list)]
