# Testes            ############################
from storage.persistence import DuplicateEntryException
from storage.pickleserver import PickleServer

test = PickleServer()

# Teste de gravação ############################
from information.dataset import Dataset
from information.data import Data
from information.history import History
from information.transformation import Transformation

dataset = Dataset('iris', 'Beautiful description.',
                  X={'length': 'R', 'width': 'R'}, Y={'class': ['M', 'F']})
data = Data(dataset, X=[1, 2, 3, 4, 5, 6, 7, 8], Y=[1, 2, 3, 4])
try:
    print('Storing Data object...')
    test.store(data, ['X', 'Y'])
    print('ok!')
except DuplicateEntryException:
    print('Duplicate! Ignored.')

test.fetch(data, ['X', 'Y'])


# Teste de leitura ############################
print('Getting Data information-only objects...')
lista = test.list_by_name('ir')
print([d.dataset.name for d in lista])

print('Getting a complete Data...')
data = test.fetch(lista[0], ['X', 'Y'])
print(data.X)