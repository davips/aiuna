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
