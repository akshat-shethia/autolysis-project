# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "openai",
#   "scikit-learn",
#   "requests"
# ]
# ///

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import requests

# OpenAI Token Setup
AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise ValueError("Please set the AIPROXY_TOKEN environment variable.")

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

# Handle missing values
print("\nHandling Missing Values:")
for column in missing_values.index:
    if data[column].dtype in ["float64", "int64"]:  # Numerical columns
        data[column].fillna(data[column].mean(), inplace=True)
        print(f"Filled missing values in '{column}' with mean: {data[column].mean()}")
    elif data[column].dtype == "object":  # Categorical columns
        data[column].fillna(data[column].mode()[0], inplace=True)
        print(f"Filled missing values in '{column}' with mode: {data[column].mode()[0]}")

print("\nMissing values handled successfully!")

# Correlation matrix for numerical columns
print("\nCorrelation Matrix:")
numerical_columns = data.select_dtypes(
    include=["float64", "int64"]
)  # Select only numeric columns
correlation_matrix = numerical_columns.corr()
print(correlation_matrix)

# Save the correlation heatmap as a PNG file
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True,
            fmt=".2f", cmap="coolwarm", cbar=True)
plt.title("Correlation Matrix Heatmap")
out_dir = filename.split('.')[0]
os.makedirs(out_dir, exist_ok=True)
plt.savefig(f"{out_dir}/correlation_matrix.png")
print(f"Correlation heatmap saved as '{out_dir}/correlation_matrix.png'")

# Outlier detection using Isolation Forest
print("\nDetecting Outliers with Isolation Forest:")
isolation_forest = IsolationForest(random_state=42, contamination=0.05)
features = numerical_columns[["average_rating", "ratings_count"]]
isolation_forest.fit(features)

# Predict anomalies (1 for inliers, -1 for outliers)
predictions = isolation_forest.predict(features)
data["is_outlier"] = predictions
outliers = data[data["is_outlier"] == -1]

print(f"Number of outliers detected: {len(outliers)}")

# Visualize inliers vs. outliers
plt.figure(figsize=(8, 6))
sns.scatterplot(
    x=features["ratings_count"],
    y=features["average_rating"],
    hue=predictions,
    palette={1: "blue", -1: "red"},
    legend="full"
)
plt.title("Isolation Forest Outlier Detection")
plt.xlabel("Ratings Count")
plt.ylabel("Average Rating")
plt.savefig(f"{out_dir}/outliers.png")
print(f"Outlier visualization saved as '{out_dir}/outliers.png'")

# Clustering Analysis
print("\nPerforming Clustering Analysis:")
pca = PCA(n_components=2)
reduced_features = pca.fit_transform(features)
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(reduced_features)

# Visualize clusters
plt.figure(figsize=(8, 6))
sns.scatterplot(
    x=reduced_features[:, 0], y=reduced_features[:, 1], hue=clusters, palette="viridis")
plt.title("Clustering Visualization")
plt.savefig(f"{out_dir}/clustering.png")
print(f"Clustering visualization saved as '{out_dir}/clustering.png'")

# Use GPT-4o-Mini to narrate the story
print("\nGenerating README.md using GPT-4o-Mini...")
story_prompt = f"""
You are an expert data analyst. Write a story about the analysis of a dataset. Include:
1. A brief description of the dataset.
2. The types of analysis performed (missing values, outliers, clustering).
3. Key findings and insights.
4. Implications and suggestions based on the findings.

The dataset contains the following columns: {', '.join(data.columns)}.
The analysis included:
- Missing value handling.
- Correlation analysis.
- Outlier detection using Isolation Forest.
- Clustering using K-Means.

Provide the response in Markdown format.
"""

import requests

# Proxy API endpoint and headers
proxy_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}",
}

# Chat Completion Data
data = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "You are an expert data analyst."},
        {"role": "user", "content": story_prompt},
    ],
}

# API Request to the Proxy
response = requests.post(proxy_url, headers=headers, json=data)
if response.status_code == 200:
    readme_content = response.json()["choices"][0]["message"]["content"]
    with open(f"{out_dir}/README.md", "w") as f:
        f.write(readme_content)
    print(f"README.md generated and saved as '{out_dir}/README.md'")
else:
    print(f"Error: {response.status_code}, {response.text}")
