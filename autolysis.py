# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "openai",
#   "scikit-learn"
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
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import silhouette_score

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

# Outlier detection using Isolation Forest
print("\nDetecting Outliers with Isolation Forest:")
isolation_forest = IsolationForest(random_state=42, contamination=0.05)
features = numerical_columns[["average_rating", "ratings_count", "ratings_5"]]
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
plt.savefig("isolation_forest_outliers.png")
print("Outlier visualization saved as 'isolation_forest_outliers.png'")

# Distribution plots for numerical columns
print("\nGenerating Feature Distributions:")
for column in numerical_columns.columns:
    plt.figure(figsize=(8, 4))
    sns.histplot(data[column], kde=True, bins=30)
    plt.title(f"Distribution of {column}")
    plt.savefig(f"distribution_{column}.png")
    print(f"Distribution plot saved as 'distribution_{column}.png'")

# Clustering Analysis with Elbow Method
print("\nPerforming Clustering Analysis:")
features = numerical_columns[["average_rating", "ratings_count", "ratings_5"]]
pca = PCA(n_components=2)
reduced_features = pca.fit_transform(features)

# Find optimal number of clusters
sse = []
silhouette_scores = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(reduced_features)
    sse.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(reduced_features, kmeans.labels_))

# Elbow plot
plt.figure(figsize=(8, 6))
plt.plot(range(2, 10), sse, marker='o')
plt.title("Elbow Method for Optimal Clusters")
plt.xlabel("Number of Clusters")
plt.ylabel("SSE")
plt.savefig("elbow_method.png")
print("Elbow plot saved as 'elbow_method.png'")

# Final K-Means clustering
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(reduced_features)

# Visualize clusters
plt.figure(figsize=(8, 6))
sns.scatterplot(x=reduced_features[:, 0], y=reduced_features[:, 1], hue=clusters, palette="viridis")
plt.title("Clustering Visualization")
plt.savefig("clustering_visualization.png")
print("Clustering visualization saved as 'clustering_visualization.png'")

# Feature Importance Analysis
print("\nFeature Importance Analysis:")
model = RandomForestRegressor(random_state=42)
X = numerical_columns.drop(columns=["average_rating"])
y = numerical_columns["average_rating"]
model.fit(X, y)
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
print(importances)

# Feature importance plot
plt.figure(figsize=(8, 6))
importances.plot(kind='bar')
plt.title("Feature Importance")
plt.savefig("feature_importance.png")
print("Feature importance plot saved as 'feature_importance.png'")

# Trend analysis over original_publication_year
print("\nAnalyzing Trends Over Time:")
time_data = data.groupby("original_publication_year")[["average_rating", "ratings_count"]].mean()
time_data.plot(figsize=(10, 6), title="Trends Over Time")
plt.xlabel("Year")
plt.ylabel("Values")
plt.savefig("trends_over_time.png")
print("Trends plot saved as 'trends_over_time.png'")

# Generate README.md
print("\nGenerating README.md...")
with open("README.md", "w") as f:
    f.write("# Automated Data Analysis\n\n")
    f.write("## Dataset Overview\n")
    f.write(f"- Number of rows: {data.shape[0]}\n")
    f.write(f"- Number of columns: {data.shape[1]}\n\n")
    f.write("## Analysis Highlights\n")
    f.write(f"- Missing values handled successfully.\n")
    f.write(f"- Number of outliers detected: {len(outliers)}\n")
    f.write(f"- Clustering visualization and elbow plot generated.\n")
    f.write(f"- Trends over time analyzed and plotted.\n")
    f.write(f"- Top correlations with 'average_rating':\n{correlation_matrix['average_rating'].sort_values(ascending=False).head(5)}\n")
    f.write("\n## Visualizations\n")
    f.write("- `correlation_matrix.png`\n")
    f.write("- `isolation_forest_outliers.png`\n")
    f.write("- `distribution_*.png`\n")
    f.write("- `elbow_method.png`\n")
    f.write("- `clustering_visualization.png`\n")
    f.write("- `feature_importance.png`\n")
    f.write("- `trends_over_time.png`\n")
print("README.md generated successfully!")