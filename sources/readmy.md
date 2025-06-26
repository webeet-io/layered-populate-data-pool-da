🧪 Step 1: Research & Data Modelling

🗂️ Data Source
	•	Title: Milieuschutzgebiete (Preservation Areas) – Berlin
	•	Provider: GDI Berlin (Geospatial Data Infrastructure)
	•	Service Type: WFS (Web Feature Service)
	•	Layer Name: erhaltungsverordnungsgebiete:erhaltgeb_es
	•	URL:
	•	WFS Service
	•	WFS Capabilities
	•	License: dl-zero-de/2.0
	•	Published: 17.06.2024
	•	Update Frequency: Unknown (assumed static)
	•	Data Type: Static — One-time import

⸻

🔑 Selected Fields

Column Name	Description
address_id	Unique ID of the address
house_number	Street number (primary)
house_number_extra	Optional house number suffix (e.g., “A”, “B”)
street_name	Name of the street
postal_code	Postal code
zone_code	Code of the preservation zone (from source data)
neighborhood	Berlin district name
zone_name	Name of the preservation area
publication_date	Official gazette publication date
effective_date	Date the regulation came into force
area_ha	Area size of preservation zone (in hectares)

🔍 Geometry column was excluded from the final CSV due to format limitations.
However, spatial analysis (e.g. intersection with house addresses) was performed in GeoPandas.

⸻

🧠 Modelling Decisions
	•	Performed spatial join using ST_Intersects logic to match addresses with preservation areas.
	•	Parsed all relevant date columns to ISO format (YYYY-MM-DD)
	•	Renamed all column headers from German to English for consistency.
	•	Converted numeric values (e.g. house numbers) to proper types.
	•	Removed irrelevant columns (e.g. housing unit counts, raw geometries).
	•	Validated and removed null values (except optional house_number_extra).

⸻

🧾 Output File

sources/houses_in_milieuschutz.csv

Format: CSV, UTF-8, delimiter: comma
Rows: ~38,000
Missing values: only in house_number_extra
