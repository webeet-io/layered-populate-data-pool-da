## 🚏 Step 2: Data Transformation — Geographic Enrichment & Neighborhood Tagging  
**Branch**: `bus-data-transformation`  
**Goal**: Clean, enrich, and unify Berlin public bus data using geographic context — focusing on accurate coordinates and Berlin district information.

---

### 🗺️ 2.1 Geographic Enrichment of Bus Stops  
**Script**: `transform_bus_data.py`  
**Input**: `public_bus_data_cleaned.csv`  
**Output**: `transformed_bus_data.csv`

This script reverse-geocodes each bus stop’s latitude and longitude using the **Nominatim API (OpenStreetMap)** to extract high-level district information (Berlin **Bezirk**):

- Loaded and cleaned the raw Berlin bus dataset.
- Queried Nominatim to retrieve administrative context for each stop.
- Extracted fields like `borough`, `county`, and `city_district`.
- Added this information into a new column: `neighborhood`.
- Respected API rate limits using `time.sleep(1)`.

> Run this step locally with:
```bash
python transform_bus_data.py


🔍 2.2 Subset for Testing and Validation
File: transformed_bus_data_subset.csv
Purpose: Handy for quick tests and manual inspection.

Includes a representative slice of the full dataset.

Used to verify that reverse geocoding worked as expected.

Allowed spot-checking neighborhood assignments and overall data cleanliness.

🚧 2.3 (Planned) Enrichment: Postcode & Stadtteil
These fields were not yet included, but are great next steps for even deeper enrichment:

Postcode: Add a column with each stop’s postal code via reverse geocoding.

Stadtteil: Enrich with smaller neighborhood identifiers like suburb or locality.

These will support more granular spatial analysis and mapping features later.
