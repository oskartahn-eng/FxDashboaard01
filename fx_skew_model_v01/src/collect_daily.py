from pathlib import Path
from saxo_provider import append_snapshot

path = Path("data/raw/saxo_daily.csv")
df = append_snapshot(path)
print(f"Saved {len(df)} rows to {path}")
