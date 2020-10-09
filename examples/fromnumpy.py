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
