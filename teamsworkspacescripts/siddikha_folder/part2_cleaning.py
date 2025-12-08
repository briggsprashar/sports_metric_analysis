import pandas as pd
import os
from datetime import datetime, timedelta

####### PART 1: PRE SELECTION AND DATA MANAGEMENT OF RAW DATASET ##########
#Selecting relevant columns for analysis
raw_data = pd.read_csv('raw\query_result.csv')
relevantcolumn = raw_data[['id', 'playername', 'timestamp', 'device', 'metric', 'value', 'team', 'data_source']].copy()

#Adding new column 'groupteam' based on 'team' column to categorize into broader sports categories
def groupteam_from_team(team):
    for sport in ['Football', 'Basketball']:
        if sport in team:
            return f"Women's {sport}" if "Women" in team else f"Men's {sport}" if "Men" in team else sport
    return "OTHERS"

relevantcolumn['groupteam'] = relevantcolumn['team'].apply(groupteam_from_team)

print(relevantcolumn['groupteam'].value_counts())


#adding new column sportsteam based on 'team' column to simplify team names to just sport names
def groupteam_from_team(team):
    for sport in ['Football', 'Basketball']:
        if sport in team:
            return sport
    return "OTHERS"

relevantcolumn['sportsteam'] = relevantcolumn['team'].apply(groupteam_from_team)

print(relevantcolumn['sportsteam'].value_counts())


#removing entries with 'OTHERS' in 'sportsteam' column to focus on main sports
cleansports = relevantcolumn[relevantcolumn['sportsteam'] != 'OTHERS']
print(cleansports['groupteam'].value_counts())
print(cleansports['sportsteam'].value_counts())


### QUESTIONs and ANSWER ON PART 2 CLEANING

        ## 2.1 MISSING DATA ANALYSIS
# 1. Identify rows with NULL or zero values in 'value' column
problem_rows = cleansports[cleansports['value'].isna() | (cleansports['value'] == 0)]

# Count problematic entries per metric
problem_summary = (
    problem_rows['metric']
    .value_counts()
    .reset_index(name='null_or_zero_count')
    .rename(columns={'index': 'metric'})
)
print("Metrics with most NULL or zero values:\n", problem_summary)

# Display total number of rows in the dataset
print("Total number of rows in dataset:", len(problem_rows))


    # 2.For each sport/team, calculate what percentage of athletes have at least 5 measurements for your selected metrics
# Count measurements per player per metric per team

#removing rows with NaN or zero values in 'value' for accurate counts
rawmetrics = cleansports[(cleansports['value'].notna()) & (cleansports['value'] != 0)]

counts = (
    rawmetrics
    .groupby(['groupteam', 'metric', 'playername'])
    .size()
    .reset_index(name='measurement_count')
)

# Flag players with ≥5 measurements
counts['has_5_or_more'] = counts['measurement_count'] >= 5

