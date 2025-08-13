
# Berlin Venue Scraper — Step 1 (Research, Tooling, Schema & PoC)

This package gives you a durable foundation for collecting data on restaurants, bars, and cafés in **Berlin**, with a schema designed for re-use in other cities. It prioritizes **OpenStreetMap (OSM) via Overpass API** as the cost-free, scalable primary source and includes **optional enrichment** hooks for Google Places and Yelp Fusion for ratings, price level, photos, and hours (if you choose to pay for them and have API keys).

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
export GOOGLE_PLACES_API_KEY="your_key"   # optional
export YELP_API_KEY="your_key"            # optional
python run_poc.py --limit 200 --out data/berlin_venues.csv
```
