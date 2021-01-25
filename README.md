![test](https://github.com/davips/aiuna/workflows/test/badge.svg)
[![codecov](https://codecov.io/gh/davips/aiuna/branch/main/graph/badge.svg)](https://codecov.io/gh/davips/aiuna)

# aiuna scientific data for the classroom
**WARNING: This project is still subject to major changes, e.g., in the next rewrite.**

<p><a href="https://commons.wikimedia.org/wiki/File:Bradypus.jpg#/media/Ficheiro:Bradypus.jpg"><img src="https://upload.wikimedia.org/wikipedia/commons/1/18/Bradypus.jpg" alt="Bradypus variegatus - By Stefan Laube - (Dreizehenfaultier (Bradypus infuscatus), Gatunsee, Republik Panama), Public Domain" width="180" height="240"></a></p>

# Installation

# Examples

**Creating data from ARFF file**
<details>
<p>

```python3
from aiuna import *

d = file("iris.arff").data

print(d.Xd)
"""
['sepallength', 'sepalwidth', 'petallength', 'petalwidth']
"""
```

```python3

print(d.X[:5])
"""
[[5.1 3.5 1.4 0.2]
 [4.9 3.  1.4 0.2]
 [4.7 3.2 1.3 0.2]
 [4.6 3.1 1.5 0.2]
 [5.  3.6 1.4 0.2]]
"""
```

```python3

print(d.y[:5])
"""
['Iris-setosa' 'Iris-setosa' 'Iris-setosa' 'Iris-setosa' 'Iris-setosa']
"""
```

```python3

#print(d.y_pd.value_counts())
#...

```


</p>
</details>

**cessing a data field as a pandas DataFrame**
<details>
<p>

```python3
#from aiuna import *

#d = dataset.data  # 'iris' is the default dataset
#df = d.X_pd
#print(df.head())
#...

#mycol = d.X_pd["petal length (cm)"]
#print(mycol[:5])
#...

```


</p>
</details>

**Creating data from numpy arrays**
<details>
<p>

```python3
from aiuna import *
import numpy as np

X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 1])
d = new(X=X, y=y)
print(d)
"""
{
    "uuid": "06NLDM4mLEMrHPOaJvEBqdo",
    "uuids": {
        "changed": "3Sc2JjUPMlnNtlq3qdx9Afy",
        "X": "13zbQMwRwU3WB8IjMGaXbtf",
        "Y": "1IkmDz3ATFmgzeYnzygvwDu"
    },
    "step": {
        "id": "06NLDM4mLEMrHPOT2pd5lzo",
        "desc": {
            "name": "New",
            "path": "aiuna.step.new",
            "config": {
                "hashes": {
                    "X": "586962852295d584ec08e7214393f8b2",
                    "Y": "f043eb8b1ab0a9618ad1dc53a00d759e"
                }
            }
        }
    },
    "changed": [
        "X",
        "Y"
    ],
    "X": [
        "[[1 2 3]",
        " [4 5 6]",
        " [7 8 9]]"
    ],
    "Y": [
        "[[0]",
        " [1]",
        " [1]]"
    ]
}
"""
```


</p>
</details>

**Checking history**
<details>
<p>

```python3
from aiuna import *

d = dataset.data  # 'iris' is the default dataset
print(d.history)
"""
{
    "02o8BsNH0fhOYFF6JqxwaLF": {
        "name": "New",
        "path": "aiuna.step.new",
        "config": {
            "hashes": {
                "X": "19b2d27779bc2d2444c11f5cc24c98ee",
                "Y": "8baa54c6c205d73f99bc1215b7d46c9c",
                "Xd": "0af9062dccbecaa0524ac71978aa79d3",
                "Yd": "04ceed329f7c3eb43f93efd981fde313",
                "Xt": "60d4f429fcd642bbaf1d976002479ea2",
                "Yt": "4660adc31e2c25d02cb751dcb96ecfd3"
            }
        }
    }
}
"""
```

```python3

del d["X"]
print(d.history)
"""
{
    "02o8BsNH0fhOYFF6JqxwaLF": {
        "name": "New",
        "path": "aiuna.step.new",
        "config": {
            "hashes": {
                "X": "19b2d27779bc2d2444c11f5cc24c98ee",
                "Y": "8baa54c6c205d73f99bc1215b7d46c9c",
                "Xd": "0af9062dccbecaa0524ac71978aa79d3",
                "Yd": "04ceed329f7c3eb43f93efd981fde313",
                "Xt": "60d4f429fcd642bbaf1d976002479ea2",
                "Yt": "4660adc31e2c25d02cb751dcb96ecfd3"
            }
        }
    },
    "06fV1rbQVC1WfPelDNTxEPI": {
        "name": "Del",
        "path": "aiuna.step.delete",
        "config": {
            "field": "X"
        }
    }
}
"""
```

```python3

d["Z"] = 42
print(d.Z, type(d.Z))
"""
[[42]] <class 'numpy.ndarray'>
"""
```

```python3

print(d.history)
"""
{
    "02o8BsNH0fhOYFF6JqxwaLF": {
        "name": "New",
        "path": "aiuna.step.new",
        "config": {
            "hashes": {
                "X": "19b2d27779bc2d2444c11f5cc24c98ee",
                "Y": "8baa54c6c205d73f99bc1215b7d46c9c",
                "Xd": "0af9062dccbecaa0524ac71978aa79d3",
                "Yd": "04ceed329f7c3eb43f93efd981fde313",
                "Xt": "60d4f429fcd642bbaf1d976002479ea2",
                "Yt": "4660adc31e2c25d02cb751dcb96ecfd3"
            }
        }
    },
    "06fV1rbQVC1WfPelDNTxEPI": {
        "name": "Del",
        "path": "aiuna.step.delete",
        "config": {
            "field": "X"
        }
    },
    "05eIWbfCJS7vWJsXBXjoUAh": {
        "name": "Let",
        "path": "aiuna.step.let",
        "config": {
            "field": "Z",
            "value": 42
        }
    }
}
"""
```


</p>
</details>

# Grants
Part of the effort spent in the present code was kindly supported by Fapesp under supervision of 
Prof. André C. P. L. F. de Carvalho at CEPID-CeMEAI (Grants 2013/07375-0 – 2019/01735-0).


# History
The novel ideias presented here are a result of a years-long
process of drafts, thinking, trial/error and rewrittings from scratch in several languages from Delphi, passing through Haskell, Java and Scala to Python - including frustration with well stablished libraries at the time. The fundamental concepts were lightly borrowed from basic category theory concepts like algebraic data structures that permeate many recent tendencies, e.g., in programming language design.

For more details, refer to https://github.com/davips/kururu
