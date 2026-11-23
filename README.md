# Quote of the Day

Fetch a quote, keep your favorites locally, search them, and see summaries and charts.
Quotes come from a local **mock library** for now (`data/mock_cache.json`). Set `QUOTE_SOURCE=live` to try ZenQuotes first (it falls back to mock if the network fails).

## Run
```
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py --load                  # 30 sample favorites + mock library + legacy_import_sample.csv

python ui_fasthtml/app.py              # web app at http://localhost:5001
streamlit run ui_streamlit/app.py      # analytics dashboard
python cli.py                          # terminal menu
python -m unittest discover -s tests   # tests
```
All three interfaces share `core/` and read the same `data/quotes.json`.

## Demo script
1. Open the web app, get a quote, save it with a rating.
2. Add a quote with a blank text, author "R2D2" (digits) to show validation errors.
3. Favorites: search by keyword and category, remove one.
4. Summary: metrics, warnings, three charts.
5. Import `data/legacy_import_sample.csv` to see row-by-row errors.
6. Stop and relaunch to show your saved quotes persisted; download the Markdown report.
