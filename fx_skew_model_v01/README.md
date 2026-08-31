# FX Options Skew Research Model — v0.1

Research-Prototyp für die Hypothese, dass die relative Position und Veränderung der 25-delta Risk-Reversal-Skew-Termstruktur (1M/3M/6M/1Y) zusätzliche Information über zukünftige FX-Renditen von Major-Paaren enthält.

## Workflow
1. Normalisierte tägliche Optionsdaten importieren.
2. Skew-/Termstruktur-Features berechnen.
3. Forward Returns als Targets erzeugen.
4. Walk-Forward-Backtest durchführen.
5. Wahrscheinlichkeiten und Opportunity Score berechnen.
6. Erst danach komplexere ML-Modelle testen.

## CSV-Schema
`date,pair,spot,atm_1m,atm_3m,atm_6m,atm_1y,rr25_1m,rr25_3m,rr25_6m,rr25_1y`

Die RR-Vorzeichenkonvention muss über den gesamten historischen Datensatz konstant und dokumentiert sein.

## Start
```bash
pip install -r requirements.txt
python src/make_sample_data.py
python src/run_research.py --input data/raw/fx_options_daily.csv
```

Die Sample-Daten dienen nur dazu, die Pipeline technisch zu prüfen und sind nicht für Trading-Aussagen geeignet.
