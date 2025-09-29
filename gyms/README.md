# 🏋️ Berlin Gyms Data Pipeline

This folder contains all scripts and sources to extract, clean, enrich, and import Berlin gyms data for the [layered-populate-data-pool-da](../) project.

## Workflow Steps

1. **Extract gyms from OpenStreetMap using Overpass API**
2. **Transform and clean raw OSM data for database import**
3. **Spatial join: Assign each gym to a Berlin district**
4. **Import cleaned gyms with district info into the Postgres/PostGIS database**

See [scripts/README.md](./scripts/README.md) for details and running instructions.

---

## Directory Structure

- `scripts/` – All processing scripts, numbered by workflow order
- `sources/` – Input and output files (CSV, GeoJSON, etc.)
- `requirements.txt` – All Python dependencies for this workflow

---

## Quick Start

```bash
# Optional: Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r gyms/scripts/requirements.txt

# Run scripts in order (from project root)
python gyms/scripts/1_get_osm_gyms.py
python gyms/scripts/2_transform_osm_gyms.py
python gyms/scripts/3_spatial_join_gyms_to_districts.py
python gyms/scripts/4_import_gyms_to_postgres.py
