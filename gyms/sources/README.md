# gyms/sources — Data Sources for Gyms Layer

## Contents
- `gyms_with_district.csv`: Final, cleaned gyms data — spatially joined with Berlin districts, ready for database import
- `berlin_districts.geojson`: Official district boundaries (for spatial join & reference)

## Data Source Overview

### 1. OpenStreetMap (OSM)
- **URL:** https://www.openstreetmap.org
- **Origin:** OSM Overpass API export (see scripts for details)
- **Update Frequency:** Dynamic (script-based, re-runnable)
- **Relevant fields:** name, address, latitude, longitude, opening_hours, phone, website, wheelchair, etc.

### 2. Berlin District Boundaries (GeoJSON)
- **Source:** Berlin Open Data Portal
- **Origin:** Official district (Bezirk) boundaries
- **Fields:** district name, district_id, geometry

## Transformation Plan (Completed)
- Fetch OSM gyms via Overpass API
- Clean and map fields to our project schema
- Spatial join with official districts (using GeoPandas)
- Export as `gyms_with_district.csv` for DB import

