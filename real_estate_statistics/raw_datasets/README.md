#### [ibb_bezirke.csv](ibb_bezirke.csv)
- Columns:
    - `neighborhood_id`: Unique identifier for the district (1-12) (currently known as `district_id`)
    - `neighborhood`: Name of the district (e.g., Mitte, Spandau, etc.) ((currently known as `district_name`))
    - `median_net_rent`: Median net cold rent in euros per square meter per month
    - `number_of_cases`: Number of rental listings (cases) used for calculating statistics
    - `mean_net_rent`: Arithmetic mean net cold rent in euros per square meter per month
    - `year`: Calendar year the data refers to

#### [ibb_planungsraeume.csv](ibb_planungsraeume.csv)
- Columns:
    - `neighborhood_id`: Unique identifier for the district (1-12) (currently known as `district_id`)
    - `street_name`: Name of the street (e.g., Bremer Straße, Neu Westend, etc.)
    - `median_net_rent`: Median net cold rent in euros per square meter per month
    - `number_of_cases`: Number of rental listings (cases) used for calculating statistics
    - `mean_net_rent`: Arithmetic mean net cold rent in euros per square meter per month
    - `year`: Calendar year the data refers to

#### [land_prices.csv](land_prices.csv)
- Columns:
    - `Bodenrichtwert-Nummer`: Code assigned to a specific land value zone (not relevant to our dataset)
    - `neighborhood`: Name of the district (e.g., Mitte, Spandau, etc.) ((currently known as `district_name`))
    - `standart_land_value`: Standard land value (Bodenrichtwert) in euros per square meter
    - `typical_land_use_type`: Typical land use type (e.g., Wohngebiet, Gewerbe, etc.)
    - `typical_floor_space_ratio`: Typical floor space ratio (GFZ), indicating permitted building density
    - `reference_date`: Official assessment date (Stichtag) for the land value and usage data

#### [statistical_regional_data_berlin.csv](statistical_regional_data_berlin.csv)
- Column:
    - `neighborhood`: Name of the district (e.g., Mitte, Spandau, etc.) ((currently known as `neighbourhood`))
    - `year`: Calendar year the data refers to
    - `inhabitants`: Number of inhabitants/residents
    - `total_area_ha`: Total area in hectares
    - `share_forest_water_agriculture`: Percentage share of forest, water, and agriculture area
    - `forest_area_ha`: Forest area in hectares
    - `water_area_ha`: Water area in hectares
    - `agriculture_area_ha`: Agricultural land area in hectares
    - `population_density_per_ha`: Population density (residents per hectare)
    - `number_of_residences`: Number of residential units or dwellings
    - `living_space_per_resident_m2`: Living area per resident in square meters

#### [raw_schema.png](raw_schema.png)
- Visual overview of the original data structure