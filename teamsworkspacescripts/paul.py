#STARTED FROM FIVEMETRICS DATASET THAT IS LOADED FROM PART1_POSTSELECTION.PY = FIVEMETRICS_DATA.CSV
import pandas as pd
from datetime import datetime, timedelta

    #THIS CODE WILL BE USED IN PART2_CLEANING.PY
# Load five metrics dataset
fivemetrics = pd.read_csv('raw/fivemetrics_data.csv')
# Display list of columns to verify loading
print("Columns in five metrics dataset:\n", fivemetrics.columns.tolist())


        ## 2.1 MISSING DATA ANALYSIS
# 1. Identify rows with NULL or zero values in 'value' column
problem_rows = fivemetrics[fivemetrics['value'].isna() | (fivemetrics['value'] == 0)]

# Count problematic entries per metric
problem_summary = (
    problem_rows['metric']
    .value_counts()
    .reset_index(name='null_or_zero_count')
    .rename(columns={'index': 'metric'})
)
print("Metrics with most NULL or zero values:\n", problem_summary)

# Display total number of rows in the dataset
print("Total number of rows in dataset:", len(fivemetrics))


    # 2.For each sport/team, calculate what percentage of athletes have at least 5 measurements for your selected metrics
# Count measurements per player per metric per team
#removing rows with NaN or zero values in 'value' for accurate counts
fivemetrics = fivemetrics.dropna(subset=['value'])

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
# Step 1: Convert 'timestamp' to datetime format
fivemetrics['timestamp'] = pd.to_datetime(fivemetrics['timestamp'], errors='coerce')

# Step 2: Define cutoff date (6 months ago from today)
cutoff_date = datetime.today() - timedelta(days=180)

# Step 3: Filter rows with valid timestamps older than cutoff
older_than_cutoff = fivemetrics[fivemetrics['timestamp'] < cutoff_date]

# Step 4: Get player-sportsteam pairs from those older rows
player_team_pairs = older_than_cutoff[['playername', 'sportsteam']].dropna(subset=['playername'])

# Step 5: Drop duplicates to get unique player-sportsteam pairs
unique_players_not_tested_recently = player_team_pairs.drop_duplicates().sort_values(by='playername')

# Step 6: Display results
print("Players with tests older than 6 months (with sportsteam):")
print(unique_players_not_tested_recently)

print("\nTotal rows before uniqueness:", len(player_team_pairs))
print("Number of unique players not tested in the last 6 months:", unique_players_not_tested_recently['playername'].nunique())



#OPTIONAL: showing list of the unique player names who have been tested recently along with their sportsteam
# Step 1: Filter rows with valid timestamps older than cutoff
older_than_cutoff = fivemetrics[fivemetrics['timestamp'] > cutoff_date]

# Step 2: Get player-sportsteam pairs from those older rows
player_team_pairs = older_than_cutoff[['playername', 'sportsteam']].dropna(subset=['playername'])

# Step 5: Drop duplicates to get unique player-sportsteam pairs
unique_players_not_tested_recently = player_team_pairs.drop_duplicates().sort_values(by='playername')

# Step 6: Display results
print("Players with tests older than 6 months (with sportsteam):")
print(unique_players_not_tested_recently)

print("\nTotal rows before uniqueness:", len(player_team_pairs))
print("Number of unique players not tested in the last 6 months:", unique_players_not_tested_recently['playername'].nunique())






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





        ## 3. LONGITUDINAL ANALYSIS AND VISUALIZATION
    #3.1 Individual Athlete Timeline (Pair Work)
#3.1A  Individual Athlete Timeline (Pair Work) (in part3_viz_individual.ipynb)
import pandas as pd
import matplotlib.pyplot as plt

#REMINDER FIVEMETRICS IS NOT TOTALLY CLEANED YET SO MAY HAVE TO HANDLE NA/0 VALUES
# Clean the dataset by removing rows with NaN or zero values in 'value'
# df = df[df['value'].notna() & (df['value'] != 0)]

