🏠 Long-Term Listings in Berlin (Immowelt) – Data Integration

This repository documents the process of integrating Long-Term Listings in Berlin from Immowelt into the database. The project involved scraping, cleaning, and enriching rental listings with geolocation data for analysis.

📊 Project Overview

Data Source: Immowelt (Berlin long-term rental listings)
Collection Method: Web scraping (no API available)
Total Listings Collected: 1246
Listings Dropped: 79 (outside Berlin, from Brandenburg)
Final Listings Inserted: 1167
Unique Neighborhoods Identified: 89

Challenges:

Immowelt applies privacy & scraping limits (only partial listings extractable per request).
Raw data had missing/abbreviated addresses and inconsistent formats.

🧪 Step 1: Research & Data Modelling

1.1 Data Source Discovery
Source: Immowelt website (scraped HTML pages)
Update Frequency: Static snapshot (one-time scrape)
Data Type: Static listings dataset
Additional Enrichment: Used Nominatim (OpenStreetMap) for geolocation to retrieve coordinates based on addresses.

1.2 Modelling & Planning
Selected key parameters:
Street & house number
Type
Postal code
District (Bezirk)
City
Price
Size (m²)
Number of rooms
Coordinates (lat, lon from Nominatim)

Known Issues:
Some addresses incomplete or abbreviated (e.g., "Str." vs. "Straße").
Duplicated entries possible due to multiple appearances of similar ads.
Not all addresses resolved by Nominatim.

1.3 Sources Directory
Raw scraped files stored in /sources.
/sources/README.md contains documentation of scraping steps and transformation plan.

🛠 Step 2: Data Transformation
Implemented transformation logic using Python:

House Type Normalization

Different types of Häuser (e.g., Reihenhaus, Einfamilienhaus, Doppelhaus) were standardized to house.
Different types of Wohnungen (e.g., Dachgeschosswohnung, Erdgeschosswohnung, Loft) were standardized to wohnung.

Address Cleaning

Normalized abbreviations: "Str." → "Straße".
Separated street names (letters) and house numbers (numeric part).

Floor Normalization

"Erdgeschoss" was standardized to 0.
Other floors converted to numeric values: 1, 2, 3, 4....

Other Cleaning & Processing

Extracted postal codes and districts.
Queried Nominatim for missing coordinates.
Dropped listings outside Berlin (79 listings from Brandenburg).
Added district_id for each listing to reference the district table.
Performed further cleaning in spreadsheets for consistency and quality.
Scripts are located in /scripts.
Outputs tested locally before database population.

🧩 Step 3: Populate Database

Transformed data inserted into the database using SSM tunnel to securely connect to the remote database.
The table was created with foreign key constraints to link listings to the districts reference table.
Established relationships with existing neighborhoods and geospatial tables.
Verified correctness of inserted data and linkage with neighborhood boundaries.

🗄️ Database Schema
<details> 
<summary>Click to expand SQL schema</summary>

