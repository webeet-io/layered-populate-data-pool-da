# Sources for Bike Lanes Data Modelling

This document lists potential data sources for the bike lanes in Berline, as well as the initial steps for extracting and transforming the data. 

## 1.1 Data Source Discovery 
### Main Source - OpenStreetMap (OSM)

- **Origin**: OSM - Overpass Turbo (https://overpass-turbo.eu/)
- **Update Frequency**: Continuous/Dynamic based on community updates.
- **Data Type**:
   - Dynamic data types through API queries (ie. `cycleway=*`, `highway=cycleway`, `highway=path + bicycle=designated`, etc.).
   - There is the possibility of static files, however these have not been included for this specific project.
- **Reason for Selection**:
  - The data is dynamic and continuously maintained by a vast community which helps to ensure the near real-time information on the cycling infrastructure of Berlin.
  - Using the API system allows for more flexible filtering of the data by attributes and locations which makes it easier to tailor the data extraction process for the Berlin dataset.

### Optional Additional Source - Berlin Environmental Atlas

- **Origin**: Geoportal Berlin (https://gdi.berlin.de/viewer/main/#)
- **Update Frequency**: Not planned.
- **Data Type**: Static dataset that is downloadable in formats like GeoJSON.
- **Reason for possible usage**:
     - As this is an official/authoritative dataset collected and compiled by the city, ensuring the accuracy and the alignment with the Berlin transport authorities (ie. Radverkehrsnetz).
     - This data is available in GIS-friendly formats (ie. GeoJSON, WFS, etc.) making it a more reliable source for spatial analysis and integration into the data pipeline.   

