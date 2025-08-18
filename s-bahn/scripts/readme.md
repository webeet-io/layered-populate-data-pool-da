S-Bahn Berlin Data Modelling

1.1 Data Source Discovery

Source: Verkehrsverbund Berlin-Brandenburg (VBB) GTFS dataset  
Origin: [Berlin Open Data Portal](https://daten.berlin.de/datensaetze/vbb-fahrplandaten-via-gtfs)  
License: Creative Commons Attribution (CC-BY)  
Update frequency: Twice per week (Wednesday, Friday)  
Data type: Dynamic (GTFS format, regularly updated)

The GTFS dataset includes:
- All public transport stops (S-Bahn, U-Bahn, buses, trams, ferries)
- Route definitions
- Timetables
- Shape files for routes
- Transfers and pathways

1.2 Modelling & Planning

Relevant columns for S-Bahn stations (from GTFS stops.txt and related files):
- `stop_id`
- `stop_name`
- `stop_lat`
- `stop_lon`
- `location_type`
- `parent_station`
- Route mapping from `routes.txt` and `trips.txt`

Planned table: `sbahn_stations`  
Fields:
- stop_id (PK)
- stop_name
- line[] (array of S-Bahn lines serving the station)
- latitude
- longitude
- postcode
- stadtteil
- fkdistrict (FK → `districts.pkdistrict`)

Connections to existing database:
- `fkdistrict` links to `districts` table via district ID
- Latitude/longitude match existing geospatial queries
- Postcode and neighborhood can connect to listings & neighborhoods datasets

Known data issues:
- Mixed data types in `trips.txt` and `stop_times.txt`
- Duplicate station names (different lines)
- Missing postcode for some stops
- Some stops may appear in multiple datasets (U-Bahn + S-Bahn)

Transformation plan:
1. Filter only S-Bahn stops from GTFS using route_id and agency information
2. Join with trips and routes to extract served lines
3. Remove duplicates, standardize names
4. Enrich with postcode, stadtteil, and fkdistrict
5. Save cleaned data to `/sources/sbahn_stations_clean.csv`

1.3 Sources Directory

Files in `/sources`:
- `sbahn_stations.csv` → raw extracted S-Bahn stations
- `sbahn_stations_clean.csv` → cleaned and enriched dataset
