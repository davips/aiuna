import numpy as np

from cruipto.compression import pack
from cruipto.uuid import UUID
from aiuna.content.data import Data
# Testes            ############################
from aiuna.history import History

matrices = {"X": np.array([[1, 2, 3, 4], [5, 6, 7, 8]]), "Y": np.array([[1, 2, 3, 4]]), "Xd": ['length', 'width'],
            "Yd": ['class'], "Xt": ["real", "real", "real", "real"], "Yt": [1, 2, 3, 4]}
uuids = {k: UUID(pack(v)) for k, v in matrices.items()}
data = Data(uuid=UUID(), uuids={"X": UUID(), "Y": UUID()}, history=History([]), **matrices)

print('OK', data)
