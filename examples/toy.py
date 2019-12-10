from cururu.persistence import DuplicateEntryException
from cururu.pickleserver import PickleServer
from pjdata.dataset import Dataset
from pjdata.data import Data
import numpy as np

# Testes            ############################
dataset = Dataset('iris', 'Beautiful description.',
                  X={'length': 'R', 'width': 'R'}, Y={'class': ['M', 'F']})
data = Data(dataset, X=np.asarray([1, 2, 3, 4, 5, 6, 7, 8]),
            Y=np.asarray([1, 2, 3, 4]))

# Teste de gravação ############################
print('Storing Data object...')
test = PickleServer()
try:
    test.store(data, ['X', 'Y'])
    print('ok!')
except DuplicateEntryException:
    print('Duplicate! Ignored.')

test.fetch(data, ['X', 'Y'])

# Teste de leitura ############################
print('Getting Data information-only objects...')
lista = test.list_by_name('ir')
print([d.dataset.name for d in lista])

print('Getting a complete Data object...')
data = test.fetch(lista[0], ['X', 'Y'])
print(data.X)
