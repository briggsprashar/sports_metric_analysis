import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from typing import cast, List
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import hmac
import hashlib
from dotenv import load_dotenv
load_dotenv()

# Get database connection details
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Load dataset from shared team file
df: pd.DataFrame = pd.read_csv(
    "teamsworkspacescripts/fivemetrics_data 2.csv",  # <-- shared input
    dtype={
        "playername": str,
        "metric": str,
        "team": str,
        "value": float,
    },
    parse_dates=["timestamp"],
    low_memory=False,
)  # type: ignore

# Coerce timestamp parsing
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')  # type: ignore

# Drop rows with null or zero values
df = df[df['value'].notnull() & (df['value'] != 0)].copy()

# Filter athletes tested in the last 6 months
cutoff_date = datetime.now() - timedelta(days=180)
recent_tests = df[df['timestamp'] >= cutoff_date].copy()

# Extract active players
active_players: List[str] = cast(
    List[str],
    recent_tests['playername'].dropna().astype(str).unique().tolist(),
)
df = df[df['playername'].isin(active_players)].copy()  # type: ignore

# Save cleaned dataset
cleaned_path = "teamsworkspacescripts/naira_docs/naira_cleaned_data.csv"
df.to_csv(cleaned_path, index=False)
print(f"✓ Cleaned dataset saved with {len(df)} rows to '{cleaned_path}'.")

# Summary of missing and zero values
missing_summary = cast(pd.Series, df.groupby('metric')['value'].apply(lambda x: int(x.isnull().sum())))  # type: ignore
zero_summary = cast(pd.Series, df.groupby('metric')['value'].apply(lambda x: int((x == 0).sum())))  # type: ignore
print("\nMissing values per metric:\n", missing_summary)
print("\nZero values per metric:\n", zero_summary)

# Athlete coverage per sport
coverage = cast(pd.Series, df.groupby('team')['playername'].nunique().sort_values(ascending=False))  # type: ignore
print("\nAthlete coverage per sport:\n", coverage)

# Create plots folder
plot_dir = "teamsworkspacescripts/naira_docs/plots"
os.makedirs(plot_dir, exist_ok=True)

# Metric-wise distribution plots
for metric in df['metric'].dropna().unique():
    subset = cast(pd.DataFrame, df[df['metric'] == metric])
    values = subset['value']
    if values.empty:
        print(f"⚠️ No valid data for metric '{metric}'. Skipping.")
        continue
    fig: Figure = plt.figure(figsize=(8, 4))  # type: ignore
    ax: Axes = fig.add_subplot(1, 1, 1)  # type: ignore
    sns.histplot(data=subset, x='value', bins=30, kde=True, ax=ax)  # type: ignore
    ax.set_title(f'Distribution of {metric}')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    fig.tight_layout()
    safe_metric = str(metric).replace("/", "_").replace(" ", "_")
    fname = os.path.join(plot_dir, f"{safe_metric}_distribution.png")
    fig.savefig(fname)  # type: ignore
    plt.close(fig)

print(f"✓ Distribution plots saved to '{plot_dir}'.")

# Anonymize player names using HMAC
ANON_KEY = os.getenv("ANON_KEY")
if not ANON_KEY:
    raise RuntimeError(
        "ANON_KEY environment variable is required for anonymization. "
        "Set ANON_KEY in your environment (do NOT commit the key to source control)."
    )

def pseudonymize_name(name: str, key: str = ANON_KEY, length: int = 10) -> str:
    digest = hmac.new(key.encode("utf-8"), name.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"PLAYER_{digest[:length].upper()}"

df['playername'] = df['playername'].map(lambda x: pseudonymize_name(str(x)) if pd.notna(x) else x)

# Save anonymized version
anon_path = "teamsworkspacescripts/naira_docs/naira_cleaned_anonymized.csv"
df.to_csv(anon_path, index=False)
print(f"✓ Player names pseudonymized and saved to '{anon_path}'.")

print("ANON_KEY loaded:", os.getenv("ANON_KEY"))