# Aggregate per team and metric
summary = (
    counts.groupby(['groupteam', 'metric'])
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
# Step 1: Convert 'timestamp' to datetime format
rawmetrics['timestamp'] = pd.to_datetime(rawmetrics['timestamp'], errors='coerce')
rawmetrics = rawmetrics.dropna(subset=['timestamp'])

# Step 2: Define cutoff date (6 months ago from today)
cutoff_date = datetime.today() - timedelta(days=180)

# Step 3: Filter rows with valid timestamps older than cutoff
older_than_cutoff = rawmetrics[rawmetrics['timestamp'] < cutoff_date]

# Step 4: Get player-sportsteam pairs from those older rows
player_team_pairs = older_than_cutoff[['playername', 'groupteam']].dropna(subset=['playername'])

# Step 5: Drop duplicates to get unique player-sportsteam pairs
unique_players_not_tested_recently = player_team_pairs.drop_duplicates().sort_values(by='playername')

# Step 6: Display results
print("Players with tests older than 6 months (with groupteam):")
print(unique_players_not_tested_recently)

print("\nTotal rows before uniqueness:", len(player_team_pairs))
print("Number of unique players not tested in the last 6 months:", unique_players_not_tested_recently['playername'].nunique())


#OPTIONAL: showing list of the unique player names who have been tested recently along with their sportsteam
# Step 1: Filter rows with valid timestamps older than cutoff
greater_than_cutoff = rawmetrics[rawmetrics['timestamp'] > cutoff_date]

# Step 2: Get player-groupteam pairs from those older rows
player_team_pairs = greater_than_cutoff[['playername', 'groupteam']].dropna(subset=['playername'])

# Step 3: Drop duplicates to get unique player-groupteam pairs
unique_players_tested_recently = player_team_pairs.drop_duplicates().sort_values(by='playername')

# Step 4: Display results
print("Players with tested within 6 months (with groupteam):")
print(unique_players_tested_recently)

print("\nTotal rows before uniqueness:", len(player_team_pairs))
print("Number of unique players not tested in the last 6 months:", unique_players_tested_recently['playername'].nunique())



######## CREATING FINAL DATASET WITH METRICS OF INTEREST ##########
clean_data = rawmetrics.drop_duplicates(subset=[col for col in rawmetrics.columns if col != 'id'])

# Define metrics of interest
metrics_six = ['Speed_Max', 'Jump Height(M)', 'Mrsi', 'Peak Velocity(M/S)', 'Peak Propulsive Power(W)', 'Distance_Total']

# Filter rows where 'metric' column matches one of the selected metrics
response_subset = clean_data[clean_data['metric'].isin(metrics_six)]

# Create a new DataFrame with only the relevant columns
# Adjust this list based on which columns you want to keep
columns_to_keep = ['id', 'playername', 'timestamp', 'device', 'metric', 'value', 'team', 'sportsteam', 'groupteam']  # example column names
sixmetrics_data = response_subset[columns_to_keep]

# Ensure 'raw' folder exists
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

# Save final dataset to CSV
output_path = os.path.join(raw_folder, "sixmetrics_data.csv")
sixmetrics_data.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")




            ## 2.2 DATA TRANSFORMATION CHANLLENGES
###SINGLE METRIC
# Load the dataset
singlemetric = pd.read_csv('raw/sixmetrics_data.csv')

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
selected_metrics = ["Mrsi"]  # Pass as a list

# Get the player's Mrsi sessions
player_sessions_mrsi = get_player_metric_sessions(singlemetric, player_name, selected_metrics)

# Display the result
print(f"\nTest sessions for {player_name} with metric {selected_metrics[0]}:")
print(player_sessions_mrsi)




            ## 2.3 CREATE A DERIVE METRIC GROUP
    #1.Calculates the mean value for each team (using the team column)
# Load the dataset
meanteam = pd.read_csv('raw/sixmetrics_data.csv')
meanteam['value'] = pd.to_numeric(meanteam['value'], errors='coerce')
meanteam = meanteam.dropna(subset=['value'])
meanteam = meanteam[meanteam['value'] > 0].copy()

# Calculate mean value per team and metric
team_means = (
    meanteam
    .groupby(['groupteam', 'metric'])['value']
    .mean()
    .reset_index()
    .rename(columns={'value': 'team_avg'})
)

# Display team means
print("Mean metric value per group teams:")
print(team_means.sort_values(by='team_avg', ascending=False))

    #2. For each athlete measurement, calculates their percent difference from their team's average
#Merge team averages into athlete data
playdiff = meanteam.merge(team_means, on=['groupteam', 'metric'], how='left')

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
print(top_5[['playername', 'groupteam', 'metric', 'value', 'team_avg', 'percent_diff_from_team']])

print("\nBottom 5 performers relative to their team mean:")
print(bottom_5[['playername', 'groupteam', 'metric', 'value', 'team_avg', 'percent_diff_from_team']])

    #4.Optional: Create z-scores or percentile rankings
# --- Add-on: Calculate Z-scores for each athlete's metric value ---

# Step 1: Calculate team-level mean and standard deviation
team_stats = (
    meanteam
    .groupby(['groupteam', 'metric'])['value']
    .agg(team_avg='mean', team_std='std')
    .reset_index()
)

# Step 2: Merge stats into athlete data
playstats = meanteam.merge(team_stats, on=['groupteam', 'metric'], how='left')

# Step 3: Calculate Z-score: (value - mean) / std
playstats['Zscore'] = (playstats['value'] - playstats['team_avg']) / playstats['team_std']

# Step 4: Display or export Z-score results
print("\nZ-scores for each athlete's metric value:")
print(playstats[['playername', 'groupteam', 'metric', 'value', 'team_avg', 'team_std', 'Zscore']].sort_values(by='Zscore', ascending=False))

# Optional: save to CSV
# playstats.to_csv('athlete_zscores.csv', index=False)