CREATE TABLE IF NOT EXISTS long_term_listings (
    listing_id VARCHAR PRIMARY KEY,        -- Unique identifier for each listing
    detail_url TEXT,                       -- Direct URL to the listing
    raw_info TEXT,                         -- Raw extracted text description
    type VARCHAR,                          -- Housing type (e.g., Wohnung, Haus)
    first_tenant VARCHAR,                  -- Boolean flag for first tenant availability
    price_euro INTEGER,                    -- Price in euros
    number_of_rooms FLOAT,                 -- Number of rooms
    surface_m2 FLOAT,                      -- Size in square meters
    floor FLOAT,                           -- Floor number (Erdgeschoss = 0)
    street VARCHAR,                        -- Normalized street name
    house_number VARCHAR,                  -- House number extracted from address
    neighborhood VARCHAR,                  -- Neighborhood name
    district VARCHAR,                       -- Berlin district (Bezirk)
    postal_code INTEGER,                   -- Postal code
    city VARCHAR,                           -- City (Berlin)
    address TEXT,                           -- Full cleaned address
    latitude FLOAT,                         -- Latitude (Nominatim)
    longitude FLOAT,                        -- Longitude (Nominatim)
    geometry TEXT,                          -- Geospatial polygon coordinates
    district_id TEXT,                        -- Foreign key referencing districts table
    CONSTRAINT district_id_fk 
        FOREIGN KEY (district_id)
        REFERENCES berlin_source_data.districts(district_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

</details>


🌍 Geolocation with Nominatim

Geocoding was performed using Nominatim (OpenStreetMap).
Each cleaned address was passed to Nominatim for latitude/longitude retrieval.

Limitations: Some incomplete addresses could not be geocoded.

📐 Data Schema – Before & After Transformation
Raw Data (Scraped)
| Column Name  | Example Value          | Issue                  |
| ------------ | ---------------------- | ---------------------- |
| `address`    | "Pohleseestr. , 12587" | Abbreviations ("Str.") |
| `price_info` | "1.200 €"              | Includes symbols       |
| `size`       | "75 m²"                | Text + unit            |
| `rooms`      | "3 Zimmer"             | Contains text + number |


### 📐 Transformed Data (Final Schema)
| Column Name       | Example Value                                                 | Notes                                  |
| ----------------- | ------------------------------------------------------------- | -------------------------------------- |
| `listing_id`      | IMM123456                                                     | Unique identifier (primary key)        |
| `detail_url`      | [https://www.immowelt.de/ex/](https://www.immowelt.de/ex/)... | Direct listing URL                     |
| `raw_info`        | Schöne Wohnung in Köpenick                                    | Raw extracted text                     |
| `type`            | Wohnung                                                       | Normalized housing type (Wohnung/Haus) |
| `first_tenant`    | TRUE                                                          | Boolean flag                           |
| `price_euro`      | 1200                                                          | Converted to numeric                   |
| `number_of_rooms` | 3                                                             | Converted to numeric                   |
| `surface_m2`      | 75                                                            | Extracted number only                  |
| `floor`           | 2                                                             | Erdgeschoss → 0, upper floors → 1..n   |
| `street`          | Pohleseestraße                                                | Normalized full street name            |
| `street_alt`      | Pohleseestr.                                                  | Original scraped street value          |
| `house_number`    | 12                                                            | Extracted from address                 |
| `address`         | Pohleseestraße 12 12587 Berlin                                | Cleaned & standardized full address    |
| `postal_code`     | 12587                                                         | Extracted with regex                   |
| `neighborhood`    | Köpenick                                                      | Normalized neighborhood                |
| `district`        | Treptow-Köpenick                                              | Mapped from postal code                |
| `city`            | Berlin                                                        | Standardized                           |
| `latitude`        | 52.4471                                                       | From Nominatim geocoding               |
| `longitude`       | 13.5742                                                       | From Nominatim geocoding               |
| `geometry`        | POLYGON(...)                                                  | Geospatial polygon                     |
| `district_id`     | D\_KEP01                                                      | FK referencing `districts` table       |


🔄 Workflow Diagram

    A[Scraping Immowelt Listings] --> B[Raw Data Cleaning]
    B --> C[Address Normalization]
    C --> D[Geocoding with Nominatim]
    D --> E[Data Transformation & Filtering]
    E --> F[Database Population via SSM Tunnel]
    
🛠️ Libraries Used

Scraping: requests, BeautifulSoup, pandas, re

Geocoding: geopy (Nominatim)

Database Transfer: sqlalchemy, psycopg2 via SSM tunnel

✅ Final Notes
Total Listings Collected: 1246

Dropped (Brandenburg): 79

Final Inserted in DB: 1167

Unique Neighborhoods: 89

Status: Successfully integrated into the database

Limitations: Due to Immowelt’s scraping restrictions, future updates may require additional handling or throttling.


📊 Sample SQL Queries


1. Average Rent per District

SELECT 

    district, 
    
    AVG(price_euro) AS avg_rent
    
FROM 

    long_term_listings
    
GROUP BY 

    district
    
ORDER BY 

    avg_rent DESC;


  
2. Top 5 Most Expensive Neighborhoods
 
SELECT 

    neighborhood, 
    
    AVG(price_euro) AS avg_rent
    
FROM 

    long_term_listings
    
GROUP BY 

    neighborhood
    
ORDER BY 

    avg_rent DESC
    
LIMIT 5;



3. Distribution of Apartment Sizes
   
SELECT 

    CASE 
    
        WHEN surface_m2 < 40 THEN 'Small (<40 m²)'
        
        WHEN surface_m2 BETWEEN 40 AND 80 THEN 'Medium (40–80 m²)'
        
        WHEN surface_m2 BETWEEN 80 AND 120 THEN 'Large (80–120 m²)'
        
        ELSE 'Extra Large (>120 m²)'
        
    END AS size_category,
    
    COUNT(*) AS count_listings
    
FROM 

    long_term_listings
    
GROUP BY 

    size_category
    
ORDER BY 

    count_listings DESC;






