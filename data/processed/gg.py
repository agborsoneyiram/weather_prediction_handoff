import pandas as pd

df = pd.read_csv("features.csv")

print(df['timestamp'].min())
print(df['timestamp'].max())