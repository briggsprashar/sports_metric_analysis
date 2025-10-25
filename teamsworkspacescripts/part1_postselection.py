import pandas as pd
import os

# Load preselection dataset
raw_data = pd.read_csv('raw/preselection.csv')

####### CREATING FINAL DATASET WITH METRICS OF INTEREST ##########
# Creating subset of data for specific metrics of interest (will change once team decides on which metrics to focus on)
# viewing list of unique entries in metric column

# removing duplicate rows based even if ID number is different
clean_data = raw_data.drop_duplicates(subset=[col for col in raw_data.columns if col != 'ID'])

# Selecting five metrics of interest
metrics_five = ['Braking Rfd(N/s)', 'Jump Height(M)', 'Rsi', 'Time To Stabilization(Ms)', 'Peak Landing Force(N)']
response_subset = clean_data[clean_data['metric'].isin(metrics_five)]

# saving final dataset to CSV in 'raw' folder (ensure 'raw' folder exists)
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

# Save final dataset to CSV
output_path = os.path.join(raw_folder, "fivemetrics_data.csv")
fivemetrics_data.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")
