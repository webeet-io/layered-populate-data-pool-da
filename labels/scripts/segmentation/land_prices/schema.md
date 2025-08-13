# 🗃️ Land Prices Schema

## 💰 Tables

### `land_prices` (Complete Schema)
| Column Name | Data Type | Description |
|------------|-----------|-------------|
| neighborhood | character varying | Neighborhood name |
| standard_land_value_per_sqm | double precision | Price per square meter |
| typical_land_use_type | character varying | Primary land use |
| typical_floor_space_ratio | numeric | Building density ratio |
| land_use_category | character varying | Zoning category |
| year | integer | Valuation year |

### 🏡 `test_berlin_data.property_prices`
| Column | Type | Description |
|--------|------|-------------|
| price_id | PK | Unique price record identifier |
| price_per_sqm | decimal | Price per square meter |

## Data Relationships
- Prices → Neighborhoods: Direct mapping by name
- Uses most recent valuation year

## Data Quality Notes
- Values updated biennially
- Reflects standard land values (not market prices)
- Includes all land use categories
- Floor space ratio rounded to 0.1