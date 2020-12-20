# aiuna scientific data for the classroom
**WARNING: This project is still subject to major changes, e.g., in the next rewrite.**


<p><a href="https://commons.wikimedia.org/wiki/File:Bradypus.jpg#/media/Ficheiro:Bradypus.jpg"><img src="https://upload.wikimedia.org/wikipedia/commons/1/18/Bradypus.jpg" alt="Bradypus variegatus - By Stefan Laube - (Dreizehenfaultier (Bradypus infuscatus), Gatunsee, Republik Panama), Public Domain" width="180" height="240"></a></p>

# Installation

# Examples

<details>
<summary>Creating data from ARFF file</summary>
<p>

```python3
import aiuna.pack

d = File("iris.arff").data
print(d.Xd)
```

```
['sepallength', 'sepalwidth', 'petallength', 'petalwidth']
```
```python3

print(d.X[:5])
```

```
[[5.1 3.5 1.4 0.2]
 [4.9 3.  1.4 0.2]
 [4.7 3.2 1.3 0.2]
 [4.6 3.1 1.5 0.2]
 [5.  3.6 1.4 0.2]]
```
```python3

print(d.y[:5])
```

```
['Iris-setosa' 'Iris-setosa' 'Iris-setosa' 'Iris-setosa' 'Iris-setosa']
```
```python3

print(sorted(set(d.y)))
```

```
['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
```

</p>
</details>

<details>
<summary>Acessing a data field as a pandas DataFrame</summary>
<p>

```python3
import aiuna.pack

d = File("iris.arff").data
df = d.X_pd
print(df.head())
```

```
   sepallength  sepalwidth  petallength  petalwidth
0          5.1         3.5          1.4         0.2
1          4.9         3.0          1.4         0.2
2          4.7         3.2          1.3         0.2
3          4.6         3.1          1.5         0.2
4          5.0         3.6          1.4         0.2
```
```python3

mycol = d.X_pd["petallength"]
print(mycol[:5])
```

```
0    1.4
1    1.4
2    1.3
3    1.5
4    1.4
Name: petallength, dtype: float64
```

</p>
</details>

<details>
<summary>Creating data from numpy arrays</summary>
<p>

```python3
import aiuna.pack

X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d)
```

```
{
    "uuid": "2BKAfUOnmjvdGlHo75rEdEM",
    "uuids": {
        "X": "34fVnbLMCkye7mDVaFTKZ2D",
        "Y": "35Eugcis8RTjXNaUbYcY8oW",
        "failure": "00000000000000000000001",
        "timeout": "00000000000000000000001",
        "comparable": "00000000000000000000001"
    },
    "matrices": "X,Y"
}
```

</p>
</details>

<details>
<summary>Checking history</summary>
<p>

```python3
import aiuna.pack

X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d.history)
```

```
[
    {
        "id": "06o5LroHNEoS3NVwXptGF1G",
        "desc": {
            "name": "New",
            "path": "aiuna.new",
            "config": {
                "hashes": {
                    "X": "586962852295d584ec08e7214393f8b2",
                    "Y": "f043eb8b1ab0a9618ad1dc53a00d759e"
                }
            }
        }
    }
]
```
```python3

del d["X"]
print(d.history)
```

```
[
    {
        "id": "06o5LroHNEoS3NVwXptGF1G",
        "desc": {
            "name": "New",
            "path": "aiuna.new",
            "config": {
                "hashes": {
                    "X": "586962852295d584ec08e7214393f8b2",
                    "Y": "f043eb8b1ab0a9618ad1dc53a00d759e"
                }
            }
        }
    },
    {
        "id": "06LmOW1zKe8JV60yeoG7GAR",
        "desc": {
            "name": "Del",
            "path": "aiuna.delete",
            "config": {
                "field": "X"
            }
        }
    }
]
```
```python3

d["Z"] = 42
print(d.Z, type(d.Z))
```

```
[[42]] <class 'numpy.ndarray'>
```
```python3

print(d.history)
```

```
[
    {
        "id": "06o5LroHNEoS3NVwXptGF1G",
        "desc": {
            "name": "New",
            "path": "aiuna.new",
            "config": {
                "hashes": {
                    "X": "586962852295d584ec08e7214393f8b2",
                    "Y": "f043eb8b1ab0a9618ad1dc53a00d759e"
                }
            }
        }
    },
    {
        "id": "06LmOW1zKe8JV60yeoG7GAR",
        "desc": {
            "name": "Del",
            "path": "aiuna.delete",
            "config": {
                "field": "X"
            }
        }
    },
    {
        "id": "070PDPFt5DqkHjb7QQg4OIu",
        "desc": {
            "name": "Let",
            "path": "aiuna.let",
            "config": {
                "field": "Z",
                "value": 42
            }
        }
    }
]
```

</p>
</details>

# Grants

# History
The novel ideias presented here are a result of a years-long process of drafts, thinking, trial/error and rewrittings from scratch in several languages from Delphi, passing through Haskell, Java and Scala to Python. The fundamental concepts were lightly borrowed from basic category theory like algebraic data structures that permeate many recent tendencies in programming language design, data flow specification, Spark, among others. 
For more historical details, refer to https://github.com/davips/kururu
