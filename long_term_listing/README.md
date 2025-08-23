
## 🏠 Long-Term Listings in Berlin (Immowelt) — Data Integration

This repository documents the full process of integrating long-term rental listings in **Berlin** from Immowelt into a PostgreSQL database. The project covers scraping, cleaning, transformation, and enrichment with geolocation data for downstream analysis.

***

### 📊 Project Overview

- **Data Source:** Immowelt (Berlin long-term rental listings)
- **Collection Method:** Web scraping (no public API)
- **Listings Collected:** 1,246
- **Listings Excluded:** 79 (outside Berlin — Brandenburg region)
- **Final Listings Inserted:** 1,167
- **Unique Neighborhoods Identified:** 89

**Key Challenges:**
- Immowelt enforces anti-scraping limits; only partial listings extractable per request
- Raw data often included missing, abbreviated, or inconsistent address info

***

### 📦 Repository Structure

```
sources/
 ├─ scripts/                           # Python notebooks for processing
 │   ├─ DB_script_AWS.ipynb
 │   ├─ immowelt_cleaning_script.ipynb
 │   ├─ immowelt_geocoding_script.ipynb
 │   └─ immowelt_scraping_script.ipynb
 └─ README.md                          
```
***

### 🧪 Step 1: Research & Data Modeling

#### 1.1 Data Source Discovery
- **Source:** Immowelt website (HTML scraped)
- **Update Frequency:** One-time static data snapshot
- **Data Type:** Rental property listings
- **Additional Enrichment:** Geolocated via Nominatim (OpenStreetMap)

#### 1.2 Data Modeling
Selected features:
- Street & house number
- Property type
- Postal code, district, city
- Price, size (m²), rooms
- Coordinates (lat/lon via Nominatim)

**Known Issues:**
- Some addresses missing or abbreviated (`"Str."` → `"Straße"`)
- Not all addresses resolvable by Nominatim


***

### 🛠 Step 2: Data Transformation

Main cleaning and transformation steps (Python):

- **House Type Normalization**:  
  - Common house types (e.g. "Einfamilienhaus", "Doppelhaus", "Reihenhaus") → "Haus"
  - Apartments (e.g. "Dachgeschosswohnung", "Loft", "Penthouse") → "Wohnung"

- **Address Normalization**:  
  - `"Str."` replaced with `"Straße"`
  - Street names and house numbers split into distinct fields

- **Floor Standardization**:  
  - `"Erdgeschoss"` set as `0`, upper floors as integers

- **Additional Processing**:  
  - Extracted postal codes, districts, neighborhoods
  - Queried Nominatim for coordinates (lat/lon)
  - Dropped non-Berlin listings (Brandenburg)
  - Added `district_id` as a foreign key
  - Manual spreadsheet fixes for some inconsistencies

All outputs tested locally before DB loading.

***

### 🧩 Step 3: Populate Database

- Loaded cleaned and enriched data into PostgreSQL via SSM tunnel
- Table created with strong foreign key references
- Linked to `districts` (and neighborhoods, geospatial tables)
- Data and relationships verified against Berlin boundaries


***

### 📝 Example Listing: Raw Info vs. Parsed Columns

**Raw Input (`raw_info`):**
> Wohnung zur Miete - Erstbezug 1.840 € 2 Zimmer 76,6 m² Dachgeschoss, 6. Geschoss Nehringstraße 13 Charlottenburg Berlin 14059

***

**Parsed Columns after Cleaning:**

| Column Name         | Extracted Value                  |
|---------------------|----------------------------------|
| type                | Wohnung                          |
| first_tenant        | yes                              |
| price_euro          | 1840                             |
| number_of_rooms     | 2                                |
| surface_m2          | 76.6                             |
| floor               | 6                                |
| street              | Nehringstraße                    |
| house_number        | 13                               |
| neighborhood        | Charlottenburg                   |
| district            | Charlottenburg-Wilmersdorf       |
| postal_code         | 14059                            |
| city                | Berlin                           |
| address             | Nehringstraße 13 14059 Charlottenburg Berlin |
| latitude            | 52.5139304                       |
| longitude           | 13.2941382                       |
| geometry            | POINT (13.2941382 52.5139304)    |
| district_id         | 11004004                         |
| listing_id          | WOH_1840_76_14059                |

***


## 🗄️ Database Schema

```sql
CREATE TABLE IF NOT EXISTS {schema}.long_term_listings (
    listing_id VARCHAR PRIMARY KEY,        -- Unique identifier
    detail_url TEXT,                       -- Listing URL
    raw_info TEXT,                         -- Raw description from site
    type VARCHAR,                          -- Wohnung/Haus/Studio
    first_tenant VARCHAR,                  -- First tenant flag
    price_euro INTEGER,                    -- Output price
    number_of_rooms FLOAT,                 -- Room count
    surface_m2 FLOAT,                      -- Surface area (sqm)
    floor FLOAT,                           -- Floor number
    street VARCHAR,                        -- Cleaned street
    house_number VARCHAR,                  -- House number
    neighborhood VARCHAR,                  -- Neighborhood name
    district VARCHAR,                      -- Berlin district
    postal_code INTEGER,                   -- Postal code
    city VARCHAR,                          -- City
    address TEXT,                          -- Cleaned full address
    latitude FLOAT,                        -- Latitude (Nominatim)
    longitude FLOAT,                       -- Longitude (Nominatim)
    geometry TEXT,                         -- Geospatial polygon or point
    district_id TEXT,                      -- FK → districts.district_id
    CONSTRAINT district_id_fk
        FOREIGN KEY (district_id)
        REFERENCES berlin_source_data.districts(district_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
```

***

## 🔄 Workflow Diagram

```
  A[Scrape Immowelt listings] --> B[Raw Data Cleaning]
  B --> C[Address Normalization]
  C --> D[Geocoding with Nominatim]
  D --> E[Data Transformation & Filtering]
  E --> F[Database Population]
```

***

## 🛠️ Libraries Used

- **Scraping:** `requests`, `BeautifulSoup`, `pandas`, `re`
- **Geocoding:** `geopy` (Nominatim)
- **Database:** `sqlalchemy`, `psycopg2` (via SSM tunnel/upload)

***

## ✅ Final Notes

- **Listings collected:** 1246
- **Listings dropped (Brandenburg):** 79
- **Inserted into DB:** 1167
- **Unique neighborhoods:** 89
- **Status:** Successfully loaded into database
- **Future work:** Immowelt’s scraping restrictions may require handling for future updates and throttling

***

## 📊 Example SQL Queries

### 1. Average Rent by District

```sql
SELECT district, AVG(price_euro) AS avg_rent
FROM long_term_listings
GROUP BY district
ORDER BY avg_rent DESC;
```

### 2. Top 5 Most Expensive Neighborhoods

```sql
SELECT neighborhood, AVG(price_euro) AS avg_rent
FROM long_term_listings
GROUP BY neighborhood
ORDER BY avg_rent DESC
LIMIT 5;
```

### 3. Apartment Size Distribution

```sql
SELECT
  CASE
    WHEN surface_m2 120 m²)'
  END AS size_category,
  COUNT(*) AS count_listings
FROM long_term_listings
GROUP BY size_category
ORDER BY count_listings DESC;
```

***
