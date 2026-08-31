from __future__ import annotations
import numpy as np
import pandas as pd
REQUIRED=["date","pair","spot","atm_1m","atm_3m","atm_6m","atm_1y","rr25_1m","rr25_3m","rr25_6m","rr25_1y"]
def validate_input(df):
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing: raise ValueError(f"Missing columns: {missing}")
    if (df.spot<=0).any(): raise ValueError("spot must be positive")
def add_features(df,zscore_window=252,change_windows=(1,5,20)):
    out=df.copy(); out.date=pd.to_datetime(out.date,utc=True); out=out.sort_values(["pair","date"]).reset_index(drop=True)
    out["skew_1m_3m"]=out.rr25_1m-out.rr25_3m
    out["skew_1m_6m"]=out.rr25_1m-out.rr25_6m
    out["skew_1m_1y"]=out.rr25_1m-out.rr25_1y
    out["skew_3m_1y"]=out.rr25_3m-out.rr25_1y
    cols=["rr25_1m","rr25_3m","rr25_6m","rr25_1y","skew_1m_3m","skew_1m_6m","skew_1m_1y","skew_3m_1y","atm_1m","atm_3m","atm_6m","atm_1y"]
    for n in change_windows:
        for col in cols: out[f"d{n}_{col}"]=out.groupby("pair")[col].diff(n)
    out["atm_slope_1m_1y"]=out.atm_1m-out.atm_1y
    out["atm_slope_3m_1y"]=out.atm_3m-out.atm_1y
    for n in (1,5,20): out[f"spot_ret_{n}d"]=out.groupby("pair").spot.pct_change(n)
    for col in ["skew_1m_1y","skew_1m_3m","skew_1m_6m","skew_3m_1y"]:
        g=out.groupby("pair")[col]
        mean=g.transform(lambda s:s.rolling(zscore_window,min_periods=zscore_window).mean())
        std=g.transform(lambda s:s.rolling(zscore_window,min_periods=zscore_window).std())
        out[f"z_{col}"]=(out[col]-mean)/std.replace(0,np.nan)
    return out
def add_targets(df,horizons=(1,5,10,20)):
    out=df.copy()
    for h in horizons:
        out[f"fwd_ret_{h}d"]=out.groupby("pair").spot.shift(-h)/out.spot-1
        out[f"fwd_up_{h}d"]=(out[f"fwd_ret_{h}d"]>0).astype(float)
    return out
def build_dataset(df,zscore_window=252,change_windows=(1,5,20),horizons=(1,5,10,20)):
    validate_input(df); return add_targets(add_features(df,zscore_window,change_windows),horizons)
