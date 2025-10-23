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

# remove limit 1000; to get full dataset
sql_toexecute = """
  select *
  from research_experiment_refactor_test
  """

response = pd.read_sql(sql_toexecute, conn)

## Downloading the data locally (optional) remove # below to enable
# Ensure 'raw' folder exists
# raw_folder = "raw"
# os.makedirs(raw_folder, exist_ok=True)

##Save result to CSV in 'raw' folder
# output_path = os.path.join(raw_folder, "query_result.csv")
# response.to_csv(output_path, index=False)
# print(f"Query result saved to: {output_path}")

# Creating subset of data for specific metrics of interest (will change once team decides on which metrics to focus on)
# viewing list of unique entries in metric column

# removing duplicate rows based even if ID number is different
response = response.drop_duplicates(subset=[col for col in response.columns if col != 'ID'])

# Standardizing responses in 'metric' column to ensure consistency (found out responses have upper/lower issues)
response['metric'] = response['metric'].str.strip().str.title()

metric_list = response['metric'].unique()
print(metric_list)

metrics_five = ['Braking Rfd(N/s)', 'Jump Height(M)', 'Rsi', 'Time To Stabilization(Ms)', 'Peak Landing Force(N)']
response_subset = response[response['metric'].isin(metrics_five)]

# Creating final dataset with selected columns
Final_Data = response_subset[['id', 'playername', 'timestamp', 'device', 'metric', 'value', 'team', 'data_source']].copy()

# saving final dataset to CSV in 'raw' folder (ensure 'raw' folder exists)
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

# Save final dataset to CSV
output_path = os.path.join(raw_folder, "final_data.csv")
Final_Data.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")
