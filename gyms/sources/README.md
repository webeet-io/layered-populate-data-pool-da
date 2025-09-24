# Data Sources for Fitness Studios (Gyms) in Berlin

## 1. OpenStreetMap (OSM) via Overpass API

- **URL:** https://overpass-api.de/api/interpreter
- **Query:** Fetches all nodes/ways/relations in Berlin tagged as `leisure=fitness_centre` or `sport=yoga`.
- **Data fields collected:** name, leisure, sport, address (street, housenumber, postcode, city), opening_hours, phone, website, wheelchair, latitude, longitude, osm_id, osm_type.
- **Script:** The data can be fetched using the provided Python script: `../scripts/get_osm_gyms.py`
- **Export format:** CSV (example: `gyms_osm_berlin_YYYY-MM-DD.csv`)
- **Update frequency:** Manual or scheduled (recommended: monthly)
- **Data type:** Dynamic (ongoing via API/script)

## How to update OSM gym data

1. Run the script to fetch the latest data:
    ```bash
    cd gyms/scripts
    python3 get_osm_gyms.py
    ```
2. The resulting CSV will be saved in `gyms/sources/` with the current date.

## Planned Transformation Steps

- Map relevant OSM fields to the database schema for gyms.
- Normalize and clean data (e.g. standardize missing values, unify address formats).
- Link gym entries to `districts` or `neighborhoods` tables using location data.
- Document any data issues or inconsistencies.
- Prepare data for import into the database.

*For details on the transformation and schema mapping, see upcoming scripts and documentation in the `/scripts` directory.*
