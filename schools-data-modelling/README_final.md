# 🏫 Berlin Schools Data Upload to NeonDB

This repository contains code and documentation to **transform, map, and upload Berlin school data** to a PostgreSQL NeonDB database.  
It also includes tools for **geospatial zone mapping, school zone spiral sorting**, and outlines lessons learned during the process — ideal for reviewers and future learners.

---

## 🧰 Tools Used

This project required of tools from the Python ecosystem:

### 📦 Core Libraries
- `pandas`: Data cleaning and transformation
- `sqlalchemy` + `psycopg2-binary`: Database connection and table upload
- `geopandas`: Handling geospatial dataframes
- `shapely`: Performing geometric operations (point-in-polygon, centroids, buffers)
- `numpy`: Efficient array and distance calculations
- `matplotlib`: Visualizing spiral maps and school zone numbers

### 🌀 Spiral Zone Sorting
- `shapely` + `numpy` were used together to compute:
  - Geometry centroids
  - Angles and distances for sorting Berlin's school induction zones (SIZ)
  - A custom spiral order first i tried starting from Kladow, moving clockwise inward, then did from  mitte  outwards it was easier.

### 🌍 Other Geospatial Experiments
- `fiona`: Attempted fallback when `shapely` geometry parsing failed
- `geopy`: Used for early geocoding and coordinate sanity checks
- `QGIS`: used for geoextraction , layers single to multi and exploding them aldo combining.


### 🌐 Web Scraping (Experimental)
- `beautifulsoup4 (bs4)`: Tried scraping private school websites for enrollment data, but most Berlin schools still use **analog systems** and rarely publish such information online

---

## 💻 Development Environments

This project was primarily developed in **Jupyter Notebook** for its clear step-by-step structure.  
However, **Visual Studio Code (VS Code)** was also used for debugging and script-based runs.

> 📝 **Observation:**  
> VS Code was faster for finding syntax errors and jumping between files,  
> but Jupyter’s cell-based workflow made transformation logic more transparent and modular.

---

## 📁 Project Structure

| File | Description |
|------|-------------|
| `transform_schools.ipynb` | Cleans and transforms the dataset (dtypes, nulls, renaming) |
| `upload_to_neondb.ipynb` | Creates the SQL table and uploads cleaned data |
| `spiral_zones.ipynb` | Calculates spiral order for Berlin SIZ zones |
| `README.md` | You are here — project overview and notes |
| `berlin_schools.csv` | Raw input data |

---

## 🔄 Summary of Steps

### 1. **Data Transformation**
- Converted text and numeric columns to proper types
- Renamed `siz` → `schoolinductionzones_id` for clarity
- Dropped unused `geometry` column

### 2. **SQL Table Creation**
- Created table `test_berlin_data.schools` in NeonDB with:
  - Proper `VARCHAR`, `INT`, `DOUBLE PRECISION` types
  - Primary key on `bsn` (school ID)

### 3. **Data Upload**
- Used `df.to_sql(... if_exists='append')` to populate the database

---

## 🗃️ Final Table Schema: `test_berlin_data.schools`

| Column | Type | Notes |
|--------|------|-------|
| `bsn` | `VARCHAR(16)` | Primary Key |
| `school_name` | `VARCHAR(128)` |  |
| `school_type_de` | `VARCHAR(64)` |  |
| `ownership_en` | `VARCHAR(32)` |  |
| `school_category_de` | `VARCHAR(64)` |  |
| `district` | `VARCHAR(64)` |  |
| `neighborhood` | `VARCHAR(64)` |  |
| `postal_code` | `INT` |  |
| `street` | `VARCHAR(64)` |  |
| `street_number` | `VARCHAR(16)` |  |
| `website` | `TEXT` | Nullable |
| `school_year` | `VARCHAR(16)` |  |
| `school_category_en` | `VARCHAR(64)` |  |
| `total_students` | `INT` | Nullable |
| `students_f` | `INT` | Nullable |
| `students_m` | `INT` | Nullable |
| `teachers_total` | `INT` | Nullable |
| `teachers_f` | `INT` | Nullable |
| `teachers_m` | `INT` | Nullable |
| `startchancen_flag` | `VARCHAR(16)` |  |
| `lon` | `DOUBLE PRECISION` |  |
| `lat` | `DOUBLE PRECISION` |  |
| `schoolinductionzones_id` | `INT` | Nullable |
| `district_id` | `INT` | 


---

## 📌 Notes & Reflections

- **Shapely 2.x** caused compatibility issues with NumPy arrays early on — fixed via careful casting
- **Visual Studio Code** was a great complement to Jupyter: cleaner error display, better autocomplete, and file navigation
- Tried scraping private school data — most sites lacked usable info, confirming Berlin schools still lean heavily on offline infrastructure


