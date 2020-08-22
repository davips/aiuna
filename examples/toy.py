import numpy as np

from pjdata.aux.compression import pack
from pjdata.aux.uuid import UUID
from pjdata.content.data import Data
# Testes            ############################
from pjdata.history import History

matrices = {"X": np.array([[1, 2, 3, 4], [5, 6, 7, 8]]), "Y": np.array([[1, 2, 3, 4]]), "Xd": ['length', 'width'],
            "Yd": ['class'], "Xt": ["real", "real", "real", "real"], "Yt": [1, 2, 3, 4]}
uuids = {k: UUID(pack(v)) for k, v in matrices.items()}
data = Data(
    uuid=UUID(), uuids={"X": UUID(), "Y": UUID()},
    failure=None, frozen=False, history=History([]), hollow=False, stream=None,
    **matrices
)

print('OK', data)
