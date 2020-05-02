import _pickle as pickle
import math

import arff
import numpy as np
import pandas as pd
import sklearn.datasets as ds

from pjdata.aux import encoders
from pjdata.aux.compression import pack
from pjdata.aux.encoders import md5digest, digest2pretty, UUID
from pjdata.aux.serialization import serialize
from pjdata.data import Data
from pjdata.step.transformation import Transformation


def read_arff(filename, description='No description.'):
    """
    Create Data from ARFF file.

    Assume X,y classification task and last attribute as target.
    And that there were no transformations (history) on this Data.

    A short hash will be added to the name, to ensure unique names.
    Actually, the first collision is expected after 1M different datasets
    with the same name ( n = 2**(log(107**6, 2)/2) ).
    Since we already expect unique names like 'iris', and any transformed
    dataset is expected to enter the system through a transformer,
    1M should be safe enough. Ideally, a single 'iris' be will stored.
    In practice, no more than a dozen are expected.

    Parameters
    ----------
    filename
        path of the dataset
    description
        dataset description

    Returns
    -------
    Data object
    """
    # Load file.
    file = open(filename, 'r')
    data = arff.load(file, encode_nominal=False)
    file.close()

    # Extract attributes and targets.
    Arr = np.array(data['data'])
    Att = data['attributes'][0:-1]
    TgtAtt = data['attributes'][-1]

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
    uuids = {
        'X': UUID(md5digest(pack(X))), 'Y': UUID(md5digest(pack(Y))),
        'Xd': UUID(md5digest(pack(Xd))), 'Yd': UUID(md5digest(pack(Yd))),
        'Xt': UUID(md5digest(pack(Xt))), 'Yt': UUID(md5digest(pack(Yt)))
    }
    hashes = {k: v.id for k, v in uuids.items()}
    clean = filename.replace('.ARFF', '').replace('.arff', '')
    splitted = clean.split('/')
    digest = md5digest(serialize(hashes).encode())
    name_ = splitted[-1] + '_' + digest2pretty(digest)[:6]

    # Generate the first transformation of a Data object: being born.
    class FakeFile:
        name = 'File'
        path = 'pjml.tool.data.flow.file'
        config = {
            'name': filename.split('/')[-1],
            'path': '/'.join(splitted[:-1]) + '/',
            'description': description,
            'hashes': hashes
        }
        jsonable = {'_id': f'{name}@{path}', 'config': config}
        serialized = serialize(jsonable)
        uuid00 = UUID(serialized.encode())

    transformer = FakeFile()
    # File transformations are always represented as 'u', no matter which step.
    transformation = Transformation(transformer, 'u')
    return Data(uuid=UUID() + transformation.uuid00, uuids=uuids,
                history=[transformation], failure=None, frozen=False,
                X=X, Y=Y, Xt=Xt, Yt=Yt, Xd=Xd, Yd=Yd,
                name=name_, desc=description)


def translate_type(name):
    if isinstance(name, list):
        return name
    name = name.lower()
    if name in ['numeric', 'real', 'float']:
        return 'real'
    elif name in ['integer', 'int']:
        return 'int'
    else:
        raise Exception('Unknown type:', name)


def read_csv(filename, target='class'):
    """
    Create Data from CSV file.
    See read_data_frame().
    :param filename:
    :param target:
    :return:
    """
    df = pd.read_csv(filename)  # 1169_airlines explodes here with RAM < 6GiB
    return read_data_frame(df, filename, target)


def read_data_frame(df, filename, target='class'):
    """
    Assume X,y classification task.
    And that there were no transformations (history) on this Data.

    A short hash will be added to the name, to ensure unique names.
    Actually, the first collision is expected after 12M different datasets
    with the same name ( n = 2**(log(107**7, 2)/2) ).
    Since we already expect unique names like 'iris', and any transformed
    dataset is expected to enter the system through a transformer,
    12M should be safe enough. Ideally, a single 'iris' be will stored.
    In practice, no more than a dozen are expected.

    Parameters
    ----------
    filename
        path of the dataset
    target
        name of target attribute

    Returns
    -------
    Data object
    """
    Y = target and as_column_vector(df.pop(target).values.astype('float'))
    X = df.values.astype('float')  # Do not call this before setting Y!
    raise NotImplementedError

    uuid_ = uuid(pickle.dumps((X, Y)))
    name = filename.split('/')[-1] + '_' + uuid_[:7]
    dataset = Dataset(name, "descrip stub")
    return Data(dataset, X=X, Y=Y, Xd=list(df.columns), Yd=['class'])


# def read_csv(filename, target='class'):
#     """
#     Create Data from CSV file.
#     See read_data_frame().
#     :param filename:
#     :param target:
#     :return:
#     """
#     df = pd.read_csv(filename)  # 1169_airlines explodes here with RAM < 6GiB
#     return read_data_frame(df, filename, target)


# def read_data_frame(df, filename, target='class'):
#     """
#     Assume X,y classification task.
#     And that there were no transformations (history) on this Data.
#
#     A short hash will be added to the name, to ensure unique names.
#     Actually, the first collision is expected after 12M different datasets
#     with the same name ( n = 2**(log(107**7, 2)/2) ).
#     Since we already expect unique names like 'iris', and any transformed
#     dataset is expected to enter the system through a transformer,
#     12M should be safe enough. Ideally, a single 'iris' be will stored.
#     In practice, no more than a dozen are expected.
#
#     Parameters
#     ----------
#     df
#     filename
#         dataset of the dataset (if a path, dataset will be extracted)
#     target
#
#     Returns
#     -------
#     Data object
#     """
#     Y = target and as_column_vector(df.pop(target).values.astype('float'))
#     X = df.values.astype('float')  # Do not call this before setting Y!
#     uuid_ = uuid(pickle.dumps((X, Y)))
#     name = filename.split('/')[-1] + '_' + uuid_[:7]
#     dataset = Dataset(name, "descrip stub")
#     return Data(dataset, X=X, Y=Y, Xd=list(df.columns), Yd=['class'])

def random_classification_dataset(n_attributes, n_classes, n_instances):
    """
    ps. Assume X,y classification task.
    :param n_attributes:
    :param n_classes:
    :param n_instances:
    :return:
    """
    n = int(math.sqrt(2 * n_classes))
    X, y = ds.make_classification(n_samples=n_instances,
                                  n_features=n_attributes,
                                  n_classes=n_classes,
                                  n_informative=n + 1)
    raise NotImplementedError
    name = 'RndData-' + uuid(pickle.dumps((X, y)))
    dataset = Dataset(
        name, "rnd", X=enumerate(n_attributes * ['rnd']), Y=['class']
    )
    return Data(dataset, X=X, Y=as_column_vector(y))


def as_column_vector(vec):
    return vec.reshape(len(vec), 1)


def nominal_idxs(M):
    return [idx for idx, val in list(enumerate(M)) if isinstance(val, list)]
