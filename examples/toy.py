import numpy as np

from pjdata.data import Data

# Testes            ############################
data = Data(X=np.array([[1, 2, 3, 4], [5, 6, 7, 8]]),
            Y=np.array([[1, 2, 3, 4]]),
            Xd=['length', 'width'], Yd=['class'],
            name='flowers', desc='Beautiful description.')

print('OK')
