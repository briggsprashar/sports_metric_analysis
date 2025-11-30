import os
from pathlib import Path
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats   # only this is needed for linregress

# --- Config ---
PLAYER_ID = "PLAYER_741"
# Build a path to the data file relative to this script file so the script
# works no matter which directory the user runs it from.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INPUT_FILE = DATA_DIR / "sixmetricsclass 3.csv"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "tables")
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# --- Load Data ---
# Ensure the path is a string for better compatibility with type-checkers
df: pd.DataFrame = pd.read_csv(str(INPUT_FILE))
print("Columns in CSV:", df.columns.tolist())  # quick check
player_df: pd.DataFrame = df[df["playername"] == PLAYER_ID].copy()
player_df["timestamp"] = pd.to_datetime(player_df["timestamp"])
# Exclude the 'Mrsi' metric from this player's analysis (case-insensitive)
player_df = player_df[~player_df["metric"].str.lower().eq("mrsi")]

# --- Best/Worst Dates ---
idx_max = player_df.groupby("metric")["value"].idxmax()  # type: ignore
idx_min = player_df.groupby("metric")["value"].idxmin()  # type: ignore

best = player_df.loc[idx_max, ["metric", "timestamp", "value"]].rename(
    columns={"timestamp": "best_date", "value": "best_value"}
)
worst = player_df.loc[idx_min, ["metric", "timestamp", "value"]].rename(
    columns={"timestamp": "worst_date", "value": "worst_value"}
)
best_worst = best.merge(worst, on="metric")

best_worst.to_csv(os.path.join(OUTPUT_DIR, "best_worst_dates.csv"), index=False)

# --- Regression Trends ---
regression_results = []
for metric, g in player_df.groupby("metric"):
    g = g.sort_values("timestamp")
    if len(g) > 1:
        x = g["timestamp"].map(pd.Timestamp.toordinal)
        y = g["value"]
        result = stats.linregress(x, y)
        regression_results.append({
            "metric": metric,
            "slope": result.slope,
            "r_value": result.rvalue,
            "p_value": result.pvalue,
            "std_err": result.stderr
        })

regression_df = pd.DataFrame(regression_results)
regression_df.to_csv(os.path.join(OUTPUT_DIR, "regression_stats.csv"), index=False)

# Also write this player's regression stats to a central folder so all player
# regression CSVs are available in one place (one file per player).
CENTRAL_DIR = Path(__file__).resolve().parent.parent / "central_stats"
CENTRAL_DIR.mkdir(exist_ok=True)
central_path = CENTRAL_DIR / f"{PLAYER_ID}_regression_stats.csv"
regression_df.to_csv(central_path, index=False)
# Also append this player's stats to a combined central CSV (one file for all players)
combined_path = CENTRAL_DIR / "all_regression_stats.csv"
to_write = regression_df.copy()
to_write["player"] = PLAYER_ID
# append with header only if file doesn't exist yet
to_write.to_csv(combined_path, mode="a", header=not combined_path.exists(), index=False)
print(regression_df)

# --- Plots ---
for metric, g in player_df.groupby("metric"):
    plt.figure(figsize=(8, 4))
    sns.lineplot(data=g, x="timestamp", y="value")
    plt.title(f"{PLAYER_ID} - {metric} over time")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.tight_layout()
    # Sanitize metric name for a safe filename (remove/replace path separators and illegal chars)
    metric_str = str(metric)
    safe_metric = re.sub(r"[\\/:*?\"<>|]", "_", metric_str)
    safe_metric = safe_metric.replace(' ', '_')
    plt.savefig(os.path.join(PLOTS_DIR, f"{safe_metric}.png"))
    plt.close()

print(f"Analysis complete for {PLAYER_ID}. Outputs saved in tables/ and plots/")
print(player_df.groupby("metric")["value"].count())
