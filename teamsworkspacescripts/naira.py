"""
naira.py — Part 1: Database Exploration and Metric Discovery
Author: Naira Khergiani
Description: Connects to MySQL, previews data, summarizes metrics, and generates PDF summary.
"""

import pandas as pd
from sqlalchemy import create_engine # type: ignore
from dotenv import load_dotenv # type: ignore
import os
# Removed unused plotting and datetime imports: matplotlib, seaborn, datetime, timedelta
# Import PyMuPDF (module may be available as 'fitz' or 'pymupdf' depending on environment)
try:
    import fitz  # type: ignore[reportMissingImports]
except Exception:
    import pymupdf as fitz  # type: ignore[reportMissingImports]

# Load environment variables
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Connect to database
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}") # type: ignore

# Query first 10 rows
query = "SELECT * FROM research_experiment_refactor_test LIMIT 10;"
df = pd.read_sql(query, engine) # type: ignore

# Summary statistics
unique_athletes = df['playername'].nunique()
teams_count = df['team'].nunique()
date_range = (df['timestamp'].min(), df['timestamp'].max())
source_counts = df['data_source'].value_counts()

# Metric discovery for Hawkins, Kinexon, Vald
metric_queries = {
    "Hawkins": "SELECT metric, COUNT(*) as count FROM research_experiment_refactor_test WHERE data_source = 'Hawkins' GROUP BY metric ORDER BY count DESC LIMIT 10;",
    "Kinexon": "SELECT metric, COUNT(*) as count FROM research_experiment_refactor_test WHERE data_source = 'Kinexon' GROUP BY metric ORDER BY count DESC LIMIT 10;",
    "Vald": "SELECT metric, COUNT(*) as count FROM research_experiment_refactor_test WHERE data_source = 'Vald' GROUP BY metric ORDER BY count DESC LIMIT 10;"
}

metric_results = {}
for source, query in metric_queries.items():
    metric_results[source] = pd.read_sql(query, engine) # type: ignore

# Create PDF summary
from typing import Any, cast
doc = cast(Any, fitz.open()) # type: ignore
# Use typing.cast to explicitly set page to Any so static type checkers accept PyMuPDF Page methods
page = cast(Any, doc.new_page()) # type: ignore

# Title
page.insert_text((72, 72), "Part 1 Summary: Database Exploration", fontsize=16)

# Connection confirmation
page.insert_text((72, 100), "✓ Successfully connected to MySQL database.", fontsize=12)

# First 10 rows preview
page.insert_text((72, 130), "First 10 Rows Preview:", fontsize=12)
preview_text = df.head(10).to_string(index=False) # type: ignore
page.insert_text((72, 150), preview_text, fontsize=8)

# Summary statistics
summary_y = 350
page.insert_text((72, summary_y), "Summary Statistics:", fontsize=12)
summary_y += 20
page.insert_text((72, summary_y), f"- Number of unique athletes: {unique_athletes}", fontsize=10)
summary_y += 15
page.insert_text((72, summary_y), f"- Number of teams: {teams_count}", fontsize=10)
summary_y += 15
page.insert_text((72, summary_y), f"- Date range: {date_range[0]} to {date_range[1]}", fontsize=10)
summary_y += 25
page.insert_text((72, summary_y), "Record Count by Data Source:", fontsize=10)
summary_y += 15
for source, count in source_counts.items():
    page.insert_text((90, summary_y), f"{source}: {count}", fontsize=10)
    summary_y += 15

# Metric discovery results
summary_y += 25
page.insert_text((72, summary_y), "Top 10 Metrics by Source:", fontsize=12)
summary_y += 20
for source, df_metrics in metric_results.items(): # type: ignore
    page.insert_text((72, summary_y), f"{source} Metrics:", fontsize=10)
    summary_y += 15
    for _, row in df_metrics.iterrows(): # type: ignore
        page.insert_text((90, summary_y), f"{row['metric']}: {row['count']}", fontsize=10)
        summary_y += 15
    summary_y += 10

# Save PDF
doc.save("part1_summary.pdf")
doc.close()

# Close connection
engine.dispose() # type: ignore

print("PDF summary 'part1_summary.pdf' created successfully with metric discovery.")

