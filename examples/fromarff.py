import aiuna  # <- auto import File
d = File("iris.arff").data
print(d.Xd)
# Output:
# ['sepallength', 'sepalwidth', 'petallength', 'petalwidth']

print(d.X[:5])
# Output:
# [[5.1 3.5 1.4 0.2]
#  [4.9 3.  1.4 0.2]
#  [4.7 3.2 1.3 0.2]
#  [4.6 3.1 1.5 0.2]
#  [5.  3.6 1.4 0.2]]

print(d.y[:5])
# Output:
# ['Iris-setosa' 'Iris-setosa' 'Iris-setosa' 'Iris-setosa' 'Iris-setosa']

print(set(d.y))
# Output:
# {'Iris-setosa', 'Iris-virginica', 'Iris-versicolor'}