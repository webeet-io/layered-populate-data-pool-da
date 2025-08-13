# 🗃️ U-Bahn Statistics Schema

## 🚇 Tables

### `ubahn` (Complete Schema)
| Column Name | Data Type | Description |
|------------|-----------|-------------|
| station | character varying | Station name |
| line | character varying | U-Bahn line |
| latitude | numeric | Geographic coordinate |
| longitude | numeric | Geographic coordinate |
| postcode | character varying | Postal code |
| neighborhood | character varying | Neighborhood name |
| district | character varying | District name |

### 🚉 `test_berlin_data.stations`
| Column | Type | Description |
|--------|------|-------------|
| station_id | PK | Unique station identifier |
| line | string | U-Bahn line number |

## Data Relationships
- Stations → Neighborhoods: Spatial proximity mapping
- Uses 500m radius for neighborhood assignment

## Data Quality Notes
- Station coordinates accurate to 5 decimal places
- Updated with new station openings
- Includes all U-Bahn lines (U1-U9)