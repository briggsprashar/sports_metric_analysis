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
    df['groupteam'].str.contains('football|basketball', case=False, na=False) &
    df['metric'].isin(metrics_of_interest)
]

percentiles = [0.1, 0.25, 0.5, 0.75, 0.9]

# Generate descriptive statistics with specified percentiles for GROUPTEAM and METRIC
desc_statsseparate = filtered_df.groupby(['groupteam', 'metric'])['value'].describe(percentiles=percentiles)

# Generate descriptive statistics with specified percentiles for METRIC ALL TEAMS
desc_statsall = filtered_df.groupby(['metric'])['value'].describe(percentiles=percentiles)

print('\nPercentile description by all sports:', desc_statsall)
print('\nPercentile description by separated teams:', desc_statsseparate)

