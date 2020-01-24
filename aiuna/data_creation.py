import _pickle as pickle
import math

import arff
import pandas as pd
import sklearn.datasets as ds

from pjdata.aux.encoders import uuid
from pjdata.data import Data
from pjdata.dataset import Dataset


def read_arff(filename, target='class'):
    """
    Create Data from ARFF file.
    See read_data_frame().
    :param filename:
    :param target:
    :return:
    """
    file = open(filename, 'r')
    data = arff.load(file, encode_nominal=True)
    df = pd.DataFrame(data['data'],
                      columns=[attr[0] for attr in data['attributes']])
    file.close()
    return read_data_frame(df, filename, target)


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
    name = 'RndData-' + uuid(pickle.dumps((X, y)))
    dataset = Dataset(
        name, "rnd", X=enumerate(n_attributes * ['rnd']), Y=['class']
    )
    return Data(dataset, X=X, Y=as_column_vector(y))


def as_column_vector(vec):
    return vec.reshape(len(vec), 1)
