import arff
import numpy as np
import pandas as pd
import sklearn.datasets as ds

from information.data import Data
from information.dataset import Dataset
from information.encoders import uuid, pack_object


def read_arff(file, target=None):
    """
    Create Data from ARFF file.
    See read_data_frame().
    :param file:
    :param target:
    :return:
    """
    data = arff.load(open(file, 'r'), encode_nominal=True)
    df = pd.DataFrame(data['data'],
                      columns=[attr[0] for attr in data['attributes']])
    return Data.read_data_frame(df, file, target)


def read_csv(file, target=None):
    """
    Create Data from CSV file.
    See read_data_frame().
    :param file:
    :param target:
    :return:
    """
    df = pd.read_csv(file)  # 1169_airlines explodes here with RAM < 6GiB
    return Data.read_data_frame(df, file, target)


def read_data_frame(df, file, target=None):
    """
    ps. Assume X,y classification task.
    Andd that there was no transformations (history) on this Data.
    :param df:
    :param file: dataset of the dataset (if a path, dataset will be extracted)
    :param target:
    :return:
    """
    name = file.split('/')[-1]
    Y = target and Data._as_column_vector(
        df.pop(target).values.astype('float'))
    X = df.values.astype('float')  # Do not call this before setting Y!
    dataset = Dataset(name, "descrip stub", X=list(df.columns), Y=['class'])
    return Data(dataset, X=X, Y=Y)


def random_classification(n_attributes, n_classes, n_instances):
    """
    ps. Assume X,y classification task.
    :param n_attributes:
    :param n_classes:
    :param n_instances:
    :return:
    """
    X, y = ds.make_classification(n_samples=n_instances,
                                  n_features=n_attributes,
                                  n_classes=n_classes,
                                  n_informative=int(
                                      np.sqrt(2 * n_classes)) + 1)
    name = 'Random-' + uuid(pack_object((X, y)))
    dataset = Dataset(
        name, "rnd", X=enumerate(n_attributes * ['rnd']), Y=['class']
    )
    return Data(dataset, X=X, Y=Data._as_column_vector(y))


def as_column_vector(vec):
    return vec.reshape(len(vec), 1)
