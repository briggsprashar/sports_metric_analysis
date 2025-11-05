from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# mapping for database connection
# need to rename the username since it conflicts with a reserved word windows

sql_username = os.getenv('POWERUSER')
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

sql_username

url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"

conn = create_engine(url_string)

# remove limit 100000; to get full dataset
sql_toexecute = """
  select *
  from research_experiment_refactor_test
  
  """

raw_data = pd.read_sql(sql_toexecute, conn)

#Removing non numeric entries and null or empty entries in 'value' column
raw_data = raw_data[pd.to_numeric(raw_data['value'], errors='coerce').notnull()]

# Standardizing responses in 'metric' column to ensure consistency (found out responses have upper/lower issues)
raw_data['metric'] = raw_data['metric'].str.strip().str.title()

####### PART 1: PRE SELECTION AND DATA MANAGEMENT OF RAW DATASET ##########
#Selecting relevant columns for analysis
relevantcolumn = raw_data[['id', 'playername', 'timestamp', 'device', 'metric', 'value', 'team', 'data_source']].copy()

#Adding new column 'groupteam' based on 'team' column to categorize into broader sports categories
def groupteam_from_team(team):
    for sport in ['Football', 'Basketball', 'Lacrosse', 'Soccer', 'Baseball']:
        if sport in team:
            return f"Women's {sport}" if "Women" in team else f"Men's {sport}" if "Men" in team else sport
    return "OTHERS"

relevantcolumn['groupteam'] = relevantcolumn['team'].apply(groupteam_from_team)

print(relevantcolumn['groupteam'].value_counts())


#adding new column sportsteam based on 'team' column to simplify team names to just sport names
def groupteam_from_team(team):
    for sport in ['Football', 'Basketball', 'Lacrosse', 'Soccer', 'Baseball']:
        if sport in team:
            return sport
    return "OTHERS"

relevantcolumn['sportsteam'] = relevantcolumn['team'].apply(groupteam_from_team)

print(relevantcolumn['groupteam'].value_counts())


#removing entries with 'OTHERS' in 'sportsteam' column to focus on main sports
cleansports = relevantcolumn[relevantcolumn['sportsteam'] != 'OTHERS']
print(cleansports['groupteam'].value_counts())
print(cleansports['sportsteam'].value_counts())


# Save preselection dataset to CSV
raw_folder = "raw"
os.makedirs(raw_folder, exist_ok=True)

output_path = os.path.join(raw_folder, "preselection.csv")
cleansports.to_csv(output_path, index=False)
print(f"Final dataset saved to: {output_path}")
