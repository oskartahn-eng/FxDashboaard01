from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from features import build_dataset
from backtest import current_scores

st.set_page_config(page_title="FX Skew Research", layout="wide")
st.title("FX Options Skew Research")
st.caption("25Δ Risk-Reversal Term Structure • Research Dashboard")

with st.sidebar:
    st.header("Daten")
    mode = st.radio("Quelle", ["Saxo Live", "Lokale Historie"])
    pairs = st.multiselect(
        "Majors",
        ["EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF"],
        default=["EURUSD","GBPUSD","USDJPY"],
    )
    refresh = st.button("Saxo-Daten jetzt abrufen")

raw = ROOT / "data/raw/saxo_daily.csv"

if mode == "Saxo Live":
    if refresh or not raw.exists():
        with st.spinner("Saxo snapshot wird geladen …"):
            try:
                subprocess.run(
                    [sys.executable, str(ROOT / "src/collect_daily.py")],
                    cwd=str(ROOT), check=True
                )
                st.success("Snapshot gespeichert.")
            except Exception as e:
                st.error(f"Abruf fehlgeschlagen: {e}")
    if not raw.exists():
        st.info("Noch kein Snapshot vorhanden. Klicke auf 'Saxo-Daten jetzt abrufen'.")
        st.stop()
    df = pd.read_csv(raw, parse_dates=["date"])
else:
    hist = ROOT / "data/raw/fx_options_daily.csv"
    if not hist.exists():
        st.info("Lege deine historische CSV unter data/raw/fx_options_daily.csv ab.")
        st.stop()
    df = pd.read_csv(hist, parse_dates=["date"])

df = df[df["pair"].isin(pairs)].copy()

if df.empty:
    st.warning("Für die ausgewählten Paare liegen keine Daten vor.")
    st.stop()

st.subheader("Aktueller Optionszustand")
latest = df.sort_values("date").groupby("pair").tail(1).copy()
latest["skew_slope_1m_1y"] = latest["rr25_1m"] - latest["rr25_1y"]
latest = latest[["date","pair","spot","rr25_1m","rr25_3m","rr25_6m","rr25_1y","skew_slope_1m_1y"]]
latest.columns = ["Datum","Pair","Spot","RR 1M","RR 3M","RR 6M","RR 1Y","1M-1Y Slope"]
st.dataframe(latest, use_container_width=True, hide_index=True)

st.subheader("Skew-Slope")
chart = df.sort_values("date").copy()
chart["skew_1m_1y"] = chart["rr25_1m"] - chart["rr25_1y"]
wide = chart.pivot(index="date", columns="pair", values="skew_1m_1y")
st.line_chart(wide, height=320)

st.subheader("Modellscore")
if len(df.groupby("pair").size()) > 0:
    ds = build_dataset(df)
    scores = current_scores(ds, horizon=10, min_training_days=60)
    if scores.empty:
        st.warning("Für einen belastbaren Modellscore fehlen noch genügend historische Beobachtungen.")
    else:
        st.dataframe(scores, use_container_width=True, hide_index=True)

st.divider()
st.caption("Hinweis: Saxo Live ist für aktuelle Forschung / Datensammlung eingebaut. Für einen langen, point-in-time Backtest benötigen wir einen lizenzierten historischen Optionsdatensatz.")
