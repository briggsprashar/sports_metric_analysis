#4 RESEARCH MONITORING FLAG SYSTEM
#4.1 Performance Monitoring Flag System (Group)
import pandas as pd

# 4.1A Metric Decline Compared to Baseline
# Load dataset
base_df = pd.read_csv('raw/fivemetrics_data.csv', parse_dates=['timestamp'])

# Filter data to last 12 months
current_date = pd.Timestamp.today()
one_year_before = current_date - pd.DateOffset(years=1)
df_2025 = base_df[(base_df['timestamp'] >= one_year_before) & (base_df['timestamp'] <= current_date)]

# Compute baseline: average of first 5 oldest records per player + metric
baseline_df = (
    df_2025
    .sort_values('timestamp')
    .groupby(['playername', 'metric'], as_index=False)
    .apply(lambda g: pd.Series({'baseline': g.head(5)['value'].mean()}), include_groups=False)
)

# Merge baseline back into dataset
df_with_baseline = df_2025.merge(baseline_df, on=['playername', 'metric'], how='left')

# Define thresholds for decline detection
thresholds = {
    'Speed_Max': 0.90,                    # <90% of baseline
    'Jump Height(M)': 0.90,               # <90% of baseline
    'Peak Velocity(M/S)': 0.95,           # <95% of baseline
    'Peak Propulsive Power(W)': 0.95,     # <95% of baseline
    'Distance_Total': 0.80                # >80% of baseline (reverse logic)
}

# Flag decline based on metric-specific rules
def flag_decline(row):
    metric = row['metric']
    baseline = row['baseline']
    value = row['value']
    if metric in ['Speed_Max', 'Jump Height(M)', 'Peak Velocity(M/S)', 'Peak Propulsive Power(W)']:
        return value < thresholds[metric] * baseline
    elif metric == 'Distance_Total':
        return value > thresholds[metric] * baseline
    return False

df_with_baseline['declined'] = df_with_baseline.apply(flag_decline, axis=1)

# Extract declined players for reporting
df_declined = df_with_baseline[df_with_baseline['declined']]
declined_report = df_declined[['playername', 'groupteam', 'metric', 'timestamp', 'value', 'baseline']]

# Save outputs
declined_report.to_csv('raw/players_below_baseline_2025.csv', index=False)
df_with_baseline.to_csv('raw/players_with_baseline_2025.csv', index=False)
print(declined_report.head())


# 4.1B Metric Below/Above Published Risk Thresholds
metric_df = pd.read_csv('raw/fivemetrics_data.csv', parse_dates=['timestamp'])
current_date = pd.Timestamp.today()
one_year_before = current_date - pd.DateOffset(years=1)
df_2025 = metric_df[(metric_df['timestamp'] >= one_year_before) & (metric_df['timestamp'] <= current_date)]

# Standard deviation threshold: mean - std
std_stats = (
    df_2025
    .groupby(['groupteam', 'metric'])
    .agg(mean=('value', 'mean'), std=('value', 'std'))
    .reset_index()
)
std_stats['std_threshold'] = std_stats['mean'] - std_stats['std']

# Percentile threshold: 10th percentile
percentile_stats = (
    df_2025
    .groupby(['groupteam', 'metric'])['value']
    .quantile(0.10)
    .reset_index()
    .rename(columns={'value': 'percentile_threshold'})
)

# Merge thresholds into dataset
df_thresh = df_2025.merge(std_stats[['groupteam', 'metric', 'std_threshold']], on=['groupteam', 'metric'], how='left')
df_thresh = df_thresh.merge(percentile_stats, on=['groupteam', 'metric'], how='left')

# Flag risk status
df_thresh['risk_std'] = df_thresh['value'] < df_thresh['std_threshold']
df_thresh['risk_percentile'] = df_thresh['value'] < df_thresh['percentile_threshold']

