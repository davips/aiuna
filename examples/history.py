# Checking history
import aiuna.pack

X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
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
