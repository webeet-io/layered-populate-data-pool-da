This notebook (venue_scraper.ipynb) collects restaurants, cafes, and bars using OpenStreetMap Overpass API and can optionally enrich ratings from Foursquare Places (free tier). It saves timestamped JSON and CSV files to output/.

1) Prerequisites
Python 3.10+

The project’s virtualenv is activated (.venv)

Dependencies from requirements.txt are installed

One extra package for notebooks:

bash
Copy
Edit
pip install notebook
Optional for ratings enrichment:

Set FSQ_API_KEY in a .env file at the repo root

ini
Copy
Edit
FSQ_API_KEY=YOUR_FSQ_KEY_HERE
2) Open the Notebook
Open venue_scraper.ipynb in VS Code and select your .venv interpreter if prompted.

3) What’s in the Notebook
Cell 1: Imports + Venue schema (Pydantic)

Cell 2: Config (logging, OUTPUT_DIR, endpoints, env vars)

Cell 3: fetch_osm() — pulls OSM venues via Overpass (with retries)

Cell 4: Foursquare helpers (fsq_find_id, fsq_get_rating) — optional

Cell 5: Save helpers (save_json, save_csv)

Cell 6: Run section

Set city, lat, lon, radius, max_enrich

Runs OSM fetch, optional FSQ ratings enrichment, saves JSON/CSV

4) Run
Execute the cells top to bottom. When Cell 6 finishes, you’ll see files like:

lua
Copy
Edit
output/
  berlin_venues_YYYYMMDD_HHMMSS.json
  berlin_venues_YYYYMMDD_HHMMSS.csv
Changing the City
Edit the variables at the top of Cell 6:

python
Copy
Edit
city = "Berlin"
lat = 52.5200
lon = 13.4050
radius = 1000
max_enrich = 50  # reduce or increase based on free tier comfort
5) Ratings (No Cost Path)
Ratings are pulled from Foursquare only if FSQ_API_KEY is present.

The code limits enrichment via max_enrich and sleeps briefly between calls to stay within free limits.

If no key is set, the notebook still runs and saves venues; rating remains null.


