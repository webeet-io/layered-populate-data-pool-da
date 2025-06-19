
# Berlin Public Transport Data Project 

## Data Source Discovery

This section outlines the discovery and documentation of datasets used to enrich the Berlin public transport project.

### Source 1: U-Bahn Stations Dataset
- **Name:** Berlin U-Bahn Stations  
- **Source & URL:** Extracted by Clifford Anderson from Wikidata via SPARQL query — [GitHub Gist](https://gist.github.com/CliffordAnderson/7fb7473af31f9343f8a55518545480a0)  
- **Type:** Open Data (SPARQL Query)  
- **Update Frequency:** Dynamic (real-time via Wikidata)  
- **Data Type:** Static (as used in this project snapshot)  
- **Key Fields:** station name, latitude, longitude  
- **Example Entry:** `U-Bahnhof Möckernbrücke, 52.4961, 13.3834`  
- **Notes:** Location data derived from coordinate properties on Wikidata. Precision and coverage may vary.

### Source 2: U-Bahn Connections Dataset
- **Name:** Berlin U-Bahn Line Connections  
- **Source & URL:** Extracted from Wikipedia by Clifford Anderson, shared via [GitHub Gist](https://gist.github.com/CliffordAnderson/7fb7473af31f9343f8a55518545480a0)  
- **Type:** Open Data / Scraper  
- **Update Frequency:** Static (manually exported from Wikipedia)  
- **Data Type:** Static  
- **Key Fields:** point1, line, point2 (station names and lines they connect)  
- **Example Entry:** `U-Bahnhof Hallesches Tor, U1, U-Bahnhof Möckernbrücke`  
- **Notes:** Cleaned version (`08-connections-no-dupes.csv`) includes deduplicated records.

---

##  Modelling & Planning

### Selected Columns from Raw Data

**From `03-stations.csv`:**
- `station`: Station name (original)  
- `lat`: Latitude  
- `lng`: Longitude  

**From `08-connections-no-dupes.csv`:**
- `point1`: Starting station  
- `line`: U-Bahn line  
- `point2`: Ending station  

### Data Linkage Plan
- **Link Key:** Cleaned station names (removing “U-Bahnhof” prefix and trimming spaces)  
- **Joining Logic:** Match `point1_clean` and `point2_clean` with cleaned `station` column from the stations dataset.

### Planned Table Schema (Merged)

| point1 | line | point2 | postcode_point1 | lat_point1 | lng_point1 | postcode_point2 | lat_point2 | lng_point2 |
|--------|------|--------|------------------|-------------|-------------|------------------|-------------|-------------|

### Known Data Issues
- Inconsistent station naming (e.g. extra spaces, “U-Bahnhof” prefixes)  
- Missing coordinates or postcodes for some stations  
- Some stations in connections not present in stations list  
- Postcode field may include trailing `.0` if not properly typed  

### Transformation Plan

1. **Cleaning**  
   - Remove “U-Bahnhof” prefix and strip whitespace from all station names  
   - Convert postcode to nullable integer type  

2. **Normalization**  
   - Ensure coordinates are properly typed as float  
   - Rename and align columns for merging  

3. **Join Process**  
   - Merge `point1_clean` with station data to get `lat`, `lng`, `postcode` for point1  
   - Merge `point2_clean` similarly for point2  


---


### Files Added to `/sources` Folder
- `03-stations.csv` – Raw dataset containing Berlin U-Bahn stations and their lat/lng  
- `08-connections-no-dupes.csv` – Cleaned connections data between U-Bahn stations  
