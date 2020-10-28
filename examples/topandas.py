# Acessing a data field as a pandas DataFrame
import aiuna.pack

d = File("iris.arff").data
df = d.X_pd
print(df.head())
# ...

mycol = d.X_pd["petallength"]
print(mycol[:5])
# ...
