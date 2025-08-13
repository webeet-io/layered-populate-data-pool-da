# 🗃️ Short-Term Listings Schema

## 🏡 Tables

### `short_time_listings` (Complete Schema)
| Column Name | Data Type | Description |
|------------|-----------|-------------|
| id | bigint | Primary key |
| host_id | bigint | Host identifier |
| neighborhood | character varying | Neighborhood name |
| district | character varying | District name |
| latitude | numeric | Geographic coordinate |
| longitude | numeric | Geographic coordinate |
| property_type | character varying | Type of property |
| room_type | character varying | Type of room |
| accommodates | integer | Guest capacity |
| bedrooms | numeric | Number of bedrooms |
| beds | numeric | Number of beds |
| bathrooms | numeric | Number of bathrooms |
| is_shared | smallint | Shared space flag |
| amenities | text | Amenities list |
| price | numeric | Nightly price |
| minimum_nights | integer | Minimum stay |
| maximum_nights | integer | Maximum stay |
| number_of_reviews | integer | Review count |
| review_scores_rating | numeric | Average rating |
| geometry | jsonb | Spatial data |

### 🏠 `test_berlin_data.listings`
| Column | Type | Description |
|--------|------|-------------|
| listing_id | PK | Unique listing identifier |
| neighborhood_id | FK | Reference to neighborhoods |

## Data Quality Notes
- Data updated monthly from platform API
- Price reflects base nightly rate
- Coordinates accurate to 6 decimal places
- Includes active listings only