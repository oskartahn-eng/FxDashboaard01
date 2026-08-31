from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
FEATURES=["z_skew_1m_1y","z_skew_1m_3m","z_skew_1m_6m","d5_skew_1m_1y","d20_skew_1m_1y","z_skew_3m_1y","atm_slope_1m_1y","spot_ret_5d","spot_ret_20d"]
def make_model(C=1.0): return Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler()),("model",LogisticRegression(C=C,max_iter=3000))])
def walk_forward(df,features=FEATURES,horizon=10,min_training_days=756,retrain_every=5,C=1.0):
    rows=[]
    for pair,g in df.groupby("pair",sort=False):
        g=g.sort_values("date").reset_index(drop=True); target=f"fwd_up_{horizon}d"; retcol=f"fwd_ret_{horizon}d"; g=g.dropna(subset=[retcol]).copy()
        if len(g)<=min_training_days: continue
        for i in range(min_training_days,len(g),retrain_every):
            train=g.iloc[:i].dropna(subset=features+[target]); test=g.iloc[i:i+retrain_every].dropna(subset=features)
            if train.empty or train[target].nunique()<2 or test.empty: continue
            model=make_model(C); model.fit(train[features],train[target].astype(int)); p=model.predict_proba(test[features])[:,1]
            x=test[["date","pair",retcol]].copy(); x["prob_up"]=p; x["signal"]=p-.5; rows.append(x)
    if not rows: return pd.DataFrame(columns=["date","pair","fwd_ret","prob_up","signal"])
    return pd.concat(rows,ignore_index=True).rename(columns={f"fwd_ret_{horizon}d":"fwd_ret"}).sort_values(["pair","date"]).reset_index(drop=True)
def summarize(bt):
    if bt.empty: return pd.DataFrame()
    result=[]
    for pair,g in bt.groupby("pair"):
        up=(g.fwd_ret>0).astype(int); auc=roc_auc_score(up,g.prob_up) if up.nunique()>1 else np.nan
        strat=np.where(g.prob_up>=.55,g.fwd_ret,np.where(g.prob_up<=.45,-g.fwd_ret,0.0))
        result.append({"pair":pair,"observations":len(g),"mean_fwd_return":g.fwd_ret.mean(),"median_fwd_return":g.fwd_ret.median(),"directional_hit_rate":((g.prob_up>=.5).astype(int)==up).mean(),"auc":auc,"mean_strategy_return":strat.mean(),"positive_strategy_fraction":np.mean(strat>0)})
    return pd.DataFrame(result)
def current_scores(df,features=FEATURES,horizon=10,min_training_days=756,C=1.0):
    rows=[]
    for pair,g in df.groupby("pair"):
        target=f"fwd_up_{horizon}d"; train=g.dropna(subset=features+[target]); live=g.dropna(subset=features).tail(1)
        if len(train)<min_training_days or live.empty or train[target].nunique()<2: continue
        model=make_model(C); model.fit(train[features],train[target].astype(int)); p=float(model.predict_proba(live[features])[:,1][0]);
        rows.append({"date":live.date.iloc[0],"pair":pair,"prob_up_10d":p,"direction":"BASE_UP" if p>=.5 else "BASE_DOWN","opportunity_score":100*min(1,abs(p-.5)/.5)})
    return pd.DataFrame(rows)
