# aiuna scientific data for the classroom

<p><a href="https://commons.wikimedia.org/wiki/File:Bradypus.jpg#/media/Ficheiro:Bradypus.jpg"><img src="https://upload.wikimedia.org/wikipedia/commons/1/18/Bradypus.jpg" alt="Bradypus variegatus - By Stefan Laube - (Dreizehenfaultier (Bradypus infuscatus), Gatunsee, Republik Panama), Public Domain" width="180" height="240"></a></p>

# Installation

# Examples

**Creating data from ARFF file**

Code
```python3
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
```


**Acessing a data field as a pandas DataFrame**

Code
```python3
import aiuna  # <- auto import File
d = File("iris.arff").data
df = d.X_pd
print(df.head())
# sepallength  sepalwidth  petallength  petalwidth
# 0          5.1         3.5          1.4         0.2
# 1          4.9         3.0          1.4         0.2
# 2          4.7         3.2          1.3         0.2
# 3          4.6         3.1          1.5         0.2
# 4          5.0         3.6          1.4         0.2

mycol = d.X_pd["petallength"]
print(mycol[:5])
# 0    1.4
# 1    1.4
# 2    1.3
# 3    1.5
# 4    1.4
# Name: petallength, dtype: float64
```


**Creating data from numpy arrays**

Code
```python3
import aiuna  # <- auto import numpy as np and helper function new()
X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d)
# Output
# {
#     "uuid": "ëЪʁŝкçӖχƿȭōʎǴE",
#     "uuids": {
#         "X": "ĘQӕΘƵǔџĊȥοӳЀvý",
#         "Y": "ĘȡǏů8χίMЙһɵҪǐǒ"
#     },
#     "matrices": "X,Y"
# }
```

**Checking history**
import aiuna  # <- auto import new()
X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d.history)
del d["X"]
print(d.history)
# Output:
# [
#     {
#         "id": "06o5LroHNEoS3NVwXptGF1G",
#         "desc": {
#             "name": "New",
#             "path": "aiuna.new",
#             "config": {
#                 "hashes": {
#                     "X": "586962852295d584ec08e7214393f8b2",
#                     "Y": "f043eb8b1ab0a9618ad1dc53a00d759e"
#                 }
#             }
#         }
#     }
# ]
# [
#     {
#         "id": "06o5LroHNEoS3NVwXptGF1G",
#         "desc": {
#             "name": "New",
#             "path": "aiuna.new",
#             "config": {
#                 "hashes": {
#                     "X": "586962852295d584ec08e7214393f8b2",
#                     "Y": "f043eb8b1ab0a9618ad1dc53a00d759e"
#                 }
#             }
#         }
#     },
#     {
#         "id": "06LmOW1zKe8JV60yeoG7GAR",
#         "desc": {
#             "name": "Del",
#             "path": "aiuna.delete",
#             "config": {
#                 "field": "X"
#             }
#         }
#     }
# ]


# Grants

# History
The novel ideias presented here are a result of a years-long process of drafts, thinking, trial/error and rewrittings from scratch in several languages from Delphi, passing through Haskell, Java and Scala to Python. The fundamental concepts were lightly borrowed from basic category theory like algebraic data structures that permeate many recent tendencies in programming language design, data flow specification, Spark, among others. 
For more historical details, refer to https://github.com/davips/kururu
