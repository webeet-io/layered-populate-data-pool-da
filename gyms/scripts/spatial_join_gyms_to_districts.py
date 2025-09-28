# spatial_join_gyms_to_districts.py
# Assigns district_id and district to each gym by spatial join

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Load Gym-Data (cleaned)
gyms_file = '../sources/gyms_cleaned_for_db.csv'
gyms_df = pd.read_csv(gyms_file)

# 2. Load berlin_districts (GeoJSON)
districts_file = '../sources/berlin_districts.geojson'
districts_gdf = gpd.read_file(districts_file)

# 3. build Point geometries for gyms
gyms_gdf = gpd.GeoDataFrame(
    gyms_df,
    geometry=[Point(xy) for xy in zip(gyms_df.longitude, gyms_df.latitude)],
    crs='EPSG:4326'
)

# 4. Spatial join gyms with districts
gyms_with_district = gpd.sjoin(
    gyms_gdf,
    districts_gdf,
    how="left",
    predicate='within'
)

# 5. Assign district_id and district name from joined data
gyms_with_district['district_id'] = gyms_with_district['Schluessel_gesamt']
gyms_with_district['district'] = gyms_with_district['Gemeinde_name']

# 6. Export the result as CSV
output_file = '../sources/gyms_with_district.csv'
cols = list(gyms_df.columns) + ['district_id', 'district']
gyms_with_district[cols].to_csv(output_file, index=False)

print(f"Exported gyms with district info to {output_file} ({len(gyms_with_district)} rows)")