# Extract risky rows
risky_rows = df_thresh[(df_thresh['risk_std']) | (df_thresh['risk_percentile'])]
risky_rows.to_csv('raw/risky_players_2025.csv', index=False)
print(risky_rows[['playername', 'groupteam', 'metric', 'value', 'std_threshold', 'percentile_threshold', 'risk_std', 'risk_percentile']].head())


# 4.1C Athlete Not Tested in >30 Days
thirty_df = pd.read_csv('raw/fivemetrics_data.csv', parse_dates=['timestamp'])
current_date = pd.Timestamp.today()

# Find last test date per athlete
last_test = (
    thirty_df.groupby('playername', as_index=False)['timestamp']
      .max()
      .rename(columns={'timestamp': 'last_test_date'})
)

# Calculate days since last test
last_test['days_since_test'] = (current_date - last_test['last_test_date']).dt.days
last_test['overdue_test'] = last_test['days_since_test'] > 30

# Merge flag back into dataset if needed
df_with_test_flag = thirty_df.merge(last_test[['playername', 'last_test_date', 'days_since_test', 'overdue_test']],
                                    on='playername', how='left')

# Extract overdue athletes
overdue_report = last_test[last_test['overdue_test']]
overdue_report.to_csv('raw/athletes_overdue_testing.csv', index=False)
print(overdue_report.head())


# 4.1D Deviation from Team Normal
deviation_df = pd.read_csv('raw/fivemetrics_data.csv', parse_dates=['timestamp'])
current_date = pd.Timestamp.today()
one_year_before = current_date - pd.DateOffset(years=1)
deviate_2025 = deviation_df[(deviation_df['timestamp'] >= one_year_before) & (deviation_df['timestamp'] <= current_date)]

# Team-level stats (mean, std)
team_stats = (
    deviate_2025
    .groupby(['groupteam', 'metric'], as_index=False)
    .agg(team_mean=('value', 'mean'), team_std=('value', 'std'))
)

# Player-level stats (mean)
player_stats = (
    deviate_2025
    .groupby(['playername', 'metric'], as_index=False)
    .agg(player_mean=('value', 'mean'))
)

# Merge stats into dataset
df_deviate = (
    deviate_2025
    .merge(team_stats, on=['groupteam', 'metric'], how='left')
    .merge(player_stats, on=['playername', 'metric'], how='left')
)

# Z-score relative to team mean
df_deviate['z_score_team'] = (df_deviate['value'] - df_deviate['team_mean']) / df_deviate['team_std']
df_deviate['significant_deviation_team'] = df_deviate['z_score_team'].abs() > 2

# Thresholds relative to player mean
thresholds = {
    'Speed_Max': 0.90,
    'Jump Height(M)': 0.90,
    'Peak Velocity(M/S)': 0.95,
    'Peak Propulsive Power(W)': 0.95,
    'Distance_Total': 0.80
}

# Evaluate decline vs player mean
def evaluate_player_mean(row):
    metric = row['metric']
    player_mean = row['player_mean']
    value = row['value']
    if metric in thresholds:
        threshold = thresholds[metric]
        ratio = value / player_mean if player_mean else None
        if ratio is None:
            return None
        if ratio < threshold:
            return f"Declined (<{int(threshold*100)}%)"
        else:
            return "Acceptable"
    return None

df_deviate['declined_vs_player_mean'] = df_deviate.apply(evaluate_player_mean, axis=1)

# Flag athletes with either team deviation or player mean decline
flagged_athletes = df_deviate[
    df_deviate['significant_deviation_team'] | (df_deviate['declined_vs_player_mean'].str.contains("Declined", na=False))
]

# Save flagged athletes and full dataset
flagged_athletes.to_csv('output/csv/part4.3_flagged_athletes.csv', index=False)
df_deviate.to_csv('raw/part4_flagged_all_players.csv', index=False)

# Quick check
print(df_deviate[['playername', 'groupteam', 'metric', 'value',
                  'team_mean', 'team_std', 'z_score_team',
                  'significant_deviation_team',
                  'player_mean', 'declined_vs_player_mean']].head())
