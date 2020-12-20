# Creating data from numpy arrays
from aiuna import *
import numpy as np

X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d)
# ...