# Load the dataset 
df = pd.read_csv('raw/fivemetrics_data.csv')

# Filter for player_1022
player_df = df[df['playername'] == 'PLAYER_1022'].copy()

# Convert timestamp to datetime
player_df['timestamp'] = pd.to_datetime(player_df['timestamp'], errors='coerce')
player_df = player_df.dropna(subset=['timestamp'])

# Filter for last 12 months
cutoff_date = player_df['timestamp'].max() - pd.DateOffset(months=12)
player_df = player_df[player_df['timestamp'] >= cutoff_date]

# Get sportsteam label (assumes consistent team for this player)
sportsteam = player_df['sportsteam'].dropna().unique()
team_label = sportsteam[0] if len(sportsteam) > 0 else "Unknown Team"

# Get unique metrics
metrics = player_df['metric'].unique()

# Plot each metric separately
for metric in metrics:
    metric_df = player_df[player_df['metric'] == metric]
    plt.figure(figsize=(10, 4))
    plt.plot(metric_df['timestamp'], metric_df['value'], marker='o')
    plt.title(f"{metric} over time for PLAYER_1022 ({team_label})")
    plt.xlabel("timestamp")
    plt.ylabel("value")
    plt.grid(True)
    plt.tight_layout()
    plt.show()



#3.1B Identify their best and worst performance dates
# Load and clean the dataset
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp', 'value'])

# Group by metric to find best and worst performance dates
best_dates = (
    player_df.loc[player_df.groupby('metric')['value'].idxmax()]
    [['metric', 'value', 'timestamp']]
    .rename(columns={'value': 'best_value', 'timestamp': 'best_date'})
)

worst_dates = (
    player_df.loc[player_df.groupby('metric')['value'].idxmin()]
    [['metric', 'value', 'timestamp']]
    .rename(columns={'value': 'worst_value', 'timestamp': 'worst_date'})
)

# Merge best and worst into one summary
performance_summary = pd.merge(best_dates, worst_dates, on='metric')

# Display results
print(f"Best and worst performance dates for {player_df['playername'].iloc[0]}:")
print(performance_summary.sort_values(by='metric'))


#  OPTIONAL SHOWS TOP 5 and TOP 5 WORST PERFORMANCES ACROSS ALL METRICS
# Load and clean the dataset
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp', 'value'])

# Get top 5 and bottom 5 performance dates per metric
top_dates = (
    player_df
    .sort_values(by='value', ascending=False)
    .groupby('metric')
    .head(5)
    [['metric', 'timestamp', 'value']]
    .assign(performance='top')
)

bottom_dates = (
    player_df
    .sort_values(by='value', ascending=True)
    .groupby('metric')
    .head(5)
    [['metric', 'timestamp', 'value']]
    .assign(performance='bottom')
)

# Combine and display
performance_dates = pd.concat([top_dates, bottom_dates]).sort_values(by=['metric', 'performance', 'timestamp'])
print(f"Top and bottom 5 performance dates for for {player_df['playername'].iloc[0]}:")
print(performance_dates)



#3.1C Calculate if they show improvement or decline trends over the last 12 months for each metric
from scipy.stats import linregress

trend_results = []

for metric in metrics:
    metric_df = player_df[player_df['metric'] == metric].copy()
    
    # Skip if not enough data
    if len(metric_df) < 2:
        continue

    # Convert timestamp to ordinal for regression
    x = metric_df['timestamp'].map(pd.Timestamp.toordinal).values
    y = metric_df['value'].values

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    # Determine trend
    if slope > 0.01:
        trend = 'improvement'
    elif slope < -0.01:
        trend = 'decline'
    else:
        trend = 'stable'

    trend_results.append({
        'metric': metric,
        'slope': round(slope, 4),
        'r_squared': round(r_value**2, 4),
        'trend': trend
    })

