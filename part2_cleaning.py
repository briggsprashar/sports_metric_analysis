#import necessary libraries
import pandas as pd

# Load five metrics dataset
fivemetrics = pd.read_csv('raw/fivemetrics_data.csv')

# Display list of columns to verify loading
print("Columns in five metrics dataset:\n", fivemetrics.columns.tolist())


## Identifying metrics with most NULL or zero values
# Step 1: Filter rows with NULL or zero values in 'value'
problem_rows = fivemetrics[fivemetrics['value'].isna() | (fivemetrics['value'] == 0)]

# Step 2: Count how many problematic rows exist per metric
problem_summary = (
    problem_rows.groupby('metric')                          # grouping by 'metric'
    .size()                                                 # counting occurrences
    .reset_index(name='null_or_zero_count')                 # resetting index and naming the count column
    .sort_values(by='null_or_zero_count', ascending=False)  # sorting by count in descending order
)

# Step 3: Display results
print("Metrics with the most NULL or zero values:\n", problem_summary)


## Rate of athletese with more than 5 types of metrics per sport/team
# Step 1: Count measurements per player per metric per team
counts = (
    fivemetrics
    .groupby(['team', 'metric', 'playername'])
    .size()
    .reset_index(name='measurement_count')
)

# Step 2: Flag players with at least 5 measurements
counts['has_5_or_more'] = counts['measurement_count'] >= 5

# Step 3: Calculate total players and qualifying players per team and metric
summary = (
    counts.groupby(['team', 'metric'])
    .agg(
        total_players=('playername', 'nunique'),
        players_with_5_or_more=('has_5_or_more', 'sum')
    )
    .reset_index()
)

# Step 4: Compute percentage
summary['percentage_with_5_or_more'] = (
    summary['players_with_5_or_more'] / summary['total_players'] * 100
).round(2)

# Step 5: Sort by percentage descending
summary = summary.sort_values(by='percentage_with_5_or_more', ascending=False)

# Step 6: Display results
print("Percentage of athletes with ≥5 measurements per team and metric:")
print(summary)
