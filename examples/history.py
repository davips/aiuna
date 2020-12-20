# Checking history
from aiuna import *

d = dataset.data  # 'iris' is the default dataset
print(d.history)
# ...

del d["X"]
print(d.history)
# ...

d["Z"] = 42
print(d.Z, type(d.Z))
# ...

print(d.history)
# ...
