# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "numpy",
#   "scikit-learn",
#   "chardet"
# ] 
# ///

import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
import httpx
import time
import chardet

API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

if not AIPROXY_TOKEN:
    print("Error: AIPROXY_TOKEN environment variable is not set.")
    sys.exit(1)

def load_data(file_path):
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())  # Detect the encoding
        encoding = result['encoding']
        data = pd.read_csv(file_path, encoding=encoding)  # Use detected encoding
        return data
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        sys.exit(1)

def basic_analysis(data):
    summary = data.describe(include='all').to_dict()
    missing_values = data.isnull().sum().to_dict()
    return {"summary": summary, "missing_values": missing_values}

def outlier_detection(data):
    numeric_data = data.select_dtypes(include=np.number)
    z_scores = np.abs((numeric_data - numeric_data.mean()) / numeric_data.std())
    outliers = (z_scores > 3).sum().to_dict()
    return {"outliers": outliers}

def cluster_analysis(data):
    numeric_data = data.select_dtypes(include=np.number).dropna()
    if numeric_data.shape[1] >= 2:
        kmeans = KMeans(n_clusters=3, random_state=42)
        numeric_data['cluster'] = kmeans.fit_predict(numeric_data)
        sns.scatterplot(
            x=numeric_data.iloc[:, 0],
            y=numeric_data.iloc[:, 1],
            hue=numeric_data['cluster'],
            palette='viridis'
        )
        plt.title("Cluster Analysis")
        plt.savefig("clusters.png")
        plt.close()

def correlation_matrix(data):
    correlation = data.corr(numeric_only=True)
    sns.heatmap(correlation, annot=True, cmap='coolwarm')
    plt.title("Correlation Matrix")
    plt.savefig("correlation_matrix.png")
    plt.close()

def query_llm(prompt):
    headers = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    retries = 3
    for attempt in range(retries):
        try:
            response = httpx.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except httpx.RequestError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    print("Failed after multiple retries.")
    sys.exit(1)

def generate_story(data, analysis, charts):
    prompt = (
        "You are a creative storyteller. "
        "Craft a compelling narrative based on this dataset analysis:\n\n"
        f"Data Summary: {analysis['summary']}\n\n"
        f"Missing Values: {analysis['missing_values']}\n\n"
        f"Outlier Analysis: {analysis.get('outliers', 'No outliers detected')}\n\n"
        "The dataset contains information about 10,000 books. "
        "Create a narrative covering these points:\n"
        "- Describe the dataset as if introducing it to an audience.\n"
        "- Highlight interesting insights or anomalies discovered.\n"
        "- Use a conversational tone, as if explaining findings to a curious reader.\n"
        "- Reference these charts for visual support: correlation_matrix.png, clusters.png.\n"
        "End the story with a thought-provoking conclusion about the dataset and its implications."
    )
    return query_llm(prompt)

def save_readme(content):
    with open("README.md", "w") as f:
        f.write(content)

def visualize_data(data):
    correlation_matrix(data)
    cluster_analysis(data)

def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    file_path = sys.argv[1]
    data = load_data(file_path)

    analysis = basic_analysis(data)
    outliers = outlier_detection(data)
    combined_analysis = {**analysis, **outliers}

    visualize_data(data)

    story = generate_story(data, combined_analysis, ["correlation_matrix.png", "clusters.png"])
    save_readme(story)

if __name__ == "__main__":
    main()