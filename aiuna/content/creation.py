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


import json
import math
from hashlib import md5

# noinspection PyUnresolvedReferences
import arff
import numpy as np
import sklearn.datasets as ds

from akangatu.linalghelper import fields2matrices


def mathash(k, v):
    try:
        dump = json.dumps(v, sort_keys=True, ensure_ascii=False).encode() if isinstance(v, list) else v.tobytes()
        return md5(dump).hexdigest()
    except TypeError as e:
        print(f"Cannot calculate hash for {k} with value {v}")
        exit()


def hashes_mats(fields):
    """Calculate pseudo-unique hash for each field."""
    matrices = dict(fields2matrices(fields).items())
    return {k: mathash(k, v) for k, v in matrices.items()}, matrices


def new(**fields):
    from aiuna.step.new import New
    hashes, matrices = hashes_mats(fields)
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

    original_hashes, matrices = hashes_mats({"X": X, "Y": Y, "Xd": Xd, "Yd": Yd, "Xt": Xt, "Yt": Yt})
    return {"dataset": name, "description": description, "matrices": matrices, "original_hashes": original_hashes}


def translate_type(name):
    if isinstance(name, list):
        return name
    name = name.lower()
    if name in ["numeric", "real"] or name.startswith("float"):
        return "real"
    elif name.startswith("int"):
        return "int"
    else:
        raise Exception("Unknown type:", name)


def read_csv(filename, target='class'):
    raise NotImplementedError
    # df = pd.read_csv(filename)  # 1169_airlines explodes here with RAM < 6GiB
    # return read_data_frame(df, filename, target)


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
    # name = "RndData-" + uuid(pickle.dumps((X, y)))
    # dataset = Dataset(name, "rnd", X=enumerate(n_attributes * ["rnd"]), Y=["class"])
    # return Data(dataset, X=X, Y=as_column_vector(y))


def as_column_vector(vec):
    return vec.reshape(len(vec), 1)


def nominal_idxs(M):
    return [idx for idx, val in list(enumerate(M)) if isinstance(val, list)]
