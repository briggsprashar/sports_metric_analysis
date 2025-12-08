

import pymysql
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# mapping for database connection
# need to rename the username since it conflicts with a reserved word windows

sql_username = os.getenv('POWERUSER')
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

sql_username

url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"

conn = create_engine(url_string)

# retrieves only the first 50 rows from the dataset
sql_toexecute = """
  select *
  from research_experiment_refactor_test
  ; 
  """

response = pd.read_sql(sql_toexecute, conn)
print(response.head(50))

## Downloading the data locally
# Ensure 'raw' folder exists
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

#Save result to CSV in 'raw' folder
output_path = os.path.join(raw_folder, "query_result.csv")
response.to_csv(output_path, index=False)

print(f"Query result saved to: {output_path}")

from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# mapping for database connection
# need to rename the username since it conflicts with a reserved word windows

sql_username = os.getenv('POWERUSER')
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

sql_username

url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"

conn = create_engine(url_string)

# remove limit 100000; to get full dataset
sql_toexecute = """
  select *
  from research_experiment_refactor_test 
  ; 
  """

raw_data = pd.read_sql(sql_toexecute, conn)

## Downloading the data locally (optional) remove # below to enable
# Ensure 'raw' folder exists
# raw_folder = "raw"
# os.makedirs(raw_folder, exist_ok=True)

##Save result to CSV in 'raw' folder
# output_path = os.path.join(raw_folder, "query_result.csv")
# response.to_csv(output_path, index=False)
# print(f"Query result saved to: {output_path}")

####### PART 1: EXPLORING RAW DATASET ##########
# Standardizing responses in 'metric' column to ensure consistency (found out responses have upper/lower issues)
raw_data['metric'] = raw_data['metric'].str.strip().str.title()


### INFORMATION FROM RAW DATASET
## Counting unique numbers of athletes
athlete_count = raw_data['playername'].nunique()
print(f"The total number of unique athletes in the raw data is {athlete_count}")

## Counting unique numbers of sports/teams
team_count = raw_data['team'].nunique()
print(f"The total number of unique sports/teams in the raw data is {team_count}")


## Date range of data collection
# Ensure timestamp column is in datetime format
raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])

# Get the earliest and latest dates
start_date = raw_data['timestamp'].min().date()
end_date = raw_data['timestamp'].max().date()

# Print the date range
print(f"The available data ranges from {start_date} to {end_date} in the raw data.")


## Hightest Number of Records per data source 
# Counting the number of records per data source
source_counts = raw_data['data_source'].value_counts()

# Print the counts
print(source_counts)

# Print the source with the most records
most_common_source = source_counts.idxmax()
most_common_count = source_counts.max()
print(f"The data source with the most records is {most_common_source} with {most_common_count} entries in the raw data.")


## Checking for Invalid or Missing names in 'playername' column
# Check for missing or invalid athlete names
invalid_names = raw_data[raw_data['playername'].isnull() | (raw_data['playername'].str.strip() == '')]

# Print the number of invalid entries
print(f"Number of athletes with missing or invalid names in the raw: {len(invalid_names)}")

## Checking for number of athlete entries with more than 1 source of data
# Count how many unique sources each athlete has
source_count = raw_data.groupby('playername')['data_source'].nunique()

# Filter athletes with data from 2 or more sources
multi_source_athletes = source_count[source_count >= 2]

# Print the result
print(f"Number of athletes that have data from multiple sources (2 or 3 systems) in the raw data: {len(multi_source_athletes)}")


### Metric Discovery and Selection
# Focusing on 'hawkins' data source for metric exploration
hawkins_data = raw_data[raw_data['data_source'] == 'hawkins']
# Count the frequency of each metric
hawkins_metrics = hawkins_data['metric'].value_counts().head(10)
# Display the result
print("Top 10 most common metrics for Hawkins data:\n", hawkins_metrics)



# Focusing on 'kinexon' data source for metric exploration
kinexon_data = raw_data[raw_data['data_source'] == 'kinexon']
# Count the frequency of each metric
kinexon_metrics = kinexon_data['metric'].value_counts().head(10)
# Display the result
print("Top 10 most common metrics for Kinexon data:\n", kinexon_metrics)


# Focusing on 'vald' data source for metric exploration
vald_data = raw_data[raw_data['data_source'] == 'vald']
# Count the frequency of each metric
vald_metrics = vald_data['metric'].value_counts().head(10)
# Display the result
print("Top 10 most common metrics for Vald data:\n", vald_metrics)


## Identifying unique metrics across all data sources
metric_list = raw_data['metric'].unique()
print("Unique metrics:")
print(metric_list)
print(f"Total number of unique metrics: {len(metric_list)}")


# Top date ranges for top metrics for each data source
# Ensure timestamp is in datetime format
raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])

# Group by data source and metric to get count and date range
summary = raw_data.groupby(['data_source', 'metric']).agg(
    record_count=('timestamp', 'count'),
    start_date=('timestamp', 'min'),
    end_date=('timestamp', 'max')
).reset_index()

# Get top 1 metric per data source by record count
top_metrics = summary.sort_values(['data_source', 'record_count'], ascending=[True, False]) \
                     .groupby('data_source').head(1)

# Remove time from dates
top_metrics['start_date'] = top_metrics['start_date'].dt.date
top_metrics['end_date'] = top_metrics['end_date'].dt.date

# Display final result
print(top_metrics[['data_source', 'metric', 'record_count', 'start_date', 'end_date']])

