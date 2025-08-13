# 🗃️ Playgrounds Schema

## 🏞️ Tables

### `playgrounds` (Complete Schema)
| Column Name | Data Type | Description |
|------------|-----------|-------------|
| technical_id | character varying | Technical identifier |
| key | character varying | Unique key |
| object_number | character varying | Object identifier |
| district | character varying | District name |
| neighborhood | character varying | Neighborhood name |
| green_area_type | character varying | Type of green space |
| playground_name | character varying | Playground name |
| playground_suffix | character varying | Name suffix |
| year_built | double precision | Construction year |
| last_renovation_year | double precision | Last renovation |
| area_sqm | double precision | Area in square meters |
| dedication | character varying | Dedication type |
| planning_area_number | double precision | Planning zone number |
| planning_area_name | character varying | Planning zone name |
| net_play_area_sqm | double precision | Usable play area |
| full_address | character varying | Complete address |
| latitude | numeric | Geographic coordinate |
| longitude | numeric | Geographic coordinate |

### 🛝 `test_berlin_data.playgrounds`
| Column | Type | Description |
|--------|------|-------------|
| playground_id | PK | Unique playground identifier |
| equipment_count | integer | Number of play equipment items |

## Data Quality Notes
- Updated annually from city records
- Coordinates accurate to 6 decimal places
- Includes all public playgrounds
- Area measurements in whole square meters