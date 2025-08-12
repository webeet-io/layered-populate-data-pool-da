# 🔌 Data Sources

| Source Name | Description        | Type | Update Frequency | Format | Origin |
|-------------|--------------------|------|------------------|--------|--------|
| VBB GTFS Feed | Official GTFS timetable for Berlin and Brandenburg. Includes geolocated stops, route geometries & scheduling, GTFS-RT vehicle_positions and trip_updates for live arrival predictions and delay data, alerts for disruptions. | static | weekly update | GTFS (zip) | https://www.vbb.de/fahrinfo/ | 
| BVG API | Official developer resources and popular public wrappers. Includes instant departure boards, journey planning queries, line statuses, and sometimes vehicle positions and delay reasons. | dynamic | real time | API(JSON) | https://www.bvg.de/de |
| OpenStreetMap | Geospatial public transport nodes, lines, and POIs | dynamic | daily/hourly by services | GeoJSON/XML | https://geo2day.com/europe/germany/berlin.html?utm_source=chatgpt.com |
| Berlin Open Data | Government published data about bus and tram network | static | undefined | WFS / API | https://daten.berlin.de/datensaetze/bvg-ungestortes-opnv-netz-strassenbahn-und-busnetz-wfs-c8a3b45a |
| GTFS.de | aggregators/archives for GTFS feeds across operators | static | daily | GTFS | https://gtfs.de/de/feeds/ |

# 📚 Preliminary Schema

| Column | dtype | Description |
|--------|-------|-------------|
| Station ID | string | bvg internal id |
| Station Name | string | |
| District | string | Name of the district |
| Neighborhood | string | name of neighborhood |
| Lines | string | line that cross that station |
| lat | float | |
| lon | float | | 