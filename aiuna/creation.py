import math

import arff
import numpy as np
import pjdata.mixin.linalghelper as li
import sklearn.datasets as ds
from pjdata.aux.compression import pack
from pjdata.aux.uuid import UUID
from pjdata.content.data import Data
from pjdata.content.specialdata import NoData
from pjdata.fakefile import FakeFile
from pjdata.history import History
from pjdata.transformer.enhancer import DSStep


class FakeStep(DSStep):
    def _info_impl(self, data):
        pass

    def _transform_impl(self, nodata):
        return NoData


class Step(DSStep):
    def _info_impl(self, data):
        pass

    def _transform_impl(self, nodata):
        return NoData


def read_arff(filename):
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
    (dict of matrix hashes, Data object)
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
    uuids = {k: UUID(pack(v)) for k, v in matrices.items()}
    original_hashes = {k: v.id for k, v in uuids.items()}

    # # old, unique, name...
    # name_ = splitted[-1] + '_' + enc(
    #     md5_int(serialize(original_hashes).encode()))[:6]

    # Generate the first transformation of a Data object: being born.
    faketransformer = FakeStep(FakeFile(filename, original_hashes))
    uuid, uuids = li.evolve_id(UUID(), {}, [faketransformer], matrices)

    # Create a temporary Data object (i.e. with a fake history).
    data = Data(
        history=History([faketransformer]),
        failure=None,
        frozen=False,
        hollow=False,
        stream=None,
        storage_info=None,
        uuid=uuid,
        uuids=uuids,
        X=X,
        Y=Y,
        Xt=Xt,
        Yt=Yt,
        Xd=Xd,
        Yd=Yd,
    )

    # Patch the Data object with the real transformer and history.
    transformer = Step(FakeFile(filename, original_hashes))
    data.history = History([transformer])

    return original_hashes, data, name, description


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


# def read_csv(filename, target="class"):
#     """
#     Create Data from CSV file.
#     See read_data_frame().
#     :param filename:
#     :param target:
#     :return:
#     """
#     df = pd.read_csv(filename)  # 1169_airlines explodes here with RAM < 6GiB
#     return read_data_frame(df, filename, target)


# def read_data_frame(df, filename, target="class"):
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
#     filename
#         path of the dataset
#     target
#         name of target attribute
#
#     Returns
#     -------
#     Data object
#     """
#     Y = target and as_column_vector(df.pop(target).values.astype("float"))
#     X = df.values.astype("float")  # Do not call this before setting Y!
#     raise NotImplementedError
#
#     uuid_ = uuid(pickle.dumps((X, Y)))
#     name = filename.split("/")[-1] + "_" + uuid_[:7]
#     dataset = Dataset(name, "descrip stub")
#     return Data(dataset, X=X, Y=Y, Xd=list(df.columns), Yd=["class"])


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
