<details>
<summary>Creating data from ARFF file</summary>
<p>

```python3
# Creating data from ARFF file
import aiuna.pack

d = File("iris.arff").data
print(d.Xd)
```

```bash
['sepallength', 'sepalwidth', 'petallength', 'petalwidth']
```
```python3

print(d.X[:5])
```

```bash
[[5.1 3.5 1.4 0.2]
 [4.9 3.  1.4 0.2]
 [4.7 3.2 1.3 0.2]
 [4.6 3.1 1.5 0.2]
 [5.  3.6 1.4 0.2]]
```
```python3

print(d.y[:5])
```

```bash
['Iris-setosa' 'Iris-setosa' 'Iris-setosa' 'Iris-setosa' 'Iris-setosa']
```
```python3

print(set(d.y))
```

```bash
{'Iris-setosa', 'Iris-virginica', 'Iris-versicolor'}
```
```python3

```

```bash
```

</p>
</details>
<details>
<summary>Acessing a data field as a pandas DataFrame</summary>
<p>

```python3
# Acessing a data field as a pandas DataFrame
import aiuna.pack

d = File("iris.arff").data
df = d.X_pd
print(df.head())
```

```bash
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

```bash
0    1.4
1    1.4
2    1.3
3    1.5
4    1.4
Name: petallength, dtype: float64
```
```python3

```

```bash
```

</p>
</details>
<details>
<summary>Creating data from numpy arrays</summary>
<p>

```python3
# Creating data from numpy arrays
import aiuna.pack

X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d)
```

```bash
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
```python3

```

```bash
```

</p>
</details>
<details>
<summary>Checking history</summary>
<p>

```python3
# Checking history
import aiuna.pack

X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d.history)
```

```bash
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

```bash
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

```bash
[[42]] <class 'numpy.ndarray'>
```
```python3

print(d.history)
```

```bash
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
```python3

```

```bash
```

</p>
</details>