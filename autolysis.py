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


