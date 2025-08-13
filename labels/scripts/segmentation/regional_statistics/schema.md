# 🗃️ Regional Statistics Schema

## 📊 Tables

### `regional_statistics` (Complete Schema)
| Column Name | Data Type | Description |
|------------|-----------|-------------|
| neighborhood | character varying | Neighborhood name |
| year | smallint | Year of data |
| inhabitants | integer | Resident count |
| total_area_ha | integer | Total area in hectares |
| share_forest_water_agriculture | numeric | Percentage of natural areas |
| forest_area_ha | integer | Forest area in hectares |
| water_area_ha | integer | Water area in hectares |
| agriculture_area_ha | integer | Agricultural area in hectares |
| population_density_per_ha | numeric | Residents per hectare |
| number_of_residences | integer | Housing unit count |
| living_space_per_resident_m2 | numeric | Average living space per person |

### 🏘️ `test_berlin_data.neighborhoods`
| Column | Type | Description |
|--------|------|-------------|
| neighborhood_id | PK | Unique area identifier |
| population | integer | Resident count |

## Data Quality Notes
- Data updated annually from census
- Area measurements accurate to 0.1 hectare
- Density calculations use mid-year population