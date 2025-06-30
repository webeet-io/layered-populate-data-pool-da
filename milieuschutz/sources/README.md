# 🛡️ Milieuschutz Data Integration — Berlin House-Level Zones

This dataset contains **house-level points** for addresses located within Berlin’s official Milieuschutz zones. These zones are divided into two types:

- 🏘️ `EM`: Residential Protection Zones (`milieuschutz_residential_protection_em_houselevel_cleaned.csv`)
- 🏙️ `ES`: Urban Character Preservation Zones (`milieuschutz_urban_character_preservation_es_houselevel_cleaned.csv`)

The pipeline was built as part of the [Smarter Real Estate Discovery through Map Layers](https://...) project at Webeet.

---

## 📦 Files

| File Name | Description |
|-----------|-------------|
| `milieuschutz_residential_protection_em_houselevel_cleaned.csv` | Cleaned house-level addresses in Residential Protection Zones (EM) |
| `milieuschutz_urban_character_preservation_es_houselevel_cleaned.csv` | Cleaned house-level addresses in Urban Character Preservation Zones (ES) |
| `*.geojson` versions | Contain the same data with WGS84 geometry for GIS applications |

---

## 📐 Shared Schema

| Column Name         | Data Type | Description                                             |
|---------------------|-----------|---------------------------------------------------------|
| `addr:housenumber`  | `string`  | Street number of the house                              |
| `addr:street`       | `string`  | Street name of the house                                |
| `addr:postcode`     | `string`  | Postal code (PLZ)                                       |
| `building`          | `category`| Optional building classification (e.g. bungalow, shed)  |
| `milieuschutz_zone` | `category`| Name of the Milieuschutz protection zone                |
| `neighborhood`      | `category`| Berlin district (Bezirk) name                           |
| `milieuschutz_type` | `category`| Type of protection: EM or ES                            |
| `source`            | `category`| Static value `"OSM"` indicating data source             |
| `lon`               | `float64` | Longitude (WGS84, decimal degrees)                      |
| `lat`               | `float64` | Latitude (WGS84, decimal degrees)                       |
| `data_quality`      | `boolean` | `True` if both street and number are present; else `False` |

---

## 🔄 Data Transformation Overview

| Step | Action |
|------|--------|
| 1. | Parsed GeoJSON polygons for Milieuschutz zones (EM & ES) |
| 2. | Mined OSM house nodes (`addr:*` tags, lat/lon) |
| 3. | Performed spatial joins (houses within EM/ES polygons) |
| 4. | Added `neighborhood` via polygon join with Berlin Bezirke |
| 5. | Created `data_quality` flag for complete addresses |
| 6. | Normalized column types: `category`, `string`, `boolean` |
| 7. | Filtered invalid/missing data and verified bounding box |
| 8. | Exported `.csv` and `.geojson` cleaned tables |

---

## 📸 Example Output Map

_(Screenshot from folium map visualization with Milieuschutz zones and Berlin Bezirke overlay)_

> 🖼️ `docs/milieuschutz_map_preview.png`

![Milieuschutz Map](docs/milieuschutz_map_preview.png)

---

## 🧪 Example Code Snippet

```python
import geopandas as gpd

# Load the cleaned GeoJSON file
gdf = gpd.read_file("milieuschutz_residential_protection_em_houselevel_cleaned.geojson")

# Quick overview
print(gdf.head())
print(gdf.crs)

# Plot simple map (or export to QGIS)
gdf.plot()
```

---

## 🌍 GeoJSON Support

Both EM and ES datasets are also exported as `.geojson`:
- EPSG:4326 / WGS84 projection
- Usable in QGIS, Folium, Mapbox, etc.

---

## 📁 Export Location

All cleaned datasets (CSV + GeoJSON) are saved to:

`/Users/zeal.v/Help/layered-populate-data-pool-da/milieuschutz/sources/`

---

## 🧠 Notes for Students

- `data_quality` is a custom flag — not from OSM — and helps filter incomplete addresses.
- This data is useful for scoring and recommendation layers related to livability, regulation, and development restrictions.
- Always inspect categorical distributions and geographic bounding boxes when dealing with spatial datasets.

---

Last updated: June 2025  
Maintainer: Zarko Vukovic  
