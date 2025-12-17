import pandas as pd
import os
from datetime import datetime, timedelta

# Load raw dataset
raw_data = pd.read_csv('raw/raw.csv', dtype=str)

# Value Cleaning
# Convert 'value' column to numeric
raw_data['value'] = pd.to_numeric(raw_data['value'], errors='coerce')

# Replace extreme outliers (<1% of metric mean) with NaN,
# then apply linear interpolation and backfill/forward fill
raw_data['value'] = (
    raw_data.groupby('metric')['value']
        .transform(lambda s: s.mask(s < s.mean() * 0.01)
                              .interpolate(method='linear')
                              .bfill()
                              .ffill())
)

# Team Name Cleaning
def clean_team_name(name):
    if pd.isna(name):
        return name
    return name.strip().lower().title()

# Standardize team names
raw_data['team'] = raw_data['team'].apply(clean_team_name)

###### PART 1: PRE-SELECTION AND DATA MANAGEMENT ##########

# Select relevant columns for analysis
relevantcolumn = raw_data[['id', 'playername', 'timestamp', 'device', 'metric', 'value', 'team', 'data_source']].copy()

# Categorize teams into broader sport categories with gender-specific labels
def groupteam_from_team(team):
    for sport in [
        "Football", "Basketball", "Baseball", "Softball", "Soccer",
        "Lacrosse", "Cross Country", "Track", "Swimming And Diving",
        "Tennis", "Volleyball"
    ]:
        if sport in team:
            return f"Women's {sport}" if "Women" in team else f"Men's {sport}" if "Men" in team else sport
    return "OTHERS"

relevantcolumn['groupteam'] = relevantcolumn['team'].apply(groupteam_from_team)
print(relevantcolumn['groupteam'].value_counts())

# Simplify team names to sport-only labels
def groupteam_from_team(team):
    for sport in [
        "Football", "Basketball", "Baseball", "Softball", "Soccer",
        "Lacrosse", "Cross Country", "Track", "Swimming And Diving",
        "Tennis", "Volleyball"
    ]:
        if sport in team:
            return sport
    return "OTHERS"

relevantcolumn['sportsteam'] = relevantcolumn['team'].apply(groupteam_from_team)
print(relevantcolumn['sportsteam'].value_counts())

# Filter dataset to exclude 'OTHERS' teams
print(">> PRE-SELECTION AND DATA MANAGEMENT: <<\n")
cleansports = relevantcolumn[relevantcolumn['sportsteam'] != 'OTHERS']
print(cleansports['groupteam'].value_counts())
print(cleansports['sportsteam'].value_counts())

# Save cleaned dataset
cleansports.to_csv('raw/cleansports.csv', index=False)

### PART 2: CLEANING QUESTIONS AND ANALYSIS ###

# Missing Data Analysis
# Identify rows with NULL or zero values in 'value'
problem_rows = cleansports[cleansports['value'].isna() | (cleansports['value'] == 0)]

# Count problematic entries per metric
problem_summary = (
    problem_rows['metric']
    .value_counts()
    .reset_index(name='null_or_zero_count')
    .rename(columns={'index': 'metric'})
)
print("Metrics with most NULL or zero values:\n", problem_summary)
print("Total number of rows in dataset:", len(problem_rows))

# Measurement Coverage
# Count measurements per player per metric per team (excluding NaN/zero values)
rawmetrics = cleansports[(cleansports['value'].notna()) & (cleansports['value'] != 0)]

counts = (
    rawmetrics
    .groupby(['groupteam', 'metric', 'playername'])
    .size()
    .reset_index(name='measurement_count')
)


# Percent of Team (groupteam) of players with ≥5 measurements (metrics)
# Flag players with ≥5 measurements
counts['has_5_or_more'] = counts['measurement_count'] >= 5

# Total players per team (unique player count)
total_players_per_team = (
    counts.groupby('groupteam')['playername']
    .nunique()
    .reset_index(name='total_players')
)

