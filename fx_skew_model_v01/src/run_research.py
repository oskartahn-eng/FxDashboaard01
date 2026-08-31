from pathlib import Path
import argparse,pandas as pd,yaml
from features import build_dataset
from backtest import walk_forward,summarize,current_scores
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--output-dir",default="."); a=ap.parse_args(); root=Path(a.output_dir); (root/"data/processed").mkdir(parents=True,exist_ok=True); (root/"reports").mkdir(parents=True,exist_ok=True)
    cfg=yaml.safe_load(open("config.yaml",encoding="utf-8")); df=pd.read_csv(a.input,parse_dates=["date"]); df=df[df.pair.isin(cfg["pairs"])].copy(); ds=build_dataset(df,cfg["zscore_window"],tuple(cfg["change_windows"]),tuple(cfg["target_horizons"])); ds.to_csv(root/"data/processed/features.csv",index=False)
    bt=walk_forward(ds,horizon=10,min_training_days=cfg["minimum_training_days"],C=cfg["model"]["C"]); bt.to_csv(root/"reports/backtest_predictions.csv",index=False); sm=summarize(bt); sm.to_csv(root/"reports/backtest_summary.csv",index=False); scores=current_scores(ds,horizon=10,min_training_days=cfg["minimum_training_days"],C=cfg["model"]["C"]); scores.to_csv(root/"reports/current_scores.csv",index=False); print("=== SUMMARY ==="); print(sm.to_string(index=False) if not sm.empty else "No rows"); print("=== SCORES ==="); print(scores.to_string(index=False) if not scores.empty else "No scores")
if __name__=="__main__": main()
