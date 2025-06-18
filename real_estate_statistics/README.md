# Historical Prices and Real Estate Statistics in Berlin

## Identified Data Sources

1. [IBB Wohnungsmarktbericht 2024](https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2024.html)
    - **Origin**: Public Dataset
    - **Update Frequency**: Annual
    - **Description**: District- and street-level rental prices and case counts in Berlin, with median and mean net cold rent per m2 per month, by year.

2. [FIS-Broker Berlin](https://fbinter.stadt-berlin.de/fb/index.jsp)
    - **Origin**: Public Dataset
    - **Update Frequency**: Annual
    - **Description**: District-level land value indicators, typical land use types and floor space indices, by year.

## Modelling & Planning

- **Key Parameters Selected**: From the [raw datasets](./raw_datasets/), the following columns were selected as most relevant:
    - `district_id`: Unique identifier for the district (1-12)
    - `district_name`: Name of the district (e.g., Mitte, Spandau, etc.)
    - `median_net_rent`: Median net cold rent in euros per square meter per month
    - `number_of_cases`: Number of rental listings (cases) used for calculating statistics
    - `mean_net_rent`: Arithmetic mean net cold rent in euros per square meter per month
    - `year`: Calendar year the data refers to
    - `standart_land_value`: Standard land value (Bodenrichtwert) in euros per square meter
    - `typical_land_use_type`: Typical land use type (e.g., Wohngebiet, Gewerbe, etc.)
    - `typical_floor_space_ratio`: Typical floor space ratio (GFZ), indicating permitted building density
    - `reference_date`: Official assessment date (Stichtag) for the land value and usage data

- **Data Relationships**: All datasets in this project are connected using the `district_name` field as the primary key for joins and integration.

    - `district_name`: The standardized name of a Berlin administrative district (e.g., "Friedrichshain-Kreuzberg"). This field is used consistently across all data sources to enable merging and comparison.
    - If available, `district_id` may also be present for reference or indexing

- **Schema**:

- **Data Issues**:

- **Transformation Plan**: