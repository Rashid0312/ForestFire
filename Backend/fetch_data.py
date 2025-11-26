from ucimlrepo import fetch_ucirepo
import pandas as pd

# 1. Fetch the Forest Fires dataset using the UCI ML Repository ID (162)
forest_fires = fetch_ucirepo(id=162)

# 2. Get the features (X) and targets (y) as pandas DataFrames
X = forest_fires.data.features
y = forest_fires.data.targets

print("Forest Fire Dataset Fetched successfully!")
print("\nFeatures (X) Head:")
print(X.head())

print("\nTargets (y) Head:")
print(y.head())

# Optional: Save the data locally as a CSV for easy use later
# full_data = pd.concat([X, y], axis=1)
# full_data.to_csv('forest_fires_data.csv', index=False)
