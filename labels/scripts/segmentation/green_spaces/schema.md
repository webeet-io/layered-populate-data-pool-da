# Green Spaces Schema Documentation

## Database Tables
### `green_spaces`
- `id`: Primary key
- `name`: Park/garden name
- `area_sqm`: Size in square meters
- `maintenance_score`: 1-10 rating
- `species_count`: Number of plant species
- `facilities`: JSON array of amenities
- `last_inspection`: Date of last inspection
- `neighborhood_id`: Foreign key

## Data Relationships
```mermaid
erDiagram
    GREEN_SPACES ||--o{ NEIGHBORHOODS : "located_in"
    GREEN_SPACES {
        int id PK
        string name
        float area_sqm
        int maintenance_score
        int species_count
        json facilities
        date last_inspection
        int neighborhood_id FK
    }
```

## Field Descriptions
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| maintenance_score | integer | 1-10 rating (10=best) | 8 |
| species_count | integer | Count of unique plant species | 42 |
| facilities | json | Available amenities | ["playground","toilets"] |

## Data Quality Notes
- Maintenance scores updated quarterly
- Species counts may be seasonal
- Area measurements rounded to nearest 100sqm