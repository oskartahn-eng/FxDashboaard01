import numpy as np,pandas as pd
def make(pair,seed):
 r=np.random.default_rng(seed); d=pd.bdate_range("2014-01-01",periods=2900); spot=np.exp(np.cumsum(r.normal(0,.004,len(d)))); common=r.normal(0,.06,len(d)).cumsum(); atm=7+r.normal(0,.25,len(d)); return pd.DataFrame({"date":d,"pair":pair,"spot":spot,"atm_1m":atm+.15,"atm_3m":atm+.05,"atm_6m":atm,"atm_1y":atm-.05,"rr25_1m":-.2+common+r.normal(0,.08,len(d)),"rr25_3m":-.1+.7*common+r.normal(0,.07,len(d)),"rr25_6m":-.05+.45*common+r.normal(0,.06,len(d)),"rr25_1y":.0+.25*common+r.normal(0,.05,len(d))})
pd.concat([make("EURUSD",1),make("GBPUSD",2),make("USDJPY",3)]).to_csv("data/raw/fx_options_daily.csv",index=False)
print("sample written")
