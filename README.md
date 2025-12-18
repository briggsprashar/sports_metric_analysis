# Athletics Performance Analytics

*Refer to [Project.md](https://github.com/SBU-Sports-Metrics/507_groupproject_2025/blob/main/Project.md) for detailed information about the project*

## Table of Contents

1. [Keywords](#keywords)
2. [Description](#1-description)
3. [Project workflow](#project-workflow)
4. [Team](#2-team)
5. [Setup Instructions](#3-setup-instructions)
5. [Database Connection Instructions](#4-database-connection-instructions)
5. [How to run each script](#5-how-to-run-each-script)
6. [Github Folder structure](#6-github-folder-structure)


## Keywords

- Exploratory data analytics (EDA)
- Federated analytics
- Python
- MySQL database (remote connection)
- `.env` credentialing (secure connection)
- Sanitized dataset (privacy secured)
- Literature review (theoretical basis)
- Framework based inquiry (robust methodology)
- Research question (focused approach)
- Sports performance constructs (RFD & ME&GC)
- Sports metrics
- Statistical patterns/trends
- Data visualization
- Gender gap in sports testing 
- Research gap identification

[TOC](#table-of-contents)

---

## 1. Description

This project is research-oriented exploratory data analysis (EDA) project using an existing SBU athlete sport-performance sanitized dataset. It involves **federated analytics** including data-cleaning, transformation and extraction to make the data direct query-based to do further exploratory data analysis (EDA) using lightweight ad-hoc querying.  

A literature review based research question and hypothesis guided the EDA.

The unified collegiate athletics dataset had data different metrics captured from Hawkins, Kinexion and Vald. This data was stored in long format for each athlete and test, giving detailed, timestamped performance metrics for the anonymized athletes across multiple teams across various metrics and data-source devices. Each row had a unique test. About a million rows were usable due to lack of appropriate data.

[TOC](#table-of-contents)

---

### Project Workflow

**Parts 1-3**
- Setup IDE, environments and dependencies
- Connected to the database
- Explored the structure
- Assessed data quality 
- Based on literature review/research question
    - Selected 1 sport; *(initially focused on multiple sports)*
    - Selected 5 key metrics *(initially were 6 metrics)*
- Cleaned and transformed the data 
- Original data was long-form
    - Reshaped the data into wide-format for partial analysis 
    - Used long form only for most parts of the project.
- Created a simple derived metrics for analysis
    - Explored creating a composite derived metric, but did not pursue it.
- Statistical testing
    - z-scores, t-tests, p-values, simple regression
- Created visualizations for pattern/trend detection
    - Box plots, violin plots, line charts, Streamlit app
- Analyzed performance trends over time for selected individual players (2 males and 2 females) 
- Compared individual players results with team results
- Ran statistical tests to see if there are any correlations, significance and larger performance patterns for individual players and teams.
- Created visualizations to help understand patterns in the data. 
- Created a simple <a href="https://507groupproject2025-gtiyppvvdgrfcijefzwtqz.streamlit.app/">Streamlit App</a> for visualizations

**Part 4**
- Developed a performance flagging system based on evidence‑based thresholds 
- Generated a CSV of flagged athletes

**Documentation**
- Summarized findings, insights and recommendations.
- Recorded findings in various written reports and a slide-deck
- The reproducible code and documentation are available on <a href= "https://github.com/SBU-Sports-Metrics/507_groupproject_2025">GitHub</a>.

**Project Management**

- This <a href="https://github.com/SBU-Sports-Metrics/Project-Workflow">artifact</a> was used to initially establish a workflow
- Later <a href="https://github.com/orgs/SBU-Sports-Metrics/projects/1/views/1">GitHub Project</a> was used to manage the full project lifecycle.

<br />

[TOC](#table-of-contents)

---

## 2. Team 

- Siddikha Abrahim: Research Analyst
- Naira Khergiani: Research Analyst
- Jaison Philip: Research Analyst
- Paul Quimbo: Lead Coder
- Briggs Prashar: Project Lead

*Details under Resources > Team in `Project.md`*

<br />

[TOC](#table-of-contents)

---

## 3. Setup Instructions

1. Clone this GitHub Repository

    ```bash
    https://github.com/SBU-Sports-Metrics/507_groupproject_2025.git
    ```
    Clone from Terminal or IDE UI
    
    In Visual Studio Code > Clone using Command Palette > `Shift + Command + P` (or `Ctrl + Shift + P` on Windows/Linux)


2. Create Virtual Environment

    ```bash
    python3 -m venv venv or python -m venv venv
    ```
    Clone from Terminal or IDE UI
    
    In Visual Studio Code > Clone using Command Palette > `Shift + Command + P` (or `Ctrl + Shift + P` on Windows/Linux)


3. Install Dependencies**

    ```bash
    pip install -r requirements.txt (terminal)
    or
    ! pip install -r requirements.txt (for Jupyter notebooks)
    ```
    Clone from Terminal or IDE UI when cloning the GitHub repo
        
    In Visual Studio Code > Clone using Command Palette > `Shift + Command + P` (or `Ctrl + Shift + P` on Windows/Linux)

<br />

[TOC](#table-of-contents)

---

## 4. Database Connection Instructions

4. Create a `.env` file to add database credentials
    
    ```env
    DB_HOST=secret hostname
    DB_PORT=secret portname
    DB_USER=secret username
    DB_PASS=secret password
    DB_NAME=secret database
    ```
    *can also a specific `table` to the .env file*

5. Load Environment Variables in Python

    ```python
    from dotenv import load_dotenv
    import os

    load_dotenv()

    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")
    ```

6. Connect to the Database
    ```python
    from sqlalchemy import create_engine

    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    )
    ```

    *Alternatively, create a separate `url string` first and then call it `engine = create_engine(url)` to create the connection engine*

<br />

[TOC](#table-of-contents)

---

## 5. How to Run Each Script

Part 1 — Exploration

- Script file name: `part1.1_exploration.py` 
- Use the command below or use other IDE UI methods to run the script file

    ```bash
    python part1_exploration.py
    ```
- Extracted output(s): `raw.csv` - contains raw data but converted metrics to string

Part 2 - Cleaning
- Script file name: `part2_cleaning.py `
- Use the command below or use other IDE UI methods to run the script file

    ```bash
    python part2_cleaning.py
    ```
    - Extracted file(s)
        - `cleanssports_filtered.csv` - all sports data with men and women
        - `fivemetrics_allsports.csv` - contains only 5 metrics but all sports
        - `athlete_zscores.csv` - contains all sports 5 metrics with z-scores 

Part 3 - Visualizations

- Script file name with output: `part3.1_viz_individual.ipynb`
- Use the .ipynb files in Jupyter notebooks to generate visualizations from source files listed in the code. Save these source files in a separate folder.

    ```bash
    jupyter notebook workflow
    ```
- Extracted output(s): `selected_players_data.csv` - only contains 4 players with 5 metrics with slope, trending and p_value.

- Script file name with output: `part3.2_viz_comparison.ipynb` 
- Use the .ipynb files in Jupyter notebooks to generate visualizations from source files listed in the code. Save these source files in a separate folder.

    ```bash
    jupyter notebook workflow
    ```
- Extracted output(s): None

Part 4 - Flagging Logic

- Script file name: part4.1_flags.py
- Use the command below or use other IDE UI methods to run the script file

    ```bash
    python part4_flags.py
    ```
- Extracted output(s):
    - `players_with_baseline_2025.csv` - contains all players with baseline and current value
    - `risky_players_2025.csv` - contains STD threshold, percentile threshold, riskSTD and riskPercentile
    - `athletes_overdue_testing.csv` contains players not tested more than 30 days
    - `part4_flagged_only.csv` - list of players that are flagged only
    - `part4_flagged_all_players.csv` - list of players 


<br />

[TOC](#table-of-contents)

---

## 6. Github Folder structure

```
507_groupproject_2025/
├── output/
│   ├── part4.3_flagged_athletes.csv
├── PDF_Reports/
│   ├── Part1_Framework.pdf                    # Theoretical framework used to guide this project
│   ├── Part1_LitReview.pdf                    # Brief literature review
│   ├── Part1_Metrics.pdf                      # Research literature focused reasoning behind metric selection
│   ├── Part1_Summary.pdf                      # Summary of Exploration & Code, Key data, Top 3 metrics/source, Research and Metric selection
│   ├── Part3_Player_analysis.pdf              # Individual player analysis
│   ├── Part4_Justification.pdf                # Performance Monitoring Flag System: Threshold Justification
│   ├── Part4_FlagSystem.pdf                   # Explains the Flagging Logic
│   ├── Part4_Research_Synthesis.PDF           # 
│   ├── Part4_Presentation.pdf                 # Presentation of project overview
│   ├── Part5_Observations_Limitations.pdf     # Observtions and limitations in the project
├── scripts/
│   ├── part1.1_exploration.py                 # Initial data exploration, descriptive statistics, distributions 
│   ├── part1.2_preselection.py                # Focused on all metrics and sports
│   ├── part1.3_postselection.py               # Focused on selected metrics and sports
│   ├── part2_cleaning.py                      # Data cleaning pipeline (missing values, normalization, merging)  
│   ├── part3.1_viz_individual.py              # Individual athlete visualizations  
│   ├── part3.2_viz_comparison.py              # Group and comparative visualizations 
│   ├── part3.3_streamlit.py                   # Demo dashboard/visualization on Streamlit
│   └── part4.1_flags.py                       # Threshold logic, decline detection, and flag generation 
├── .gitignore                                 # .env, raw files, etc to ignore
├── Project.md                                 # Comprehensive project details
├── README.md                                  # Project overview
├── references.md                              # References/sources used in literature review and documentation
└── requirements.txt                           # Dependencies
```

<br />

[TOC](#table-of-contents)

---

<div align="left">⁂</div>
