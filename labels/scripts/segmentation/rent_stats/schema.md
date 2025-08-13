# 🗃️ Rent Statistics Schema

## 🏠 Tables

### `rent_stats_per_neighborhood` (Complete Schema)
| Column Name | Data Type | Description |
|------------|-----------|-------------|
| neighborhood | character varying | Neighborhood name |
| median_net_rent_per_m2 | numeric | Median rent per m² |
| number_of_cases | integer | Sample size |
| mean_net_rent_per_m2 | numeric | Average rent per m² |
| year | smallint | Data year |

### `rent_stats_per_street` (Complete Schema)
| Column Name | Data Type | Description |
|------------|-----------|-------------|
| neighborhood | character varying | Neighborhood name |
| street_name | character varying | Street name |
| median_net_rent_per_m2 | numeric | Median rent per m² |
| number_of_cases | integer | Sample size |
| mean_net_rent_per_m2 | numeric | Average rent per m² |
| year | smallint | Data year |
| street_id | integer | Street identifier |

### `test_berlin_data.rental_stats`
| Column | Type | Description |
|--------|------|-------------|
| rental_id | PK | Unique rental record identifier |
| neighborhood_id | FK | Reference to neighborhoods |

## Data Relationships
- Neighborhood stats aggregate street-level data
- Uses 3-year moving averages for stability

## Data Quality Notes
- Updated annually from rental registry
- Excludes social housing units
- Minimum 10 cases per statistic
- Rents reflect net cold rents