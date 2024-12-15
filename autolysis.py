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
        # Use detected encoding
        data = pd.read_csv(file_path, encoding=encoding)
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
    z_scores = np.abs(
        (numeric_data - numeric_data.mean()) / numeric_data.std())
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
    plt.figure(figsize=(12, 10))  # Increased the figure size
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
            response = httpx.post(API_URL, headers=headers,
                                  json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except httpx.RequestError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    print("Failed after multiple retries.")
    sys.exit(1)


def generate_story(data, analysis, charts):
    prompt = (
        "You are an expert data analyst and a creative storyteller. "
        "Your task is to craft a compelling, well-structured narrative based on the analysis of a dataset. "
        "The story should be engaging, insightful, and appeal to a general audience interested in data-driven findings.\n\n"

        "### Analysis Details\n"
        f"#### Data Summary:\n{analysis['summary']}\n\n"
        f"#### Missing Values:\n{analysis['missing_values']}\n\n"
        f"#### Outlier Analysis:\n{analysis.get(
            'outliers', 'No significant outliers detected')}\n\n"

        "### Instructions for Writing the Story\n"
        "Using the analysis results provided above, narrate a story that includes the following components:\n\n"

        "1. **Introduction to the Dataset**:\n"
        "   - Briefly describe the dataset and its purpose as if introducing it to an audience.\n"
        "   - Highlight the significance of the data and what it represents without assuming its domain.\n\n"

        "2. **The Analytical Journey**:\n"
        "   - Explain the steps taken during the analysis in a logical sequence:\n"
        "     - Handling missing values.\n"
        "     - Detecting outliers or anomalies.\n"
        "     - Performing correlation analysis and identifying key relationships.\n"
        "     - Conducting clustering analysis to identify patterns or groupings.\n\n"

        "3. **Key Insights and Discoveries**:\n"
        "   - Highlight the most interesting findings uncovered during the analysis.\n"
        "   - Discuss trends, anomalies, or surprising relationships discovered in the data.\n"
        "   - Use storytelling techniques to make these findings relatable and impactful.\n\n"

        "4. **Visual Storytelling**:\n"
        "   - Reference the following charts to visually support your analysis and story:\n"
        "     - `correlation_matrix.png` (Correlation heatmap showing relationships between variables).\n"
        "     - `clusters.png` (Cluster analysis plot illustrating data groupings).\n"
        "   - Describe what these visuals reveal and connect them to the narrative.\n\n"

        "5. **Implications of the Findings**:\n"
        "   - Explain the broader implications of the findings.\n"
        "   - Offer actionable suggestions or insights based on the analysis.\n"
        "   - Discuss what stakeholders (e.g., businesses, researchers, policymakers) can do with these insights.\n\n"

        "6. **Conclusion**:\n"
        "   - End the story with a thought-provoking conclusion that ties together the findings.\n"
        "   - Reflect on the overall importance of analyzing datasets like this and how data-driven decisions "
        "can unlock meaningful insights.\n\n"

        "### Tone and Style\n"
        "- Use a conversational and engaging tone as if explaining the findings to a curious reader.\n"
        "- Avoid technical jargon unless necessary, and explain terms clearly.\n"
        "- Ensure the narrative flows logically and connects insights to visuals.\n\n"

        "Craft the story to be clear, concise, and captivating for a wide range of readers."
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

    story = generate_story(data, combined_analysis, [
                           "correlation_matrix.png", "clusters.png"])
    save_readme(story)


if __name__ == "__main__":
    main()
