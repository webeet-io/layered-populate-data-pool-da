**🛒 Berlin Superstore Dataset – Data Profiling & Preparation**

This project involves extracting, exploring, and transforming supermarket data in Berlin using OpenStreetMap (OSM) via the osmnx library. The processed dataset can be used for location-based services, business mapping, or urban retail studies.

⸻

**📌 1. Data Source Discovery**

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

**🔄 2. Planned Transformation & Profiling Steps**

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

**🧰 Tools Used**

	•	Python
	•	osmnx, geopandas, pandas
	•	Jupyter Notebook (for analysis and exploration)
