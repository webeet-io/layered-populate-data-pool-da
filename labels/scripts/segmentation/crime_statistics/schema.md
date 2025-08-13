# 🗃️ Crime Statistics Schema

## 📊 Tables

### `crime_statistics` (Complete Schema)
| Column Name | Data Type | Description |
|------------|-----------|-------------|
| id | integer | Primary key |
| area_id | character varying | Area identifier |
| locality | character varying | Local area name |
| neighborhood | character varying | Neighborhood name |
| year | integer | Year of data |
| crime_type_german | character varying | Crime type (German) |
| crime_type_english | character varying | Crime type (English) |
| category | character varying | Crime category |
| total_number_cases | integer | Total cases reported |
| frequency_100k | numeric | Cases per 100k population |
| population_base | integer | Population base for rate calc |
| severity_weight | numeric | Severity weighting factor |
| created_at | timestamp without time zone | Record creation timestamp |
| updated_at | timestamp without time zone | Last update timestamp |

### 🏘️ `test_berlin_data.neighborhoods`
| Column | Type | Description |
|--------|------|-------------|
| neighborhood_id | PK | Unique area identifier |
| population | integer | Resident count |

### 🚨 `test_berlin_data.crimes`
| Column | Type | Description |
|--------|------|-------------|
| crime_id | PK | Unique incident ID |
| is_violent | boolean | Violent crime flag |
| is_property | boolean | Property crime flag |
| location | geometry | Geographic coordinates |
| date | timestamp | When crime occurred |

## 🔗 Relationships
- Crimes → Neighborhoods: Spatial join using `ST_Within()`
- Analysis uses 12-month crime window

## Data Quality Notes
- Crime data updated quarterly
- Population figures from annual census
- Severity weights range 1-5 (5=most severe)