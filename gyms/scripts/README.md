# Scripts for Gym Layer Data

## get_osm_gyms.py

- Fetches gym, fitness studio, and yoga location data for Berlin from OpenStreetMap (Overpass API).
- Exports data as a CSV file to `../sources/`.
- Can be run any time to update the gym dataset.
- See comments in the script for details on fields and logic.

## Planned next steps

- Add transformation scripts to process, clean and map the raw OSM data to the final database schema.
- Include tests to verify data quality before import.