# Players with ≥5 measurements per team
players_with_5_or_more_per_team = (
    counts[counts['has_5_or_more']]
    .groupby('groupteam')['playername']
    .nunique()
    .reset_index(name='players_with_5_or_more')
)

# Merge totals and ≥5 counts
summary = total_players_per_team.merge(players_with_5_or_more_per_team, on='groupteam', how='left')
summary['players_with_5_or_more'] = summary['players_with_5_or_more'].fillna(0)

# Calculate percentage
summary['percentage_with_5_or_more'] = (
    summary['players_with_5_or_more'] / summary['total_players'] * 100
).round(2)

# Sort and display
summary = summary.sort_values(by='percentage_with_5_or_more', ascending=False)
print("Percentage of athletes with ≥5 measurements per team:\n", summary)



# Athlete Testing Recency
# Convert 'timestamp' to datetime
rawmetrics['timestamp'] = pd.to_datetime(rawmetrics['timestamp'], errors='coerce')
rawmetrics = rawmetrics.dropna(subset=['timestamp'])

# Define cutoff date (6 months ago)
cutoff_date = datetime.today() - timedelta(days=180)

# Identify athletes not tested in last 6 months
older_than_cutoff = rawmetrics[rawmetrics['timestamp'] < cutoff_date]
player_team_pairs = older_than_cutoff[['playername', 'groupteam', 'device']].dropna(subset=['playername'])
unique_players_not_tested_recently = player_team_pairs.drop_duplicates().sort_values(by='playername')

print("Players with tests older than 6 months (with groupteam):")
print(unique_players_not_tested_recently)
print("\nTotal rows before uniqueness:", len(player_team_pairs))
print("Number of unique players not tested in the last 6 months:", unique_players_not_tested_recently['playername'].nunique())
unique_players_not_tested_recently.to_csv('raw/players_not_tested_recently.csv', index=False)

# OPTIONAL: Identify athletes tested within last 6 months
greater_than_cutoff = rawmetrics[rawmetrics['timestamp'] > cutoff_date]
player_team_pairs = greater_than_cutoff[['playername', 'groupteam']].dropna(subset=['playername'])
unique_players_tested_recently = player_team_pairs.drop_duplicates().sort_values(by='playername')

print("Players tested within 6 months (with groupteam):")
print(unique_players_tested_recently)
print("\nTotal rows before uniqueness:", len(player_team_pairs))
print("Number of unique players tested in the last 6 months:", unique_players_tested_recently['playername'].nunique())

######## FINAL DATASET CREATION ##########
# Remove duplicates (excluding 'id') for clean dataset
raw_data = rawmetrics.drop_duplicates(subset=[col for col in rawmetrics.columns if col != 'id'])

# Define metrics of interest
metrics_five = ['Speed_Max', 'Jump Height(M)', 'Peak Velocity(M/S)', 'Peak Propulsive Power(W)', 'Distance_Total']

# Filter dataset to include only selected metrics
response_subset = raw_data[raw_data['metric'].isin(metrics_five)]

# Create a new DataFrame with only the relevant columns
# Adjust this list based on which columns you want to keep
columns_to_keep = ['id', 'playername', 'timestamp', 'device', 'metric', 'value', 'groupteam']
fivemetrics_data = response_subset[columns_to_keep]

# Convert 'value' column to numeric type
fivemetrics_data['value'] = pd.to_numeric(fivemetrics_data['value'], errors='coerce')

# Ensure 'raw' folder exists
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

# Save final dataset to CSV
output_path = os.path.join(raw_folder, "fivemetrics_allsports.csv")
fivemetrics_data.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")


## 2.2 DATA TRANSFORMATION CHALLENGES
### Single Metric Wide Data Function
print(">> DATA TRANSFORMATION CHALLENGES: <<\n")
# Load dataset and pivot to wide format
widedf = pd.read_csv('raw/fivemetrics_allsports.csv', dtype=str)

