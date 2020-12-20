# Acessing a data field as a pandas DataFrame
from aiuna import *

d = dataset.data  # 'iris' is the default dataset
df = d.X_pd
print(df.head())
# ...

mycol = d.X_pd["petal length (cm)"]
print(mycol[:5])
# ...
