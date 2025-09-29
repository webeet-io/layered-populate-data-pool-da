# spatial_join_gyms_to_districts.py
# Assigns district_id and district to each gym by spatial join

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Load cleaned gym data
gyms_file = 'gyms/sources/gyms_cleaned_for_db.csv'
gyms_df = pd.read_csv(gyms_file)

# 2. Load Berlin districts (GeoJSON)
districts_file = 'gyms/sources/berlin_districts.geojson'
districts_gdf = gpd.read_file(districts_file)

# 3. Build Point geometries for gyms
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

# ---- COLUMN CHECK & CLEAN-UP ----
# Remove duplicate or unnecessary columns (like district_id.1)
unwanted_columns = [col for col in gyms_with_district.columns if col.endswith('.1')]
if unwanted_columns:
    print(f"Removing columns: {unwanted_columns}")
    gyms_with_district = gyms_with_district.drop(columns=unwanted_columns)

# ----- NEU: district_id sicher als String ohne ".0" -----
gyms_with_district['district_id'] = (
    gyms_with_district['district_id']
    .apply(lambda x: str(int(x)) if pd.notnull(x) else None)
)

# 6. Export the result as CSV
output_file = 'gyms/sources/gyms_with_district.csv'
cols = list(gyms_df.columns) + ['district_id', 'district']
gyms_with_district[cols].to_csv(output_file, index=False)

print(f"Exported gyms with district info to {output_file} ({len(gyms_with_district)} rows)")
