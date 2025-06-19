# Milieuschutzgebiete (Preservation Areas) – Berlin

## Source
- **Provider:** GDI Berlin (Geospatial Data Infrastructure)
- **Service Type:** WFS (Web Feature Service)
- **Layer Name:** `erhaltungsverordnungsgebiete:erhaltgeb_es`
- **URL:** https://gdi.berlin.de/services/wfs/erhaltungsverordnungsgebiete  , (https://gdi.berlin.de/services/wfs/erhaltungsverordnungsgebiete?REQUEST=GetCapabilities&SERVICE=wfs)
- **License:** dl-zero-de/2.0
- **Published:** 17.06.2024

## Update Frequency
- Unknown (assumed to be static — one-time import recomended)

## Data Type
- **Static** — not dynamically updated via API or automated schedule

## Fields Used
| Column         | Description                                          |
|----------------|------------------------------------------------------|
| `id`           | Unique identifier of the preservation zone           |
| `schluessel`   | Administrative code                                  |
| `bezirk`       | Berlin district name                                 |
| `gebietsname`  | Name of the preservation zone                        |
| `f_gybl_dat`   | Date of publication in the official gazette          |
| `f_in_kraft`   | Date the regulation came into force                  |
| `ae_gvbldat`   | (Optional) alternate publication date (often null)   |
| `fl_in_ha`     | Area size in hectares                                |
| `geometry`     | Multipolygon geometry in EPSG:25833 (meters)         |

## Coordinate Reference System (CRS)
- Current CRS: **EPSG:25833** — UTM Zone 33N (used in Germany) (EPSG:25833 — these are projected coordinates (in meters),
UTM zone 33N system, used in Germany for cadastral and precise measurements.)
- ⚠️ Note: CRS differs from common global standard (EPSG:4326 – lat/lon),  
  so it must be explicitly declared when importing to PostGIS or transformed if needed

## Transformation Plan
1. Parse date fields (`f_gybl_dat`, `f_in_kraft`, `ae_gvbldat`) to ISO date format
2. Validate and clean geometries
3. Reproject geometries to EPSG:4326 for compatibility (EPSG:4326 is latitude/longitude in degrees (geographic coordinates, used in Google Maps, OpenStreetMap, etc.)
4. Export data to `milieuschutzgebiete.geojson` inside `/sources`

## Intended Usage
- Spatial join with `neighborhoods` using `ST_Intersects`
- Analysis of which areas are under preservation protection
- PostgreSQL/PostGIS integration for geospatial querying
