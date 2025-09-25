
---

## **gyms/scripts/README.md**
# Gyms Data Scripts

This folder contains the main scripts to fetch, process, and import gym data for Berlin.

## Script Overview

| Script                                  | Purpose                                                                                 |
|-----------------------------------------|-----------------------------------------------------------------------------------------|
| **1_get_osm_gyms.py**                   | Download gyms in Berlin from OpenStreetMap (via Overpass API). Exports raw data to CSV. |
| **2_transform_osm_gyms.py**             | Clean and normalize raw OSM gym data for database import.                               |
| **3_spatial_join_gyms_to_districts.py** | Spatial join: assign each gym to its Berlin district using GeoJSON borders.             |
| **4_import_gyms_to_postgres.py**        | Import the enriched data into your Postgres/PostGIS database.                           |

> **Warning:**  
> The import script (`4_import_gyms_to_postgres.py`) will truncate (empty) the `gyms` table before importing.  
> All previous data in this table will be deleted on each run!

## How to Run

- **Always run from the project root directory for path consistency.**
- Edit your database credentials in `4_import_gyms_to_postgres.py` before running the last script.

```bash
python gyms/scripts/1_get_osm_gyms.py
python gyms/scripts/2_transform_osm_gyms.py
python gyms/scripts/3_spatial_join_gyms_to_districts.py
python gyms/scripts/4_import_gyms_to_postgres.py
