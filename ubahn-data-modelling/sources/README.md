# 🚇 Berlin U-Bahn Data Modeling – Simoun Asmar

## Step 1: Research & Data Modeling  
**Branch:** `ubahn-data-modelling`  
**Focus:** U-Bahn stations and connections in Berlin using cleaned Wikidata and Wikipedia data.

---

## 1.1 Data Source Discovery

### 📍 Source 1: Berlin U-Bahn Stations
- **Name:** Berlin U-Bahn Stations
- **Source & URL:** Extracted from Wikidata via SPARQL by Clifford Anderson — [GitHub Gist](https://gist.github.com/CliffordAnderson/7fb7473af31f9343f8a55518545480a0)
- **Type:** Open Data (SPARQL export)
- **Update Frequency:** Static snapshot (manual)
- **Data Type:** Static
- **Key Fields:** `station`, `lat`, `lng`
- **Example Entry:**  
  `station`: U-Bahnhof Alexanderplatz  
  `lat`: 52.5219  
  `lng`: 13.4132
- **Notes:** Data may contain inconsistent naming formats (e.g., prefixes like "U-Bahnhof")

---

### 🔗 Source 2: U-Bahn Line Connections
- **Name:** Berlin U-Bahn Line Connections
- **Source & URL:** Scraped from Wikipedia and shared via the same [GitHub Gist](https://gist.github.com/CliffordAnderson/7fb7473af31f9343f8a55518545480a0)
- **Type:** Open Data / Manual Scraper
- **Update Frequency:** Static (manual update)
- **Data Type:** Static
- **Key Fields:** `point1`, `line`, `point2`
- **Example Entry:**  
  `point1`: U-Bahnhof Alexanderplatz  
  `line`: U2  
  `point2`: U-Bahnhof Klosterstraße
- **Notes:** A cleaned version (`08-connections-no-dupes.csv`) includes deduplicated entries (removes directional duplicates).

---

## 1.2 Modeling & Planning

### 📌 Selected Columns

From `03-stations.csv`:
- `station`: U-Bahn station name
- `lat`: Latitude of the station
- `lng`: Longitude of the station

From `08-connections-no-dupes.csv`:
- `point1`: Starting station name
- `line`: U-Bahn line identifier
- `point2`: Ending station name

---

### 🧠 Planned Transformations

- **Normalize** and **clean station names** (remove `"U-Bahnhof"` and trim whitespace).
- **Join** geographic coordinates from `03-stations.csv` to both `point1` and `point2`.
- Use **reverse geocoding** to assign `postcode` to both endpoints based on their latitude and longitude.
- Use a **PLZ-to-neighborhood lookup** (or similar dataset) to assign a **neighborhood name** to each point based on postcode.
- **Deduplicate** any redundant or mirrored connections (`A → B` and `B → A`).
- **Export** final enriched connection data as `merged_ubahn_connections.csv`.

---

### 🔗 Data Linking Strategy

- **Join Key:** Cleaned station names, normalized by removing `"U-Bahnhof"` prefix and trimming whitespace.
- **Join Logic:**
  - Match `point1` and `point2` (after cleaning) with `station` in the coordinates dataset.
  - Join `lat` and `lng` values from `03-stations.csv` to each connection.
  - Apply **reverse geocoding** on `lat/lng` to retrieve `postcode`.
  - Map `postcode` to neighborhood using a lookup table.

---

### 🧱 Planned Schema for Merged Output

| point1             | line | point2               | lat_point1 | lng_point1 | lat_point2 | lng_point2 | postcode_point1 | postcode_point2 | neighborhood_point1 | neighborhood_point2 |
|--------------------|------|----------------------|-------------|-------------|-------------|-------------|------------------|------------------|-----------------------|-----------------------|
| U-Bahnhof Zoo      | U9   | U-Bahnhof Hansaplatz | 52.505      | 13.332      | 52.517      | 13.343      | 10787            | 10557            | Tiergarten            | Moabit                |

---
### ⚠️ Known Data Issues

- Inconsistent station names (e.g. “U-Bahnhof” prefix, spacing)
- Some stations in the connections dataset may not exist in the station list
- Possible missing latitude/longitude values
- Missing postal codes — will be filled using **reverse geocoding**

---

### 🔧 Transformation Plan

1. **Cleaning**  
   - Remove `"U-Bahnhof"` prefix and strip extra spaces from all station names
   - Normalize case (e.g., all lowercase or title case for join keys)

2. **Normalization**  
   - Ensure `lat` and `lng` fields are of numeric type
   - Create new columns: `point1_clean`, `point2_clean`, `station_clean`

3. **Reverse Geocoding**  
   - Use reverse geocoding to derive **postal codes** for `lat_point1` and `lat_point2`
   - These will be added as `postcode_point1` and `postcode_point2`

4. **Merging**  
   - Join `point1_clean` with cleaned station names → add `lat_point1`, `lng_point1`, `postcode_point1`
   - Join `point2_clean` with cleaned station names → add `lat_point2`, `lng_point2`, `postcode_point2`

5. **Deduplication**  
   - Ensure reverse connections aren’t duplicated (e.g., A→B and B→A only appears once)

6. **Export Plan**  
   - Final merged dataset will be saved as: `merged_ubahn_connections.csv`

---

## 1.3 `/sources` Directory Setup

### 📂 Files Currently Included

- `03-stations.csv` – Cleaned list of U-Bahn stations with coordinates
- `08-connections-no-dupes.csv` – Unique U-Bahn connections between stations

### 📝 /sources/README.md Overview


# 📦 Sources Directory

## Data Sources

### 1. Berlin U-Bahn Stations
- **File:** 03-stations.csv
- **Source:** Wikidata via SPARQL (Clifford Anderson)
- **Fields:** station, lat, lng

### 2. U-Bahn Connections
- **File:** 08-connections-no-dupes.csv
- **Source:** Wikipedia (Clifford Anderson)
- **Fields:** point1, line, point2

## Planned Transformations
- Normalize and clean station names
- Join coordinates from station dataset to both `point1` and `point2`
- Use reverse geocoding to assign postal codes to both ends of the connection
- Identify and remove deduplicate connections
- Export enriched dataset as `merged_ubahn_connections.csv`
