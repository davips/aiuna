# Creating data from ARFF file
from aiuna import *

d = file("iris.arff").data

print(d.Xd)
# ...

print(d.X[:5])
# ...

print(d.y[:5])
# ...

#print(d.y_pd.value_counts())
#...
