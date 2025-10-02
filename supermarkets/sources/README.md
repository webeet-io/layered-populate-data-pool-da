# 🛒 Berlin Superstore Dataset – Data Profiling & Preparation**

This project involves extracting, exploring, and transforming supermarket data in Berlin using OpenStreetMap (OSM) via the osmnx library. The processed dataset can be used for location-based services, business mapping, or urban retail studies.

⸻

## 📌 1. Data Source Discovery

	•	Source: OpenStreetMap (OSM)
	•	Accessed via: osmnx Python package
	•	Query Tags: {"shop": "supermarket"}
	•	Place Queried: "Berlin, Germany"


Topic: Supermarkets in Berlin

**Main source:**

- Name: OpenStreetMap (OSM) via OSMnx library
- Source and origin: Public crowdsourced geospatial database
- Update frequency: Continuous (dynamic)
- Data type: Dynamic (API query using shop=supermarket)

**Reason for selection:**

- Covers all supermarkets in Berlin
- Includes coordinates, names, addresses, and other useful attributes
- Open, free, and easy to query programmatically

**Optional additional sources:**

- Name: Berlin Open Data Portal (daten.berlin.de)
- Source and origin: Official Berlin city government
- Update frequency: Varies per dataset
- Data type: Static or semi-static (download as CSV/GeoJSON)
- Possible usage: Enrich with official administrative boundaries or extra metadata

**Enrichment potential:**

Neighborhood/district info from Berlin shapefiles (GeoJSON)
Linking to local amenities for spatial context

⸻

## 🔄 2. Planned Transformation & Profiling Steps

**✅ Step-by-Step Process**

	1.	🗺️ Data Extraction

	•	Queried Berlin OSM boundaries using osmnx.features_from_place(...)
	•	Filtered features using shop=supermarket tag

	2.	🧹 Initial Cleaning & Column Selection

	•	Extracted relevant columns:
name, addr:street, addr:housenumber, addr:postcode, addr:city, opening_hours, brand, geometry, and various payment:* tags
	•	Extracted latitude and longitude from geometry
	•	Renamed columns for clarity (e.g., addr:street → street, brand → store_type, etc.)

	3.	📋 Dataset Profiling

	•	.shape – Number of rows and columns
	•	.info() – Data types and null counts
	•	Missing value analysis – Count + percentage of missing values per column
	•	Distinct values per column – For understanding cardinality
	•	Most common values – Using value_counts() for categorical profiling

	4.	📐 Spatial Sanity Checks

	•	Verified geometry types (Point vs MultiPoint)
	•	Confirmed latitude and longitude ranges fall within Berlin’s bounding box

	5.	💾 Data Export

	•	Raw dataset saved in sources folder as:
	•	CSV: supermarkets_raw.csv without geometry
	•	GeoJSON: supermarkets_raw.geojson with geometry (for mapping use)

⸻

## 🧰 Tools Used**

	•	Python
	•	osmnx, geopandas, pandas
	•	Jupyter Notebook (for analysis and exploration)

# 🏪 Berlin Superstores – Data Transformation & DB Insert

This project documents the transformation and integration process for a dataset of supermarkets (and similar stores) in Berlin. The data was sourced from **OpenStreetMap (OSM)** using the **Overpass API** and further enriched with geographic and administrative context before being inserted into a **Neon test database**.

---

## 🗂️ 1. Data Source

- ✅ **Source**: OpenStreetMap (via `osmnx` and Overpass API)
- ✅ **Tags used**: `shop=supermarket`, `convenience`, `grocery`, `department_store`, `general`
- ✅ **Format**: JSON → GeoDataFrame → Cleaned DataFrame

---

## 🔄 2. Data Transformation Steps

All transformation steps were handled in Python using `pandas` and `geopandas`.

### ✅ Cleaning & Normalization
- Cleaned column names (lowercase, snake_case, removed special characters)
- Standardized string fields (`name`, `brand`, `address`, etc.)
- Converted `NaN` to `None` where needed for DB compatibility

### ✅ Enrichment
- Extracted `latitude` and `longitude` from geometry
- Reverse geocoded missing address fields (`street`, `housenumber`, `postcode`, `city`)
- Joined **district** and **neighborhood** info using Berlin LOR GeoJSON boundaries
- Added new fields: `source`, `store_id`, `full_address`

### ✅ Data Validation
- Checked data types and missing values
- Ensured geometry points are valid and matched with admin boundaries
- Normalized contact fields (`phone`, `email`, `website`)
- Dropped irrelevant or overly sparse columns

---

## 🗃️ 3. Planned Database Schema (`superstore_in_berlin`)

| Column              | Type      | Description                                      |
|---------------------|-----------|-----------------------------------------------   |
| `store_id`          | string    | Unique ID from OSM (`node`, `way`, or `relation`)|
| `name`              | string    | Name of the store                                |
| `brand`             | string    | Store brand/type                                 |
| `street`            | string    | Street name                                      |
| `housenumber`       | string    | House number                                     |
| `postcode`          | string    | Postal code                                      |
| `city`              | string    | City (Berlin)                                    |
| `district_id`       | string    | FK → `districts(id)`                             |
| `neighborhood_id`   | string    | FK → `neighborhoods(id)`                         |
| `latitude`          | FLOAT     | Latitude                                         |
| `longitude`         | FLOAT     | Longitude                                        |
| `full_address`      | string    | Combined full address                            |
| `opening_hours`     | string    | Opening hours string                             |
| `phone`             | string    | Contact number                                   |
| `email`             | string    | Contact email                                    |
| `website`           | string    | Website                                          |
| `source`            | string    | Always `osm`                                     |

---

## 💾 4. Insert into Test Database (`test_berlin_data`)

- ✅ Used `SQLAlchemy` and `psycopg2` to connect to NeonDB
- ✅ Verified DB connection and tested inserts with sample records
- ✅ Ensured:
  - Primary key constraints (`store_id`)
  - Foreign key references (`district_id`, `neighborhood_id`)
  - Address + location fields are present
  - Row count matched cleaned dataset

---

## 🚧 Next Steps

- [ ] Run data validation queries in SQL (duplicates, nulls, invalid FKs)
- [ ] Insert into production schema after testing
- [ ] Create API endpoints to expose this data (optional)
- [ ] Add documentation for querying spatial data with PostGIS

---

## 📁 Folder structure:

├── sources/
│   ├── supermarkets_raw.csv
│   ├── supermarkets_raw.geojson
│   └── lor_ortsteile.geojson
    └── final_supermarkets_with_district.csv
├── scripts/
│   ├── supermarkets-data-transforming.ipynb
│   
├── README.md
└── requirements.txt