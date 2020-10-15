# Creating data from ARFF file
import aiuna.pack

d = File("iris.arff").data
print(d.Xd)
# ...

print(d.X[:5])
# ...

print(d.y[:5])
# ...

print(set(d.y))
# ...
