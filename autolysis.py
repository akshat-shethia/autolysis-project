# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "openai",
# ]
# ///

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai


AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise ValueError("Please set the AIPROXY_TOKEN environment variable.")


import sys

# Check if a file was provided
if len(sys.argv) != 2:
    print("Usage: uv run autolysis.py <filename.csv>")
    sys.exit(1)

# Get the filename
filename = sys.argv[1]

# Read the CSV file
try:
    data = pd.read_csv(filename)
    print(f"Successfully loaded {filename}")
except Exception as e:
    print(f"Error loading {filename}: {e}")
    sys.exit(1)

# Show basic info about the data
print("Dataset Overview:")
print(data.info())
print("First 5 Rows:")
print(data.head())

# Analyze missing values
print("\nMissing Values:")
missing_values = data.isnull().sum()
print(missing_values[missing_values > 0])

# Summary statistics for numerical columns
print("\nSummary Statistics:")
print(data.describe())

# Correlation matrix for numerical columns
print("\nCorrelation Matrix:")
numerical_columns = data.select_dtypes(include=["float64", "int64"])  # Select only numeric columns
correlation_matrix = numerical_columns.corr()
print(correlation_matrix)

# Save the correlation heatmap as a PNG file
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
plt.title("Correlation Matrix Heatmap")
plt.savefig("correlation_matrix.png")
print("Correlation heatmap saved as 'correlation_matrix.png'")