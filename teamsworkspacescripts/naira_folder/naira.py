"""
naira.py — Metrics Exploration Script
Author: Naira Khergiani
Purpose: Load team CSV data, compute summary metrics, and print results.
"""

import pandas as pd

# Path to my CSV file inside my naira_folder 
csv_path = "teamsworkspacescripts/naira_folder/data/sixmetricsclass 3.csv"

# Load the dataset
df = pd.read_csv(csv_path) # type: ignore

print("\n✓ CSV successfully loaded.")
print(f"Rows: {len(df)}, Columns: {len(df.columns)}\n")

# Preview first few rows
print("Preview of dataset:")
print(df.head(10))

# Compute basic metrics
print("\nSummary Statistics:")
print(df.describe(include='all'))

# Example: Count players, events, or categories
if "playername" in df.columns:
    print("\nUnique players:", df["playername"].nunique())

if "event" in df.columns:
    print("Unique events:", df["event"].nunique())

print("\n✓ Metrics computation complete.")

