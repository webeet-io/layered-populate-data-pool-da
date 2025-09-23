# Data Sources for Fitness Studios (Gyms) in Berlin

## 1. OpenStreetMap (OSM)
- **URL:** https://www.openstreetmap.org
- **API:** https://wiki.openstreetmap.org/wiki/OpenStreetMap_API
- **Update frequency:** Continuously updated (community-driven)
- **Data type:** API (e.g., Overpass API, GeoJSON/CSV export possible)
- **Relevant fields:** 
    - name
    - leisure (e.g., fitness_centre, sports_centre)
    - sport (e.g., fitness, yoga, gymnastics)
    - addr:street
    - addr:housenumber
    - addr:postcode
    - addr:city
    - opening_hours
    - phone
    - website
    - wheelchair
    - lat
    - lon
- **Example Overpass Turbo query:**  
  [Fitness studios in Berlin via Overpass Turbo](https://overpass-turbo.eu/s/1qbb)

## 2. Other potential sources (to review)
- [daten.berlin.de](https://daten.berlin.de/) – Berlin Open Data Portal
- Google Places API (limited, for comparison)
- Websites of sports clubs, associations, district offices
- Lists from major fitness chains (e.g., McFit, Urban Sports Club) – if available as open data

---

## Next steps (planned)
- Download and store an OSM export (GeoJSON/CSV)
- Evaluate and compare data sources
- Match available fields with the planned database table structure