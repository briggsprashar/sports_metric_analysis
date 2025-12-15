from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Load database connection parameters from environment variables
# (renamed username variable to avoid conflict with Windows reserved words)
sql_username = os.getenv('POWERUSER')
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

sql_username

# Construct SQLAlchemy connection string for MySQL using pymysql driver
url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"
conn = create_engine(url_string)

# SQL query to retrieve the full dataset (no row limit applied)
sql_toexecute = """
  select *
  from research_experiment_refactor_test
"""
raw_data = pd.read_sql(sql_toexecute, conn)

# Keep only rows where 'value' is numeric and non-null
raw_data = raw_data[pd.to_numeric(raw_data['value'], errors='coerce').notnull()]

# Normalize entries in 'metric' column by stripping whitespace and standardizing case
raw_data['metric'] = raw_data['metric'].str.strip().str.title()

####### PART 1: PRE-SELECTION AND DATA MANAGEMENT ##########

# Select a subset of relevant columns for downstream analysis
relevantcolumn = raw_data[['id', 'playername', 'timestamp', 'device', 'metric', 'value', 'team', 'data_source']].copy()

# Function to classify teams into broader sport categories, with gender-specific labels where applicable
def groupteam_from_team(team: str) -> str:
    team_lower = str(team).lower()
    sports = [
        "football", "basketball", "baseball", "softball", "soccer",
        "lacrosse", "cross country", "track", "swimming and diving",
        "tennis", "volleyball"
    ]
    for sport in sports:
        if sport in team_lower:
            if "women" in team_lower:
                return f"Women's {sport.title()}"
            elif "men" in team_lower:
                return f"Men's {sport.title()}"
            else:
                return sport.title()
    return "OTHERS"

# Apply classification function to create 'groupteam' column
relevantcolumn['groupteam'] = relevantcolumn['team'].apply(groupteam_from_team)

# Identify rows with missing or zero values in 'value' column
mask = (relevantcolumn['value'].isna()) | (relevantcolumn['value'] == 0)
problem_rows = relevantcolumn.loc[mask]

# Summarize problematic rows by device and grouped team
device_team_issues = (
    problem_rows.groupby(['device', 'groupteam'])
    .size()
    .reset_index(name='count')
)

# Count total number of problematic rows
total_problem_rows = problem_rows.shape[0]

print(device_team_issues)
print("Total problematic rows:", total_problem_rows)

# Count distinct grouped teams present in dataset
unique_groupteam_count = relevantcolumn['groupteam'].nunique()
print("Unique groupteam count:", unique_groupteam_count)

# Frequency distribution of grouped teams
groupteam_frequency = relevantcolumn['groupteam'].value_counts().reset_index()
groupteam_frequency.columns = ['groupteam', 'count']
print(groupteam_frequency)

# Re-define grouping function for a narrower focus (Football and Basketball only)
# Adds 'groupteam' column with gender-specific labels where available
def groupteam_from_team(team):
    for sport in ['Football', 'Basketball']:
        if sport in team:
            return f"Women's {sport}" if "Women" in team else f"Men's {sport}" if "Men" in team else sport
    return "OTHERS"

relevantcolumn['groupteam'] = relevantcolumn['team'].apply(groupteam_from_team)
print(relevantcolumn['groupteam'].value_counts())

# Simplify team names to sport-only labels in new 'sportsteam' column
def groupteam_from_team(team):
    for sport in ['Football', 'Basketball']:
        if sport in team:
            return sport
    return "OTHERS"

relevantcolumn['sportsteam'] = relevantcolumn['team'].apply(groupteam_from_team)
print(relevantcolumn['groupteam'].value_counts())

# Filter dataset to exclude rows labeled as 'OTHERS' in 'sportsteam'
cleansports = relevantcolumn[relevantcolumn['sportsteam'] != 'OTHERS']
print(cleansports['groupteam'].value_counts())
print(cleansports['sportsteam'].value_counts())

# Save cleaned and pre-selected dataset to CSV in 'raw' folder
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

output_path = os.path.join(raw_folder, "preselection.csv")
cleansports.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")