# Convert timestamp column to datetime
widedf['timestamp'] = pd.to_datetime(widedf['timestamp'], errors='coerce')

# Drop rows with invalid timestamps or missing values
widedf = widedf.dropna(subset=['timestamp', 'value'])

# Pivot to wide format: metrics become columns
pivot_wide = (
    widedf.pivot_table(
        index=['playername', 'groupteam', 'device', 'timestamp'],
        columns='metric',
        values='value',
        aggfunc='last'
    )
    .reset_index()
)

# Function to extract sessions for a given player and selected metrics
def get_player_metric_sessions_wide(data, player_name, selected_column):
    filtered = data[data['playername'] == player_name].copy()
    chosen_cols = ['timestamp', 'groupteam'] + [c for c in selected_column if c in filtered.columns]
    session_df = filtered[chosen_cols].dropna(subset=selected_column, how='all')
    return session_df

# Example usage
player_name = "PLAYER_995" # Replace with other playersname as needed
selected_column = ["Speed_Max"]   # Replace with other metrics as needed
player_sessions = get_player_metric_sessions_wide(pivot_wide, player_name, selected_column)

print(f"\nTest sessions for {player_name} with metrics {selected_column}:")
print(player_sessions)


## 2.3 CREATE DERIVED METRIC GROUP
print(">> CREATE DERIVED METRIC GROUP: <<\n")
# 2.3.1 Calculate mean value per team and metric
meanteam = pd.read_csv('raw/fivemetrics_allsports.csv', dtype=str)
meanteam['value'] = pd.to_numeric(meanteam['value'], errors='coerce')
meanteam = meanteam.dropna(subset=['value'])
meanteam = meanteam[meanteam['value'] > 0].copy()

team_means = (
    meanteam
    .groupby(['groupteam', 'metric'])['value']
    .mean()
    .reset_index()
    .rename(columns={'value': 'team_avg'})
)

print("Mean metric value per group teams:")
print(team_means.sort_values(by=['groupteam', 'metric'], ascending=False))

# 2.3.2 Calculate percent difference from team average for each athlete measurement
playdiff = meanteam.merge(team_means, on=['groupteam', 'metric'], how='left')
playdiff['percent_diff_from_team'] = ((playdiff['value'] - playdiff['team_avg']) / playdiff['team_avg']) * 100

print("\nPercent difference from team average for each athlete measurement:")
print(
    playdiff[['playername', 'groupteam', 'metric', 'value', 'team_avg', 'percent_diff_from_team']]
    .sort_values(by='percent_diff_from_team', ascending=False)
)

# 2.3.3 Identify top 5 and bottom 5 performers relative to team mean
sorted_diff = playdiff.sort_values(by='percent_diff_from_team', ascending=False)
top_5 = sorted_diff.head(5)
bottom_5 = sorted_diff.tail(5)

print("\nTop 5 performers relative to their team mean:")
print(top_5[['playername', 'groupteam', 'metric', 'value', 'team_avg', 'percent_diff_from_team']])

print("\nBottom 5 performers relative to their team mean:")
print(bottom_5[['playername', 'groupteam', 'metric', 'value', 'team_avg', 'percent_diff_from_team']])

# 2.3.4 Optional: Calculate Z-scores for athlete metrics
team_stats = (
    meanteam
    .groupby(['groupteam', 'metric'])['value']
    .agg(team_avg='mean', team_std='std')
    .reset_index()
)

playstats = meanteam.merge(team_stats, on=['groupteam', 'metric'], how='left')
playstats['Zscore'] = (playstats['value'] - playstats['team_avg']) / playstats['team_std']

print("\nZ-scores for each athlete's metric value:")
print(playstats[['playername', 'groupteam', 'metric', 'value', 'team_avg', 'team_std', 'Zscore']].sort_values(by='Zscore', ascending=False))

# Save Z-score results to CSV
playstats.to_csv('raw/athlete_zscores.csv', index=False)
