## Data transformation Log

This document outlines the data enrichment process performed on the cleaned Deutsche Post locations dataset. The primary goal was to augment the location data with geographical context, specifically district and neighborhood information, including their respective unique IDs. The process was completed in two main parts.

---
### Part 1: Adding District and Neighborhood Names via Spatial Join

In the first stage, we used geospatial data to determine the district and neighborhood for each location based on its coordinates.

* **Data Loading:** The base dataset (`deutschepost_clean.csv`) containing latitude and longitude for each location was loaded. A GeoJSON file (`lor_ortsteile.geojson`) containing Berlin's neighborhood polygons (`Ortsteile`) was used as the geographical reference.
* **Geospatial Conversion:** The **GeoPandas** library was used to convert the primary DataFrame into a `GeoDataFrame` by creating `Point` geometries from the coordinate columns (`latitude`, `longitude`).
* **Spatial Join:** A **spatial join** (`gpd.sjoin` with the predicate `'within'`) was performed to map each point (post office) to its corresponding polygon (neighborhood).
* **Column Integration:** The district (`BEZIRK`) and neighborhood (`OTEIL`) names were extracted from the GeoJSON's attributes and added as new columns (`district`) and (`neighborhood`) to the main dataset.


---
### Part 2: Adding District and Neighborhood IDs via Table Merging

In the second stage, we used standard lookup tables to add unique IDs for the districts and neighborhoods identified in Part 1.

* **Loading Lookup Tables:** Two new CSV files, `districts.csv` and `neighborhoods.csv`, were loaded. These tables contained the mapping between names and their corresponding unique IDs.
* **Merging for District ID:** A **`pandas.merge`** operation (a left join) was executed to connect the main dataset with the `districts` table on the common `district` name column. This added the `district_id` to each row.
* **Merging for Neighborhood ID:** A second `pandas.merge` was performed to connect the resulting dataset with the `neighborhoods` table on the common `neighborhood` name column, which added the `neighborhood_id`.
* **Final Result:** The final DataFrame now contains the original location data, fully enriched with both the human-readable names and the unique IDs for each location's district and neighborhood and saved as `deutschepost_clean_with_distr.csv`.
