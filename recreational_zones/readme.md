
# 1.1 📍 Data Source Discovery

## 🎯 Topic Focus: Recreational Zones in Berlin – Public Parks 🌳 and Playgrounds 🛝

---

## 🔍 Identified Data Sources

### 1. 🌳 **Public Parks (Grünanlagenbestand)**

- **📚 Source and Origin**:
  - [Berlin Open Data Portal – Urban Green Spaces Overview](https://www.berlin.de/sen/uvk/en/nature-and-green/urban-green-space/data-and-facts/public-parks/)
  - [🔗 Direct Dataset via FIS-Broker](https://fbinter.stadt-berlin.de/fb/index.jsp?loginkey=alphaDataStart&alphaDataId=s_gruenanlagenbestand@senstadt)

- **📅 Update Frequency**:
  - Typically **updated annually**, depending on municipal reporting.
  - 🗂️ Metadata includes versioning details.

- **💾 Data Type**:
  - **Static** dataset (e.g., SHP, CSV, GML)
  - 🔄 Manual refresh needed when new data is released.

- **🧾 Key Data Fields**:
  - 🆔 Park ID
  - 🏷️ Name
  - 🏞️ Type of green area
  - 🏘️ Neighborhood
  - 📏 Area in m²
  - 🗺️ Planning area
  - 📜 Designation status

- **📈 Potential Uses**:
  - Enhance neighborhood datasets with green access
  - Urban planning and zoning insights
  - Environmental equity and accessibility analysis

---

### 2. 🛝 **Playgrounds (Spielplatzbestand)**

- **📚 Source and Origin**:
  - [Berlin Open Data Portal – Playgrounds Overview](https://www.berlin.de/sen/uvk/en/nature-and-green/urban-green-space/data-and-facts/playgrounds/)
  - [🔗 Direct Dataset via FIS-Broker](https://fbinter.stadt-berlin.de/fb/index.jsp?loginkey=alphaDataStart&alphaDataId=s_spielplatzbestand@senstadt)

- **📅 Update Frequency**:
  - Usually **annually updated** based on local reports 🗓️

- **💾 Data Type**:
  - **Static** dataset (CSV or SHP)
  - 🔄 Needs manual download for the latest version

- **🧾 Key Data Fields**:
  - 🏷️ Playground name
  - 📍 Neighborhood & locality
  - 🧸 Type of playground
  - 🏗️ Year built / 🛠️ Last renovated
  - 📏 Area (total and net in m²)
  - 🗺️ Planning area identifiers

- **📈 Potential Uses**:
  - Family-friendly neighborhood insights 👨‍👩‍👧
  - Infrastructure and maintenance tracking 🔧
  - Urban development & social equity analysis

---

## 📊 Summary Table

| **📂 Category**       | **🔗 Source** | **📅 Frequency** | **💾 Type** | **📝 Notes** |
|------------------------|---------------|-------------------|--------------|----------------|
| 🌳 Public Parks         | [FIS-Broker](https://fbinter.stadt-berlin.de/fb/index.jsp?loginkey=alphaDataStart&alphaDataId=s_gruenanlagenbestand@senstadt) | Annually | Static | Park names, areas, location, type |
| 🛝 Playgrounds          | [FIS-Broker](https://fbinter.stadt-berlin.de/fb/index.jsp?loginkey=alphaDataStart&alphaDataId=s_spielplatzbestand@senstadt) | Annually | Static | Playground size, location, condition |

---

# 1.2 🧠 Modelling & Planning

## 🗂️ Use Case Focus
Enhance Berlin neighborhood and listing data with relevant features from **recreational zones**, specifically **public parks** and **playgrounds**, to support accessibility scoring, livability indexes, and spatial insights.

---

## ✅ Key Parameters from Raw Data

### 🌳 **Public Parks**

| Column (German)             | Proposed Name           | Description                                      |
|-----------------------------|-------------------------|--------------------------------------------------|
| Name                        | `park_name`             | Name of the green space                          |
| Art der Grünanlage          | `park_type`             | Type of green area (Volkspark, Landschaftspark)  |
| Bezirk                      | `neighborhood`          | Berlin district name                             |
| Ortsteil                    | `locality`              | Neighborhood/locality                            |
| Fläche in m²                | `area_sqm`              | Size of the park in square meters                |
| Planungsraum                | `planning_area`         | Urban planning division (for spatial hierarchy)  |
| Koordinaten (Lat/Lon)       | `latitude`, `longitude` | Geospatial location                           |

---

### 🛝 **Playgrounds**

| Column (German)                   | Proposed Name           | Description                                        |
|-----------------------------------|-------------------------|----------------------------------------------------|
| Name des Spielplatzes             | `playground_name`       | Name of the playground                             |
| Namenszusatz des Spielplatzes     | `playground_suffix`     | Extra naming detail or location note               |
| Art der Grünanlage                | `playground_type`       | Playground category or structure                   |
| Bezirk                            | `neighborhood`          | Berlin district name                               |
| Ortsteil                          | `locality`              | Neighborhood/locality                              |
| Baujahr                           | `year_built`            | Construction year                                  |
| letztes Sanierungsjahr            | `last_renovation_year`  | Last renovation date                               |
| Größe in m² (Kataster)            | `total_area_sqm`        | Total area of the site                             |
| Nettospielfläche in m²            | `net_play_area_sqm`     | Usable play surface area                           |
| Planungsraum                      | `planning_area`         | Spatial zoning for integration                     |
| Koordinaten (Lat/Lon)             | `latitude`, `longitude` | Geospatial location                                |

---

## 🔗 Integration with Existing Tables

- **Join keys / connectors**:
  - `latitude`, `longitude` → for spatial joins with neighborhood polygons or listing coordinates.
  - `district`, `locality` → for administrative joins with existing neighborhood datasets.
  - `planning_area` → optional additional spatial segmentation.

- **Spatial Join Strategy**:
  - Parks/playgrounds will be mapped to the nearest or containing **neighborhood polygon** using spatial lookup (e.g., via GeoPandas or PostGIS).

---

## ⚠️ Known Data Issues

- 🧱 **Missing values**:
  - Some playgrounds lack `last_renovation_year` or `net_play_area_sqm`.
- 🏷️ **Inconsistent naming**:
  - Duplicates or variations in names across districts (e.g., "Schulhof Spielplatz", "Spielplatz Schulhof").
- 📐 **Area accuracy**:
  - Some green space polygons may contain multiple park types—manual review may be needed.
- 🧭 **Coordinate discrepancies**:
  - Some entries may have missing or incorrect lat/lon values (to be validated spatially).

---

## 🔧 Data Transformation Plan

1. **Load and Inspect**:
   - Import data (CSV, SHP) into Pandas or GeoPandas.
   - Standardize encoding (UTF-8) and column headers.

2. **Clean & Normalize**:
   - Rename columns using snake_case.
   - Fill or drop nulls where applicable.
   - Standardize naming of park/playground types.

3. **Spatial Validation**:
   - Ensure all rows have valid latitude and longitude.
   - Run spatial joins with neighborhood shapefiles.

4. **Structure & Store**:
   - Tag each row with `zone_type`: `"park"` or `"playground"`.

5. **Export or Integrate**:
   - Save cleaned data as `.geojson` or upload to PostGIS/spatial DB.
   - Integrate into broader listing or neighborhood enrichment pipelines.

---

