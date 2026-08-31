# Live-Daten integrieren

## Was jetzt integriert ist

Die App besitzt einen öffentlichen Saxo-Adapter. Saxo veröffentlicht eine tägliche FX-Options-Analyse mit 25Δ Risk Reversals und ATM Vols, inklusive 1M/3M/6M/1Y für EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD und USDCHF.

Die App speichert bei jedem Abruf einen Tages-Snapshot in:

`data/raw/saxo_daily.csv`

So entsteht automatisch eine eigene historische Datenbank **ab dem Tag, an dem du die Sammlung startest**.

## Start lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Dann die lokale URL öffnen, die Streamlit im Terminal ausgibt.

## Automatisch täglich sammeln

Windows Task Scheduler oder Linux cron kann einmal täglich

```bash
python src/collect_daily.py
```

ausführen.

## Wichtige Einschränkung

Die öffentliche Saxo-Seite liefert den aktuellen Snapshot und die Veränderung
gegenüber dem vorherigen Snapshot, aber keinen vollständigen frei verfügbaren
Langzeit-Archivfeed. Deshalb ist die Saxo-Integration ideal für Live-/Forward-
Sammlung, aber nicht ausreichend für einen 5-10-Jahres-Backtest.

Für Backtesting soll später ein historischer Feed (z.B. CME DataMine/QuikVol
oder OTC-FX-Vol-Surface-Datensatz) in dasselbe CSV-Schema normalisiert werden.
