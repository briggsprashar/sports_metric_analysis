# SBU Athletics Performance Analytics

## Overview

This repository contains scripts and notes for cleaning, analyzing, and
visualizing athletics performance data. It includes a privacy-preserving
anonymization step to produce pseudonymized datasets suitable for sharing.

### Dataset Structure

The cleaned dataset (`naira_cleaned_data.csv`) follows a long-format schema with the following columns:

- `id` — unique row identifier
- `playername` — anonymized athlete ID (e.g., PLAYER_1186)
- `timestamp` — date and time of measurement
- `device_metric` — performance metric name with platform prefix (e.g., kinexon_Speed Max)
- `value` — numeric measurement
- `team` — tracking system or internal label (e.g., hawkins, kinexon)
- `sports_team` — sport/team affiliation (e.g., Mens Basketball)
- `groupteam` — group label (e.g., Team: Brook Men)

## Scripts

- `naira.py` — Part 1: Connects to MySQL, previews data, summarizes metrics, and generates a PDF report.
- `part2_cleaning.py` — Part 2: Cleans data, generates plots, and produces anonymized dataset.

### Project workflow

Please refer to the `project_workflow` folder in the organization profile
repository for the full process and deliverables.

> Note: PDF files in this repo are placeholders for now.

## Team

Contributors (alphabetical by last name)

- Siddikha Abrahim
- Naira Khergiani
- Jaison Philip
- Briggs Prashar
- Paul Quimbo

For each contributor, add Role and Contributions under their name as needed.

## Anonymization & running `part2_cleaning.py`

`part2_cleaning.py` performs data cleaning, creates distribution plots, and
produces a pseudonymized dataset using a keyed HMAC. The pseudonymization is
deterministic (same input name → same pseudonym) and irreversible without the
secret key.

Key points

- Pseudonymization method: HMAC-SHA256 with a secret key (first 10 hex chars
  used as the code, prefixed by `PLAYER_`).
- The secret key is read from the environment variable `ANON_KEY`.
- The script writes an anonymized CSV to `teamsworkspacescripts/naira_cleaned_anonymized.csv`.

Quick instructions (PowerShell)

1. Install dependencies (if needed):

```powershell
pip install -r requirements.txt
# optional: install typing stubs to reduce editor diagnostics
pip install pandas-stubs matplotlib-stubs
```

2 Set a secret key in PowerShell (example — replace with a secure key stored in a vault):

```powershell
$env:ANON_KEY = 'your_secure_key_here'
python part2_cleaning.py
```

Outputs

- `naira_cleaned_data.csv` — cleaned dataset (intermediate)
- `teamsworkspacescripts/naira_cleaned_anonymized.csv` — anonymized dataset safe to share
- `plots/*_distribution.png` — saved distribution plots

Security recommendations

- Never store `ANON_KEY` in source control. Use a secret manager for production keys.
- If you require re-identification later, consider saving an encrypted mapping file (I can implement this).
- Consider reducing timestamp precision (month/year) and performing k-anonymity checks before publishing.

Optional improvements I can implement

- Add encrypted mapping (Fernet) support for authorized re-identification.
- Coarsen timestamps and implement automatic k-anonymity checks (suppress/merge small groups).
- Add a short section describing how to rotate or revoke `ANON_KEY` safely.

Generated on: 2025-11-08
