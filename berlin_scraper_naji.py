import requests
import json
import csv
import logging
import os
import argparse
import time
from datetime import datetime
from tenacity import retry, wait_exponential, stop_after_attempt
from models import Venue
from dotenv import load_dotenv

load_dotenv()

# -------- Logging --------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("venue_scraper.log"), logging.StreamHandler()],
)

# -------- Config --------
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"

FSQ_API_KEY = os.getenv("FSQ_API_KEY")  # Optional. If absent, we skip ratings.
FSQ_SEARCH_URL = "https://api.foursquare.com/v3/places/search"
FSQ_DETAILS_URL = "https://api.foursquare.com/v3/places/{fsq_id}"

FSQ_HEADERS = {"Authorization": FSQ_API_KEY} if FSQ_API_KEY else {}

# -------- Overpass (free OSM base data) --------
@retry(wait=wait_exponential(multiplier=2, min=4, max=60), stop=stop_after_attempt(5))
def fetch_osm(lat: float, lon: float, radius: int):
    logging.info(f"Requesting OSM data (lat={lat}, lon={lon}, radius={radius}m)...")
    query = f"""
    [out:json][timeout:300];
    node["amenity"~"restaurant|cafe|bar"](around:{radius},{lat},{lon});
    out;
    """
    resp = requests.post(OVERPASS_ENDPOINT, data={"data": query}, timeout=60)
    resp.raise_for_status()
    return resp.json()

# -------- Foursquare enrichment (ratings 0–10) --------
def fsq_find_id(name: str, lat: float, lon: float) -> str | None:
    if not FSQ_API_KEY:
        return None
    try:
        # Tight radius to avoid wrong matches; tweak if needed
        params = {"ll": f"{lat},{lon}", "radius": 75, "query": name, "limit": 1}
        r = requests.get(FSQ_SEARCH_URL, headers=FSQ_HEADERS, params=params, timeout=15)
        r.raise_for_status()
        items = r.json().get("results", [])
        return items[0]["fsq_id"] if items else None
    except Exception as e:
        logging.debug(f"FSQ search failed for {name}: {e}")
        return None

def fsq_get_rating(fsq_id: str) -> float | None:
    if not FSQ_API_KEY or not fsq_id:
        return None
    try:
        r = requests.get(FSQ_DETAILS_URL.format(fsq_id=fsq_id), headers=FSQ_HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("rating")  # 0.0–10.0 where available
    except Exception as e:
        logging.debug(f"FSQ details failed for {fsq_id}: {e}")
        return None

# -------- Save helpers --------
def save_json(data, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved JSON: {path}")

def save_csv(venues, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "latitude",
                "longitude",
                "venue_type",
                "cuisine_type",
                "address",
                "contact_info",
                "opening_hours",
                "rating",   # now filled if FSQ key provided
                "source",
            ],
        )
        writer.writeheader()
        for v in venues:
            writer.writerow(v)
    logging.info(f"Saved CSV: {path}")

def main():
    parser = argparse.ArgumentParser(description="Venue scraper (OSM base + optional Foursquare ratings).")
    parser.add_argument("--city", required=True, help="City name (for filenames).")
    parser.add_argument("--lat", type=float, required=True, help="Latitude of city center.")
    parser.add_argument("--lon", type=float, required=True, help="Longitude of city center.")
    parser.add_argument("--radius", type=int, default=1000, help="Search radius in meters.")
    parser.add_argument("--max_enrich", type=int, default=1000, help="Max venues to try rating enrichment for (to stay within free limits).")
    parser.add_argument("--sleep_ms", type=int, default=120, help="Sleep milliseconds between FSQ calls to be polite.")
    args = parser.parse_args()

    try:
        osm = fetch_osm(args.lat, args.lon, args.radius)
        if "elements" not in osm or not osm["elements"]:
            logging.error(f"No OSM results for {args.city}.")
            return

        # Convert to model dicts first
        venues = []
        for el in osm["elements"]:
            v = Venue(
                name=el["tags"].get("name", "Unknown"),
                latitude=el["lat"],
                longitude=el["lon"],
                venue_type=el["tags"].get("amenity", "unknown"),
                cuisine_type=el["tags"].get("cuisine"),
                address=el["tags"].get("addr:street"),
                contact_info=el["tags"].get("phone"),
                source="OpenStreetMap",
            ).model_dump()
            venues.append(v)

        logging.info(f"Collected {len(venues)} venues from OSM for {args.city}.")

        # Optional: Foursquare enrichment for ratings (0–10)
        if FSQ_API_KEY:
            logging.info(f"Enriching ratings from Foursquare (limit {args.max_enrich})...")
            enriched = 0
            for i, v in enumerate(venues):
                if enriched >= args.max_enrich:
                    break
                fsq_id = fsq_find_id(v["name"], v["latitude"], v["longitude"])
                if fsq_id:
                    rating = fsq_get_rating(fsq_id)
                    if rating is not None:
                        v["rating"] = float(rating)
                        enriched += 1
                # polite rate limiting
                time.sleep(args.sleep_ms / 1000.0)
            logging.info(f"Ratings enriched for {enriched} venues via Foursquare.")
        else:
            logging.info("FSQ_API_KEY not found — skipping ratings enrichment.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{args.city.lower()}_venues_{timestamp}"

        # Save JSON and CSV
        save_json(venues, f"{base}.json")
        save_csv(venues, f"{base}.csv")

        logging.info("Done.")
    except requests.RequestException as e:
        logging.error(f"Network error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
