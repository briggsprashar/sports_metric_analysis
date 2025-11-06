import pandas as pd
import os

# Load preselection dataset
raw_data = pd.read_csv('raw/preselection.csv')

####### CREATING FINAL DATASET WITH METRICS OF INTEREST ##########

# Remove duplicate rows based on all columns except 'ID'
clean_data = raw_data.drop_duplicates(subset=[col for col in raw_data.columns if col != 'ID'])

# Define metrics of interest
metrics_five = ['Speed_Max', 'Jump Height(M)', 'Rsi', 'Peak Velocity(M/S)', 'Peak Propulsive Force(W)', 'Distance_Total']

# Filter rows where 'metric' column matches one of the selected metrics
response_subset = clean_data[clean_data['metric'].isin(metrics_five)]

# Create a new DataFrame with only the relevant columns
# Adjust this list based on which columns you want to keep
columns_to_keep = ['id', 'playername', 'timestamp', 'device', 'metric', 'value', 'team', 'sportsteam', 'groupteam']  # example column names
fivemetrics_data = response_subset[columns_to_keep]

# Ensure 'raw' folder exists
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

# Save final dataset to CSV
output_path = os.path.join(raw_folder, "fivemetrics_data.csv")
fivemetrics_data.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")
