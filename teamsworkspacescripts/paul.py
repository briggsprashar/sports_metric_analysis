#CLEANING SCriPT before going to final cleaning.py

import pandas as pd
from datetime import datetime, timedelta

# Load dataset and verify columns
DATA_PATH = 'raw/fivemetrics_data.csv'
fivemetrics = pd.read_csv(DATA_PATH)
print("Columns in dataset:", fivemetrics.columns.tolist())

# Filter rows with missing or zero 'value'
problem_rows = fivemetrics[fivemetrics['value'].isna() | (fivemetrics['value'] == 0)]

# Count problematic entries per metric
problem_summary = (
    problem_rows['metric']
    .value_counts()
    .reset_index(name='null_or_zero_count')
    .rename(columns={'index': 'metric'})
)

print("Metrics with most NULL or zero values:\n", problem_summary)


# Count measurements per player per metric per team
counts = (
    fivemetrics
    .groupby(['team', 'metric', 'playername'])
    .size()
    .reset_index(name='measurement_count')
)

# Flag players with ≥5 measurements
counts['has_5_or_more'] = counts['measurement_count'] >= 5

# Aggregate per team and metric
summary = (
    counts.groupby(['team', 'metric'])
    .agg(
        total_players=('playername', 'nunique'),
        players_with_5_or_more=('has_5_or_more', 'sum')
    )
    .reset_index()
)

# Calculate percentage
summary['percentage_with_5_or_more'] = (
    summary['players_with_5_or_more'] / summary['total_players'] * 100
).round(2)

# Sort and display
summary = summary.sort_values(by='percentage_with_5_or_more', ascending=False)
print("Percentage of athletes with ≥5 measurements per team and metric:\n", summary)



#ATHLETES DID NOT GET TESTED FOR 6 MONTHS

# Convert 'timestamp' to datetime format
fivemetrics['timestamp'] = pd.to_datetime(fivemetrics['timestamp'], errors='coerce')

# Define cutoff date (6 months ago from today)
cutoff_date = datetime.today() - timedelta(days=6*30)  # approx 6 months

# Filter only valid timestamps
valid_data = fivemetrics.dropna(subset=['timestamp'])

# Step 1: Get latest test date per athlete per metric
latest_test = (
    valid_data
    .groupby(['playername', 'metric'])['timestamp']
    .max()
    .reset_index(name='last_test_date')
)

# Step 2: Flag athletes not tested in last 6 months
latest_test['tested_recently'] = latest_test['last_test_date'] >= cutoff_date

# Step 3: Filter athletes who haven't been tested recently
not_tested_recently = latest_test[~latest_test['tested_recently']]

# Step 4: Display full results
print("Athletes who haven't been tested in the last 6 months (by metric):")
print(not_tested_recently.sort_values(by='last_test_date'))

# Step 5: Display unique player names
unique_players_not_tested = not_tested_recently['playername'].drop_duplicates().sort_values().reset_index(drop=True)
print("\nUnique athletes who haven't been tested in the last 6 months:")
print(unique_players_not_tested)





# Define cutoff date: 6 months ago from today
cutoff_date = datetime.today() - timedelta(days=180)

# Identify last test date per athlete per metric
last_tests_all = (
    fivemetrics
    .groupby(['playername', 'metric'])['timestamp']
    .max()
    .reset_index(name='last_test_date')
)

# Flag athletes tested in last 6 months
last_tests_all['tested_recently'] = last_tests_all['last_test_date'] >= cutoff_date

# Filter athletes who have been tested recently
tested_recently_all = last_tests_all[last_tests_all['tested_recently']]

# Count unique athletes tested recently
unique_tested_athletes = tested_recently_all['playername'].nunique()

# Display results
print(f"\nNumber of athletes tested in the last 6 months (all metrics): {unique_tested_athletes}")
print("List of unique athletes tested in the last 6 months:")
print(tested_recently_all['playername'].drop_duplicates().sort_values().reset_index(drop=True))



###SINGLE
# Load the dataset
fivemetrics = pd.read_csv('raw/fivemetrics_data.csv')

# Define the function
def get_player_metric_sessions(data, player_name, selected_metrics):
    

    # Filter for the selected player and metrics
    filtered = data[
        (data['playername'] == player_name) &
        (data['metric'].isin(selected_metrics))
    ].dropna(subset=['timestamp'])
    
    # Pivot to get one row per session with metrics as columns
    session_df = (
        filtered
        .pivot_table(index='timestamp', columns='metric', values='value', aggfunc='first')
        .reset_index()
    )
    
    # Reorder columns: timestamp first, then selected metrics
    ordered_cols = ['timestamp'] + [metric for metric in selected_metrics if metric in session_df.columns]
    session_df = session_df[ordered_cols]
    
    return session_df

# Example usage
player_name = "PLAYER_1167"
selected_metrics = ["Rsi"]

# Get the player's Rsi sessions
player_sessions_rsi = get_player_metric_sessions(fivemetrics, player_name, selected_metrics)

# Display the result
print(f"\nTest sessions for {player_name} with metric {selected_metrics[0]}:")
print(player_sessions_rsi)




# Define the function to support multiple players
def get_player_metric_sessions(data, player_names, selected_metrics):

    # Ensure timestamp is in datetime format
    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
    
    # Filter for selected players and metrics
    filtered = data[
        (data['playername'].isin(player_names)) &
        (data['metric'].isin(selected_metrics))
    ].dropna(subset=['timestamp'])
    
    # Pivot to get one row per session with metrics as columns
    session_df = (
        filtered
        .pivot_table(index=['playername', 'timestamp'], columns='metric', values='value', aggfunc='first')
        .reset_index()
    )
    
    # Reorder columns: playername, timestamp, then selected metrics
    ordered_cols = ['playername', 'timestamp'] + [metric for metric in selected_metrics if metric in session_df.columns]
    session_df = session_df[ordered_cols]
    
    return session_df

# Example usage
player_names = ["PLAYER_1167", "PLAYER_1208", "PLAYER_892"]
selected_metrics = ["Rsi"]

# Get the players' Rsi sessions
player_sessions_rsi = get_player_metric_sessions(fivemetrics, player_names, selected_metrics)

# Display the result
print(f"\nTest sessions for players {', '.join(player_names)} with metric {selected_metrics[0]}:")
print(player_sessions_rsi)
