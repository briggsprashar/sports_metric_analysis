#after doing the part1_preselection.py script
import pandas as pd

#load preselection dataset
cleansports = pd.read_csv('raw/preselection.csv')


### Metric Discovery and Selection
# Focusing on 'hawkins' data source for metric exploration
hawkins_data = cleansports[cleansports['data_source'] == 'hawkins']
# Count the frequency of each metric
hawkins_metrics = hawkins_data['metric'].value_counts().head(40)
# Display the result
print("Top 40 most common metrics for Hawkins data:\n", hawkins_metrics)


# Focusing on 'kinexon' data source for metric exploration
kinexon_data = cleansports[cleansports['data_source'] == 'kinexon']
# Count the frequency of each metric
kinexon_metrics = kinexon_data['metric'].value_counts().head(30)
# Display the result
print("Top 30 most common metrics for Kinexon data:\n", kinexon_metrics)


# Focusing on 'vald' data source for metric exploration
vald_data = cleansports[cleansports['data_source'] == 'vald']
# Count the frequency of each metric
vald_metrics = vald_data['metric'].value_counts().head(20)
# Display the result
print("Top 20 most common metrics for Vald data:\n", vald_metrics)



## Identifying unique metrics across all data sources
metric_list = cleansports['metric'].unique()
print(f"Total number of unique metrics: {len(metric_list)}")


# Top date ranges for top metrics for each data source
# Ensure timestamp is in datetime format
cleansports['timestamp'] = pd.to_datetime(cleansports['timestamp'])

# Group by data source and metric to get count and date range
summary = cleansports.groupby(['data_source', 'metric']).agg(
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

#shared results to team in teams group chat
