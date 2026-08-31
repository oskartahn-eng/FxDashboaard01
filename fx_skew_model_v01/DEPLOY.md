# Website daraus machen

## Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Dann öffnet Streamlit die Web-App lokal im Browser.

## Kostenlos online

1. GitHub-Repository anlegen.
2. Den Inhalt dieses Ordners ins Repository laden.
3. `https://share.streamlit.io` öffnen und mit GitHub anmelden.
4. `Create app` wählen.
5. Repository, Branch `main` und Datei `app.py` auswählen.
6. Deploy.

Danach erhält die App eine `streamlit.app`-URL.

Wichtig: In v0.1 werden noch keine Live-Marktdaten abgerufen. Die App kann bereits
CSV-Daten laden, Features berechnen und den Walk-Forward-Backtest anzeigen.
