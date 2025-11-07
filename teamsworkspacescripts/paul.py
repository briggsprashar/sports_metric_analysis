#STARTED FROM FIVEMETRICS DATASET THAT IS LOADED FROM PART1_POSTSELECTION.PY = FIVEMETRICS_DATA.CSV
import pandas as pd
from datetime import datetime, timedelta

#THIS CODE WILL BE USED IN PART2_CLEANING.PY

# Load five metrics dataset
fivemetrics = pd.read_csv('raw/fivemetrics_data.csv')

# Display list of columns to verify loading
print("Columns in five metrics dataset:\n", fivemetrics.columns.tolist())



            ## 2.1 MISSING DATA ANALYSIS
    # 1.Identify rows with NULL or zero values in 'value' column
problem_rows = fivemetrics[fivemetrics['value'].isna() | (fivemetrics['value'] == 0)]

# Count problematic entries per metric
problem_summary = (
    problem_rows['metric']
    .value_counts()
    .reset_index(name='null_or_zero_count')
    .rename(columns={'index': 'metric'})
)
print("Metrics with most NULL or zero values:\n", problem_summary)


    # 2.For each sport/team, calculate what percentage of athletes have at least 5 measurements for your selected metrics
# Count measurements per player per metric per team
counts = (
    fivemetrics
    .groupby(['sportsteam', 'metric', 'playername'])
    .size()
    .reset_index(name='measurement_count')
)

# Flag players with ≥5 measurements
counts['has_5_or_more'] = counts['measurement_count'] >= 5

# Aggregate per team and metric
summary = (
    counts.groupby(['sportsteam', 'metric'])
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


    # 3.Identify athletes who haven't been tested in the last 6 months (for your selected metrics)
# Convert 'timestamp' to datetime format
fivemetrics['timestamp'] = pd.to_datetime(fivemetrics['timestamp'], errors='coerce')

# Define cutoff date (6 months ago from today)
cutoff_date = datetime.today() - timedelta(days=180)  # approx 6 months

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


#OPTIONAL: showing list of the unique player names who have been tested recently along with their sportsteam
# Step 5: Filter athletes who HAVE been tested recently
tested_recently = latest_test[latest_test['tested_recently']]

# Step 6: Merge with original data to get sportsteam info
player_team_info = fivemetrics[['playername', 'sportsteam']].drop_duplicates()

# Merge to get sportsteam for tested players
tested_with_team = tested_recently.merge(player_team_info, on='playername', how='left')

# Step 7: Drop duplicates to get unique player-team pairs
unique_tested_players = tested_with_team[['playername', 'sportsteam']].drop_duplicates()

# Step 8: Display results
print("Unique players tested in the last 6 months with their sportsteam:")
print(unique_tested_players.sort_values(by='playername'))








            ## 2.2 DATA TRANSFORMATION CHANLLENGES
###SINGLE METRIC
# Load the dataset
singlemetric = pd.read_csv('raw/fivemetrics_data.csv')

# Remove rows with NaN or zero values in 'value'
singlemetric = singlemetric.dropna(subset=['value'])
singlemetric = singlemetric[singlemetric['value'] >= 0].copy()

# Define the function
def get_player_metric_sessions(data, player_name, selected_metrics):
    # Ensure selected_metrics is a list
    if isinstance(selected_metrics, str):
        selected_metrics = [selected_metrics]
    
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
selected_metrics = ["Rsi"]  # Pass as a list

# Get the player's Rsi sessions
player_sessions_rsi = get_player_metric_sessions(singlemetric, player_name, selected_metrics)

# Display the result
print(f"\nTest sessions for {player_name} with metric {selected_metrics[0]}:")
print(player_sessions_rsi)



            ## 2.3 CREATE A DERIVE METRIC GROUP
    #1.Calculates the mean value for each team (using the team column)
# Load the dataset
meanteam = pd.read_csv('raw/fivemetrics_data.csv')
meanteam['value'] = pd.to_numeric(meanteam['value'], errors='coerce')
meanteam = meanteam.dropna(subset=['value'])
meanteam = meanteam[meanteam['value'] > 0].copy()

# Calculate mean value per team and metric
team_means = (
    meanteam
    .groupby(['team', 'metric'])['value']
    .mean()
    .reset_index()
    .rename(columns={'value': 'team_avg'})
)

# Display team means
print("Mean metric value per team:")
print(team_means.sort_values(by='team_avg', ascending=False))

    #2. For each athlete measurement, calculates their percent difference from their team's average
#Merge team averages into athlete data
playdiff = meanteam.merge(team_means, on=['team', 'metric'], how='left')

# Calculate percent difference from team average
playdiff['percent_diff_from_team'] = ((playdiff['value'] - playdiff['team_avg']) / playdiff['team_avg']) * 100

# Display results
print("\nPercent difference from team average for each athlete measurement:")
print(
    playdiff[
        ['playername', 'team', 'metric', 'value', 'team_avg', 'percent_diff_from_team']
    ].sort_values(by='percent_diff_from_team', ascending=False)
)

    #3.Identifies the top 5 and bottom 5 performers relative to their team mean
# Sort by percent difference
sorted_diff = playdiff.sort_values(by='percent_diff_from_team', ascending=False)

# Top 5 performers (above team average)
top_5 = sorted_diff.head(5)

# Bottom 5 performers (below team average)
bottom_5 = sorted_diff.tail(5)

# Display results
print("\nTop 5 performers relative to their team mean:")
print(top_5[['playername', 'team', 'metric', 'value', 'team_avg', 'percent_diff_from_team']])

print("\nBottom 5 performers relative to their team mean:")
print(bottom_5[['playername', 'team', 'metric', 'value', 'team_avg', 'percent_diff_from_team']])
























# Count unique teams and their frequency
team_counts = (
    cleanedsixmonth['team']
    .value_counts()
    .reset_index()
    .rename(columns={'index': 'team', 'team': 'count'})
)

# Display the result
print("\nUnique teams and their total entry counts:")
print(team_counts)



# Show unique players with more than 5 metrics and their sportsteam
# Load the CSV
cleanedsixmonth = pd.read_csv('raw/sixmonthsmetrics_data.csv')

# Count non-null metrics per row, excluding 'playername'

metric_counts = cleanedsixmonth.drop(columns=['playername', 'sportsteam']).notnull().sum(axis=1)

# Filter rows where the player has more than 5 metrics
filtered_df = cleanedsixmonth.loc[metric_counts >= 5, ['playername', 'sportsteam']]

# Drop duplicates to get unique player-team pairs
unique_players = filtered_df.drop_duplicates()

# Display the result
print("Unique players with more than 5 metrics and their sportsteam:")
print(unique_players)


