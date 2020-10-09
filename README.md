# aiuna scientific data for the classroom

<p><a href="https://commons.wikimedia.org/wiki/File:Bradypus.jpg#/media/Ficheiro:Bradypus.jpg"><img src="https://upload.wikimedia.org/wikipedia/commons/1/18/Bradypus.jpg" alt="Bradypus variegatus - By Stefan Laube - (Dreizehenfaultier (Bradypus infuscatus), Gatunsee, Republik Panama), Public Domain" width="180" height="240"></a></p>

# Installation

# Examples

**Creating data from numpy arrays**

Code
```python3
import aiuna  # <- auto import numpy as np and helper function new()


X = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])
y = np.array([0,
              1,
              1])
d = new(X=X, y=y)

print(d)
```
Output

    {
        "uuid": "ëЪʁŝкçӖχƿȭōʎǴE",
        "uuids": {
            "X": "ĘQӕΘƵǔџĊȥοӳЀvý",
            "Y": "ĘȡǏů8χίMЙһɵҪǐǒ"
        },
          "comparable": "",
          "matrices": "X,Y"
    }



# Grants

# History
The novel ideias presented here are a result of a years-long process of drafts, thinking, trial/error and rewrittings from scratch in several languages from Delphi, passing through Haskell, Java and Scala to Python. The fundamental concepts were lightly borrowed from basic category theory like algebraic data structures that permeate many recent tendencies in programming language design, data flow specification, Spark, among others. 
For more historical details, refer to https://github.com/davips/kururu