# Display trend summary
trend_df = pd.DataFrame(trend_results)
print(f"\nPerformance trend for {player_df['playername'].iloc[0]} (last 12 months):")
print(trend_df.sort_values(by='metric'))



    #3.2 Individual Athlete Timeline (Pair Work) this will be in part3_viz_comparison.ipynb
#3.2A Create box plots or violin plots comparing your selected metric(s) between teams
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load and clean the dataset
df = pd.read_csv('raw/fivemetrics_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['value', 'sportsteam', 'metric'])

# Get all unique metrics
all_metrics = df['metric'].unique()

# Plot each metric separately
for metric in all_metrics:
    metric_df = df[df['metric'] == metric]

    # Box Plot
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='sportsteam', y='value', data=metric_df)
    plt.title(f"Box Plot of {metric} by Team")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Violin Plot
    plt.figure(figsize=(12, 6))
    sns.violinplot(x='sportsteam', y='value', data=metric_df, inner='quartile')
    plt.title(f"Violin Plot of {metric} by Team")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


#3.2B Calculate statistical significance (t-test or ANOVA as appropriate)
import pandas as pd
from scipy.stats import f_oneway

# Load and clean the dataset
df = pd.read_csv('raw/fivemetrics_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['value', 'sportsteam', 'metric'])

# Prepare results
anova_results = []

# Loop through each metric
for metric in df['metric'].unique():
    metric_df = df[df['metric'] == metric]
    teams = metric_df['sportsteam'].unique()

    # Collect values per team
    team_values = [metric_df[metric_df['sportsteam'] == team]['value'].values for team in teams]

    # Skip if any team has fewer than 2 values
    if any(len(vals) < 2 for vals in team_values):
        continue

    # Perform ANOVA
    stat, p = f_oneway(*team_values)

    anova_results.append({
        'metric': metric,
        'F_statistic': round(stat, 4),
        'p_value': round(p, 4),
        'significant': p < 0.05
    })

# Display results
anova_df = pd.DataFrame(anova_results)
print("ANOVA results comparing sportsteams for each metric:")
print(anova_df.sort_values(by='metric'))


#3.2C  Create a visualization showing testing frequency by team over time
import pandas as pd
import matplotlib.pyplot as plt

# Load and clean the dataset
df = pd.read_csv('raw/fivemetrics_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp', 'sportsteam'])

# Create a 'month' column
df['month'] = df['timestamp'].dt.to_period('M').dt.to_timestamp()

# Group by team and month to count tests
test_counts = df.groupby(['sportsteam', 'month']).size().reset_index(name='test_count')

# Pivot for plotting
pivot_df = test_counts.pivot(index='month', columns='sportsteam', values='test_count').fillna(0)

# Plot
plt.figure(figsize=(14, 6))
pivot_df.plot(marker='o')
plt.title("Testing Frequency by Team Over Time")
plt.xlabel("Month")
plt.ylabel("Number of Tests")
plt.grid(True)
plt.legend(title='Team', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()


    #3.3C  Dashboard Metric (Full Group)
#3.3A Total number of tests per month (all systems combined)
import pandas as pd
import matplotlib.pyplot as plt

# Load and clean the dataset
df = pd.read_csv('raw/fivemetrics_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp', 'device'])

# Create a 'month' column
df['month'] = df['timestamp'].dt.to_period('M').dt.to_timestamp()

# Group by month and count tests
monthly_tests = df.groupby('month').size().reset_index(name='total_tests')

# Format month for display
monthly_tests['month_str'] = monthly_tests['month'].dt.strftime('%Y - %m')

# Plot
plt.figure(figsize=(12, 4))
plt.bar(monthly_tests['month_str'], monthly_tests['total_tests'], color='skyblue')
plt.title("Total Number of Tests per Month (All Devices)")
plt.xlabel("Month")
plt.ylabel("Total Tests")
plt.xticks(rotation=90)
plt.tight_layout()
plt.grid(axis='y')
plt.show()


