# Automated Data Analysis with LLM Integration

## Project Overview
This project showcases an automated data analysis pipeline that uses machine learning, statistical methods, and AI-powered narratives to derive insights from structured datasets. The repository contains analyses for multiple datasets (`goodreads.csv`, `happiness.csv`, `media.csv`) and demonstrates a modular approach to handling data analysis tasks.

## Features
- Automated handling of missing values using statistical imputation.
- Detection of outliers using Isolation Forest.
- Clustering analysis using K-Means with visualized cluster distributions.
- Correlation analysis to identify relationships between variables.
- Dynamic storytelling using LLMs (GPT-4o-Mini).
- Clear and concise visualizations to support analysis insights.
- Modular script (`autolysis.py`) that dynamically adapts to different datasets.

## Datasets Analyzed
1. **Goodreads Dataset**:
   - Contains information about books, including ratings, reviews, and publication details.
   - **Key Insights**:
     - Strong positive correlation between `ratings_count` and `average_rating`.
     - Books with higher ratings tend to attract more reader engagement.
     - Outliers detected include books with polarizing reception.
   - Visualizations:
     - `correlation_matrix.png`
     - `outliers.png`
     - `clustering.png`

2. **Happiness Dataset**:
   - Global dataset measuring wellbeing metrics across countries and years.
   - **Key Insights**:
     - High GDP per capita correlates with better life satisfaction scores.
     - Strong social support and perceived freedom are key contributors to happiness.
     - Clustering analysis identified groups of countries with similar wellbeing patterns.
   - Visualizations:
     - `correlation_matrix.png`
     - `outliers.png`
     - `clustering.png`

3. **Media Dataset**:
   - Information about media content and user engagement metrics.
   - **Key Insights**:
     - Trends over time highlight shifts in user engagement.
     - Outliers detected for media items with extreme user interactions.
     - Clustering reveals distinct patterns in content consumption.
   - Visualizations:
     - `correlation_matrix.png`
     - `outliers.png`
     - `clustering.png`

## How It Works
1. **Input a Dataset**:
   - Provide any structured dataset (CSV format) as input to `autolysis.py`.

2. **Automated Analysis**:
   - Handles missing values based on data types (mean for numerical, mode for categorical).
   - Detects outliers and generates scatterplot visualizations.
   - Performs clustering to identify natural groupings within the data.
   - Analyzes trends over time if applicable.

3. **Narrative Generation**:
   - Uses an AI-powered LLM to generate a detailed README.md summarizing:
     - Data description
     - Analytical methods
     - Key insights
     - Implications and recommendations

4. **Output**:
   - Visualizations and README.md are saved in the corresponding directory (e.g., `goodreads/`, `happiness/`, `media/`).

## Repository Structure
```plaintext
├── autolysis.py                # Main script for automated analysis
├── LICENSE                     # MIT License
├── goodreads/                  # Output files for Goodreads dataset
│   ├── README.md               # Analysis summary
│   ├── correlation_matrix.png
│   ├── outliers.png
│   ├── clustering.png
├── happiness/                  # Output files for Happiness dataset
│   ├── README.md
│   ├── correlation_matrix.png
│   ├── outliers.png
│   ├── clustering.png
├── media/                      # Output files for Media dataset
│   ├── README.md
│   ├── correlation_matrix.png
│   ├── outliers.png
│   ├── clustering.png
