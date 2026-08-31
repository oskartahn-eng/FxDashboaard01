from __future__ import annotations
from io import StringIO
from datetime import datetime, timezone
from pathlib import Path
import re
import requests
import pandas as pd

URL = "https://fxowebtools.saxobank.com/otc.html"
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF"]


def _num(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    # strip parenthetical daily-change text, e.g. "-0.03 (-0.13)"
    s = re.sub(r"\s*\([^)]*\)", "", s)
    try:
        return float(s)
    except ValueError:
        return None


def fetch_saxo() -> pd.DataFrame:
    r = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    tables = pd.read_html(StringIO(r.text))

    rr = None
    atm = None
    for t in tables:
        cols = [str(c).strip().lower() for c in t.columns]
        text = " ".join(cols + [str(x).lower() for x in t.astype(str).head(3).values.ravel()])
        if "25-delta risk reversal" in text or "risk reversal" in text:
            # Identify the RR table by the presence of 1m/3m/6m/1y columns.
            if all(k in text for k in ["1m", "3m", "6m", "1y"]):
                rr = t
        if "atm volatilities" in text or "atm" in text:
            if all(k in text for k in ["1m", "3m", "6m", "1y"]):
                atm = t

    if rr is None:
        raise RuntimeError("Could not find Saxo 25-delta Risk Reversal table")

    # Saxo tables have Pair / Spot / 1w / 1m / 3m / 6m / 9m / 1y.
    rr = rr.copy()
    rr.columns = [str(c).strip().lower() for c in rr.columns]
    pair_col = next((c for c in rr.columns if c == "pair"), rr.columns[0])
    spot_col = next((c for c in rr.columns if c == "spot"), None)

    out = []
    for _, row in rr.iterrows():
        pair = str(row.get(pair_col, "")).strip().upper()
        if pair not in PAIRS:
            continue
        item = {
            "date": None,
            "pair": pair,
            "spot": _num(row.get(spot_col)) if spot_col else None,
            "atm_1m": None,
            "atm_3m": None,
            "atm_6m": None,
            "atm_1y": None,
            "rr25_1m": _num(row.get("1m")),
            "rr25_3m": _num(row.get("3m")),
            "rr25_6m": _num(row.get("6m")),
            "rr25_1y": _num(row.get("1y")),
            "source": "Saxo FX Options Analytics",
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        out.append(item)

    result = pd.DataFrame(out)
    if result.empty:
        raise RuntimeError("Saxo parser returned no target pairs")

    # Try to read the report date from page text is intentionally omitted here.
    # The collection date is the date on which our process retrieved the snapshot.
    result["date"] = pd.Timestamp.now(tz="UTC").normalize()
    return result


def append_snapshot(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    latest = fetch_saxo()
    if path.exists():
        old = pd.read_csv(path, parse_dates=["date"])
        combined = pd.concat([old, latest], ignore_index=True)
    else:
        combined = latest
    combined["date"] = pd.to_datetime(combined["date"], utc=True)
    # One snapshot per pair/day. If re-run on the same day, keep the latest retrieval.
    combined = combined.sort_values("retrieved_at_utc").drop_duplicates(["date", "pair"], keep="last")
    combined.to_csv(path, index=False)
    return combined

if __name__ == "__main__":
    p = Path("data/raw/saxo_daily.csv")
    df = append_snapshot(p)
    print(df.tail(10).to_string(index=False))
