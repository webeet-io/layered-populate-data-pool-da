# Step 1 — Research & Data Modelling

**Task:** Identify and document relevant data sources, select the 23 key parameters, draft a table schema, and save raw data in `/sources`.

---

## A. Data Source Discovery
- **Main source:** OpenStreetMap (OSM) via the OSMnx Python library.
- **Reason:** Open, free, and continuously updated. Contains location, address, and other details for all banks in Berlin.
- **Data type:** Dynamic (queried via API using `amenity=bank` filter).
- **Update frequency:** Continuous.
- **Extra sources:** Berlin Open Data Portal (optional enrichment).

---

## B. Selected Columns (23 total)
1. osm_id  
2. name  
3. brand  
4. operator  
5. street  
6. housenumber  
7. postcode  
8. city  
9. country  
10. phone  
11. email  
12. website  
13. opening_hours  
14. atm  
15. wheelchair  
16. building  
17. latitude  
18. longitude  
19. geom_type  
20. geom  
21. neighbourhood  
22. district  
23. source  

---

## C. Planned Schema
- Table name: `banks_in_berlin`
- Data types chosen to match expected content (text, float, geometry).
- `latitude` and `longitude` extracted from geometry.
- `neighbourhood` and `district` will be added later via spatial join.

---

## D. Transformation Plan
1. Fetch data from OSM (`amenity=bank`, Berlin).
2. Convert column names to snake_case.
3. Normalize address and contact formats.
4. Enrich with neighbourhood/district information.
5. Save cleaned dataset (GeoJSON + CSV).

---

## E. Files in `/sources` after Step 1
- **banks_raw.geojson** — raw data with geometry.
- **banks_raw.csv** — raw data without geometry.
- **README.md** — this file.
