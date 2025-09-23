### 🧪 Step 1: Research & Data Modelling  
PR Branch Name: clubs-data-modelling  

This notebook documents the process for Step 1 of the "Clubs & Social Activities in Berlin" project:  

- **1.1 Data Source Discovery**  
- **1.2 Modelling & Planning**  
- **1.3 Prepare the /sources Directory**  
- **1.4 Review**  

---

### 🎯 Goal  
- Identify and document relevant data sources.  
- Select the key parameters for our use case.  
- Draft the planned table schema.  
- Plan cleaning and transformation steps before database population.  

---

## 1.1 Data Source Discovery  

**Topic:** Clubs & Social Activities in Berlin  

**Main source:**  
- **Name:** OpenStreetMap (OSM) via OSMnx / Overpass API  
- **Source and origin:** Public crowdsourced geospatial database  
- **Update frequency:** Continuous (dynamic)  
- **Data type:** Dynamic (API query using tags such as `club=*`, `leisure=*`, `sport=*`, `community_centre=*`)  
- **Reason for selection:**  
  - Covers a wide variety of sports clubs, cultural clubs, and social activity centers in Berlin  
  - Includes geospatial data (coordinates, polygons), names, addresses, and attributes  
  - Open, free, and queryable programmatically  

**Optional additional sources:**  
- **Name:** Berliner Turn- und Freizeitsport-Bund (BTFB)  (https://btfb.de/vereinsservice/vereinssuche/#Vereine-im-Portrait)
  - Source: Official Berlin sports association website  
  - Type: Static (manual export / scraping)  
  - Use: Provides official structured list of sports clubs in Berlin  

- **Name:** Berlin Open Data Portal (daten.berlin.de)  
  - Source: Berlin city government  
  - Type: Static or semi-static (CSV, GeoJSON)  
  - Use: Enrichment with official district boundaries or metadata  

  **Enrichment potential:**  
- Use Berlin shapefiles (districts, neighborhoods) for spatial joins.  


---

## 1.2 Modelling & Planning  

**Key Parameters (planned):**  
- Identification: `name`, `club`, `category`, `subcategory`  
- Location: `address`, `district`, `geometry (lat/lon)`  
- Contact: `website`, `phone`, `email`  
- Attributes: `opening_hours`, `membership`, `fees`, `sport` / `leisure type`  
- Metadata: `source`, `last_updated`  

**Integration with existing tables:**  
- Join on `district_id` from the Berlin districts reference table.  


**Planned table schema:**  
```sql
CREATE TABLE berlin_clubs (
    club_id SERIAL PRIMARY KEY,
    name TEXT,
    category TEXT,
    subcategory TEXT,
    street TEXT,
    housenumber TEXT,
    postcode TEXT,
    district TEXT,
    city TEXT,
    country TEXT,
    district_id INT REFERENCES berlin_districts(district_id),
    latitude FLOAT,
    longitude FLOAT,
    website TEXT,
    phone TEXT,
    email TEXT,
    opening_hours TEXT,
    wheelchair TEXT
   
);
