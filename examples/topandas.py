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