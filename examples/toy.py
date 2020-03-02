import numpy as np

from pjdata.data import Data
from pjdata.dataset import Dataset

# Testes            ############################
dataset = Dataset('flowers', 'Beautiful description.')
                  # X={'length': 'R', 'width': 'R'}, Y={'class': ['M', 'F']})
data = Data(dataset, X=np.array([[1, 2, 3, 4], [5, 6, 7, 8]]),
            Y=np.array([[1, 2, 3, 4]]))

print('OK')
