#  Clubs & Social Activities in Berlin — Research, Modelling & Data Transformation and Test Loading into PostgreSQL

##  Goal
- Build a dataset of clubs and social activities in Berlin.
- Clean and filter data from OpenStreetMap.
- Perform a **load into PostgreSQL production database** (Layereddb).
- Document the table in **GitHub Wiki** and update the **ERD in Lucidchart**.

---

##  Process Overview

### 1. Library Imports & Configuration
- **Main libraries:** `pandas`, `geopandas`, `osmnx`, `sqlalchemy`, `psycopg2`, `shapely`.
- Configured PostgreSQL connection via **SQLAlchemy + psycopg2**.

---

### 2. Data Collection from OpenStreetMap (OSM)
- Queried **OpenStreetMap** with `osmnx.features_from_place("Berlin, Germany", tags={...})`.
- **Extracted features** using tags:
    - `club=*`
    - `leisure=*`
    - `sport=*`
    - `amenity=*`
- **Filtering Applied:**
    - **Excluded** categories: theaters, bars, cafes, pubs, restaurants, night_clubs.

---

### 3. Data Cleaning & Preparation
- **Selected and standardized attributes:**
    - `club_id`, `name`, `club`, `leisure`, `sport`, `amenity`,
    - `street`, `housenumber`, `postcode`,
    - `website`, `phone`, `email`, `opening_hours`,
    - `wheelchair`, `geometry`
- **Coordinate Calculation:** Calculated coordinates (`latitude`, `longitude`) from `geometry`.
- **Geospatial Join (Enrichment):** Joined with **districts and neighborhoods** (`lor_ortsteile.geojson`) to add:
    - `district`, `district_id`, `neighborhood`, `neighborhood_id`.

---

### 4. Address Enrichment & Validation
- **Missing Data:** Initial OSM data contained many `NULL` values in `street` and `housenumber`.
- **Enrichment Test:** **Nominatim reverse geocoding** was tested to build a `full_address` and fill missing values.
- **Data Validation:**
    - Checked **string lengths** per column to define correct SQL column sizes (VARCHAR length, TEXT fields, etc.).
    - Adjusted schema accordingly (e.g., longer fields for `website`, `full_address`, `opening_hours`).

---

### 5. Database Schema 
```sql
CREATE TABLE IF NOT EXISTS test_berlin_data.clubs (
    club_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200),
    club VARCHAR(100),
    leisure VARCHAR(100),
    sport VARCHAR(100),
    amenity VARCHAR(100),
    street VARCHAR(200),
    housenumber VARCHAR(50),
    postcode VARCHAR(20),
    website VARCHAR(250),
    phone VARCHAR(100),
    email VARCHAR(150),
    opening_hours TEXT,
    wheelchair VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    district VARCHAR(100),
    neighborhood_id VARCHAR(100),
    neighborhood VARCHAR(100),
    full_address TEXT,
    district_id VARCHAR(100),
    geometry TEXT, 	-- stored as Well-Known Text (WKT)
    CONSTRAINT district_id_fk FOREIGN KEY (district_id)
        REFERENCES test_berlin_data.districts(district_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
```

---
### **6. Loading into PostgreSQL**
- **Geometry Conversion:** `shapely Point` objects were converted into **WKT (Well-Known Text)** strings so they could be inserted into the `TEXT` column.
- **Loading:** The transformed `DataFrame` was loaded into PostgreSQL with the `.to_sql()` method.
- **Verification:** The data insertion into Layereddb was verified as correct.
-	Primary key uniqueness (club_id)
-	Foreign key integrity (district_id references districts.district_id)
-	Data types and nullability
-	Row counts match cleaned dataset
-	Standardization of contact info and website fields
---
### **7. Documentation & ERD Update**
-	**GitHub Wiki:** Added a structured description of social_clubs_activities table with all columns, data types, keys, and examples.
-	**Lucidchart ERD:** Updated project ERD:
-	Added social_clubs_activities table
-	Created relationship: social_clubs_activities.district_id → districts.district_id
-	
## **Current Status**
- Data successfully **extracted, filtered, and normalized**.
- Production load completed and verified.
- Table is fully documented in GitHub Wiki.
- ERD updated in Lucidchart to reflect new table and relationships.
