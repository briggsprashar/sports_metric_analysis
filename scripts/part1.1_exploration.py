from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Load database connection parameters from environment variables
# (renamed username variable to avoid conflict with Windows reserved words)
sql_username = os.getenv('POWERUSER')
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

sql_username

# Construct SQLAlchemy connection string for MySQL using pymysql driver
url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"
conn = create_engine(url_string)

# SQL query to retrieve the full dataset (no row limit applied)
sql_toexecute = """
  select *
  from research_experiment_refactor_test
"""
raw_data = pd.read_sql(sql_toexecute, conn)

####### PART 1: EXPLORING RAW DATASET ##########

# Normalize entries in 'metric' column by stripping whitespace and standardizing case
raw_data['metric'] = raw_data['metric'].str.strip().str.title()

### INFORMATION FROM RAW DATASET
print(">> INFORMATION FROM THE RAW DATASET: <<\n")

## 1.2.1 Count unique athletes
athlete_count = raw_data['playername'].nunique()
print(f"The total number of unique athletes in the raw data is {athlete_count}")

## 1.2.2 Count unique sports/teams
team_count = raw_data['team'].nunique()
print(f"The total number of unique sports/teams in the raw data is {team_count}")

## 1.2.3 Determine date range of data collection
# Ensure 'timestamp' column is in datetime format
raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])
# Identify earliest and latest dates
start_date = raw_data['timestamp'].min().date()
end_date = raw_data['timestamp'].max().date()
print(f"The available data ranges from {start_date} to {end_date} in the raw data.")

## 1.2.4 Identify data source with highest record count
# Count records per data source
source_counts = raw_data['data_source'].value_counts()
print(source_counts)
# Report the source with the most records
most_common_source = source_counts.idxmax()
most_common_count = source_counts.max()
print(f"The data source with the most records is {most_common_source} with {most_common_count} entries in the raw data.")

## 1.2.5 Check for invalid or missing athlete names
invalid_names = raw_data[raw_data['playername'].isnull() | (raw_data['playername'].str.strip() == '')]
print(f"Number of athletes with missing or invalid names in the raw: {len(invalid_names)}")

## 1.2.6 Count athletes with data from multiple sources
# Calculate number of unique sources per athlete
source_count = raw_data.groupby('playername')['data_source'].nunique()
# Filter athletes with data from 2 or more sources
multi_source_athletes = source_count[source_count >= 2]
print(f"Number of athletes that have data from multiple sources (2 or 3 systems) in the raw data: {len(multi_source_athletes)}")

### METRIC DISCOVERY AND SELECTION
print(">> METRIC DISCOVERY AND SELECTION: <<\n")

# 1.3.1 Explore metrics in 'hawkins' data source
hawkins_data = raw_data[raw_data['data_source'] == 'hawkins']
hawkins_metrics = hawkins_data['metric'].value_counts().head(10)
print("Top 10 most common metrics for Hawkins data:\n", hawkins_metrics)

# 1.3.2 Explore metrics in 'kinexon' data source
kinexon_data = raw_data[raw_data['data_source'] == 'kinexon']
kinexon_metrics = kinexon_data['metric'].value_counts().head(10)
print("Top 10 most common metrics for Kinexon data:\n", kinexon_metrics)

# 1.3.3 Explore metrics in 'vald' data source
vald_data = raw_data[raw_data['data_source'] == 'vald']
vald_metrics = vald_data['metric'].value_counts().head(10)
print("Top 10 most common metrics for Vald data:\n", vald_metrics)

# 1.3.4 Identify all unique metrics across sources
metric_list = raw_data['metric'].unique()
print("Unique metrics:")
print(metric_list)
print(f"Total number of unique metrics: {len(metric_list)}")

# Summarize record counts and date ranges for top metrics per data source
summary = raw_data.groupby(['data_source', 'metric']).agg(
    record_count=('timestamp', 'count'),
    start_date=('timestamp', 'min'),
    end_date=('timestamp', 'max')
).reset_index()

# Select top metric per source by record count
top_metrics = summary.sort_values(['data_source', 'record_count'], ascending=[True, False]) \
                     .groupby('data_source').head(1)

# Convert datetime to date only
top_metrics['start_date'] = top_metrics['start_date'].dt.date
top_metrics['end_date'] = top_metrics['end_date'].dt.date

print(top_metrics[['data_source', 'metric', 'record_count', 'start_date', 'end_date']])

## Save raw dataset locally (optional)
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)
output_path = os.path.join(raw_folder, "raw.csv")
raw_data.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")
