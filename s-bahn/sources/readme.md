S-Bahn Berlin — Sources

Data Source

I used the GTFS dataset from the Verkehrsverbund Berlin-Brandenburg (VBB), available via the Berlin Open Data Portal.
It is updated twice per week (Wednesday, Friday), licensed under CC-BY, and contains public transport stops, routes, timetables, shapes, and transfers.

Additionally, I used the official Berlin district boundaries (Bezirksgrenzen) dataset, available via the Open Data Portal Berlin (ODIS).
The file is provided as GeoJSON, licensed under CC-BY, and contains polygon geometries with official district IDs (AGS/ARS codes).
This dataset was used to enrich each station with its corresponding Berlin district and district_id.

Transformation Steps

- Extract only S-Bahn stops from the GTFS dataset.  
- Join with routes and trips to identify served S-Bahn lines.  
- Remove duplicates and standardise station names.  
- Add placeholders for enrichment (postcode, neighbourhood, district).  
- Perform spatial join with Berlin district boundaries to assign `district` and `district_id`.  
- Save cleaned results to `/sources/sbahn_stations_transformed.csv`.  


Sources Directory

Files in `/sources`:

- `sbahn_stations.csv` → raw extracted S-Bahn stations  
- `sbahn_stations_clean.csv` → cleaned and pre-processed dataset  
- `bezirksgrenzen.geojson` → official Berlin district boundaries from ODIS (used for spatial join)  
- `sbahn_stations_transformed.csv` → final enriched dataset with district and district_id  
