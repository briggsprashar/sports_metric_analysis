import pandas as pd
import os

# Load the preselected dataset from CSV
raw_data = pd.read_csv('raw/preselection.csv')

# Keep only rows where 'value' is numeric and non-zero
raw_data = raw_data[
    pd.to_numeric(raw_data['value'], errors='coerce').notnull() &
    (pd.to_numeric(raw_data['value'], errors='coerce') != 0)
]

# Remove duplicate records based on all columns except 'ID'
clean_data = raw_data.drop_duplicates(subset=[col for col in raw_data.columns if col != 'ID'])

# Define the set of performance metrics to retain
metrics_five = [
    'Speed_Max',
    'Jump Height(M)',
    'Peak Velocity(M/S)',
    'Peak Propulsive Power(W)',
    'Distance_Total'
]

# Subset rows where 'metric' matches one of the selected metrics
response_subset = clean_data[clean_data['metric'].isin(metrics_five)]

# Select only the relevant columns for the final dataset
# Adjust this list if additional fields are required
columns_to_keep = [
    'id', 'playername', 'timestamp', 'device',
    'metric', 'value', 'team', 'sportsteam', 'groupteam'
]
fivemetrics_data = response_subset[columns_to_keep]

####### FINAL DATASET CREATION WITH METRICS OF INTEREST ##########

# Convert 'value' column to numeric for consistency
raw_data['value'] = pd.to_numeric(raw_data['value'], errors='coerce')

# Handle extreme outliers:
# Replace values less than 1% of the mean for each metric with NaN,
# then apply linear interpolation followed by backfill/forward fill
raw_data['value'] = (
    raw_data.groupby('metric')['value']
        .transform(lambda s: s.mask(s < s.mean() * 0.1)
                              .interpolate(method='linear')
                              .bfill()
                              .ffill())
)

# Ensure the 'raw' folder exists for saving outputs
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

# Save the final dataset containing the five selected metrics
output_path = os.path.join(raw_folder, "fivemetrics_data.csv")
fivemetrics_data.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")