#3.3B Breakdown by data source (stacked bar chart recommended)
import pandas as pd
import matplotlib.pyplot as plt

# Load and clean the dataset
df = pd.read_csv('raw/fivemetrics_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp', 'device'])

# Create a 'month' column
df['month'] = df['timestamp'].dt.to_period('M').dt.to_timestamp()

# Group by month and device to count tests
monthly_device_counts = df.groupby(['month', 'device']).size().unstack(fill_value=0)

# Plot stacked bar chart
monthly_device_counts.index = monthly_device_counts.index.strftime('%Y-%m')
monthly_device_counts.plot(kind='bar', stacked=True, figsize=(14, 6), colormap='tab20')
plt.title("Monthly Test Counts by Data Source (Device)")
plt.xlabel("Month")
plt.ylabel("Number of Tests")
plt.xticks(rotation=90)
plt.legend(title='Device', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.grid(axis='y')
plt.show()





#3.3C Identify any gaps or unusual patterns in data collection
import pandas as pd
import matplotlib.pyplot as plt

# Load and clean the dataset
df = pd.read_csv('raw/fivemetrics_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp'])

# Create a 'month' column
df['month'] = df['timestamp'].dt.to_period('M').dt.to_timestamp()

# Count tests per month
monthly_counts = df.groupby('month').size().reset_index(name='test_count')

# Calculate rolling mean and flag dips
monthly_counts['rolling_mean'] = monthly_counts['test_count'].rolling(window=3, center=True).mean()
monthly_counts['is_gap'] = monthly_counts['test_count'] < 0.5 * monthly_counts['rolling_mean']

# Display flagged months
gaps = monthly_counts[monthly_counts['is_gap'] | (monthly_counts['test_count'] == 0)]
print("Gaps or unusual dips in data collection:")
print(gaps[['month', 'test_count']])

# Plot with annotations
plt.figure(figsize=(12, 5))
plt.plot(monthly_counts['month'], monthly_counts['test_count'], marker='o', label='Monthly Tests')
plt.plot(monthly_counts['month'], monthly_counts['rolling_mean'], linestyle='--', label='3-Month Rolling Mean')
for _, row in gaps.iterrows():
    plt.annotate('Gap', xy=(row['month'], row['test_count']), xytext=(row['month'], row['test_count'] + 5),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontsize=9, color='red')
plt.title("Monthly Test Counts with Gaps Highlighted")
plt.xlabel("Month")
plt.ylabel("Test Count")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()



import pandas as pd
from datetime import datetime, timedelta
df = pd.read_csv('raw/fivemetrics_data.csv')

# Set pandas options to show full column content and width
pd.set_option('display.max_columns', None)      # Show all columns in output
pd.set_option('display.max_colwidth', None)     # Don't truncate column content
pd.set_option('display.width', None)            # Auto-adjust display width for terminal

# Your existing code to generate descriptive stats
metrics_of_interest = [
    "Jump Height(M)",
    "Peak Propulsive Power(W)",
    "Peak Velocity(M/S)",
    "Rsi",
    "Distance_Total",
    "Speed_Max"
]

filtered_df = df[
    df['metric'].isin(metrics_of_interest)
]

percentiles = [0.1, 0.25, 0.5, 0.75, 0.9]

# Generate descriptive statistics with specified percentiles for GROUPTEAM and METRIC
desc_statsseparate = filtered_df.groupby(['groupteam', 'metric'])['value'].describe(percentiles=percentiles)

# Generate descriptive statistics with specified percentiles for METRIC ALL TEAMS
desc_statsall = filtered_df.groupby(['metric'])['value'].describe(percentiles=percentiles)

print('\nPercentile description by all sports:\n', desc_statsall.to_string())
print('\nPercentile description by separated teams:\n', desc_statsseparate.to_string())