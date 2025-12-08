# 507_groupproject_2025
SBU Athletics Performance Analytics
## Database Connection and Data Exploration

These were the steps followed in order to set up a Python environment, connect to the MySQL database, and explore the `research_experiment_refactor_test` table.

---

## Steps

- Set up a Python environment and installed the required libraries: `sqlalchemy`, `pandas`, `pymysql`, and `python-dotenv`
- Created a `.env` file to securely store database credentials
- Established a connection to the MySQL database using SQLAlchemy
- Verified the connection by querying the `research_experiment_refactor_test` table
- Loaded the results into a pandas DataFrame and printed the output
- Captured a screenshot of the query results (see below)

---


1. **Installed required libraries:**

   ```bash
   pip install sqlalchemy pandas pymysql python-dotenv
   ```

2. **Created a `.env` file** with the following variables:
   
  POWERUSER=your_username_here

  PASSWORD=your_password_here

  HOSTNAME=your_host_here

  DATABASE=your_database_name_here



## Connection with Query Code

```python
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Load credentials from environment variables
sql_username = os.getenv('POWERUSER')  
sql_password = os.getenv('PASSWORD')
sql_host = os.getenv('HOSTNAME')
sql_database = os.getenv('DATABASE')

# Create connection URL
url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"
conn = create_engine(url_string)

# Sample query to test connection
sql_toexecute = """
  SELECT *
  FROM research_experiment_refactor_test
  LIMIT 10100;
"""

# Execute query and load results into a DataFrame
response = pd.read_sql(sql_toexecute, conn)
print(response)
```
---

## Screenshots of Query Results

![Alt text](raw/project%20screenshot1.png)

![Alt text](raw/project%20screenshot2.png)



---



  Exclusion of the `.env` file was added to `.gitignore` while the `USERNAME` variable was renamed to POWERUSER avoid conflicts with Windows reserved keywords.. My query was limited to 10100 rows for initial exploration
- The group project repository is hosted at: https://github.com/SBU-Sports-Metrics/507_groupproject_2025.git

