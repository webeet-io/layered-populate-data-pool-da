# Sources for bikelanes Data Modelling

This document lists potential data sources for the bike lanes in Berline, as well as the initial steps for extracting and transforming the data. 

## 1.1 Data Source Discovery
### Main Source - OpenStreetMap (OSM)

- **Origin**: OSM - Overpass Turbo
- **Update Frequency**: Continuous/Dynamic based on community updates.
- **Data Type**:
   - Dynamic data types through API queries (ie. Overpass Turbo).
   - There is the possibility of static files, however these have not been included for this specific project.
- **Relevant Fields**:
  - `street name`
  - `cycleway type` (lane, track, shared, etc.)
  - `lane direction`(left or right)
  - `coordinates`/`geometry`
  - `length`
  - `last updated`

  
