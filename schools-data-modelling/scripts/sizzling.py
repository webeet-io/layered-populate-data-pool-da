#the siz'zle 🥓🧩
import geopandas as gpd
import pandas as pd
from shapely import wkt

# 📦📚 Step 1: Load school data from CSV and parse the geometry column
# We assume the 'geometry' column contains WKT (Well-Known Text) point data
# 🧠❗️ If your geometry column contains "lat/lon" columns instead of WKT text,
# you'll need to convert it like this instead:
# schools_df["geometry"] = gpd.points_from_xy(schools_df["longitude"], schools_df["latitude"])
# and skip the wkt.loads line.
schools_df = pd.read_csv(r"C:\Users\Maxdesk\Documents\berlin_schools_v1_with_geometry.csv")
schools_df["geometry"] = schools_df["geometry"].apply(wkt.loads)

# 🌍📌 Convert to GeoDataFrame with WGS84 (EPSG:4326)
schools_gdf = gpd.GeoDataFrame(schools_df, geometry="geometry", crs="EPSG:4326")

# 🧭🔁 Reproject to match SIZ zones (assumed to use EPSG:25833)
schools_gdf = schools_gdf.to_crs("EPSG:25833")

# 🌀🗺️ Step 2: Load spiral zone polygons (actually school induction zones – SIZ)
spiral_gdf = gpd.read_file(r"C:\Users\Maxdesk\Documents\spiral_zones.geojson")
print("🧪 Columns in spiral_gdf:", spiral_gdf.columns.tolist())

# 🧾🔎 Step 3: Rename the column to 'siz' if it's still called 'zone_id'
# This standardizes the name so we know what to expect during the join
if "spiral_zone" in spiral_gdf.columns:
    spiral_gdf = spiral_gdf.rename(columns={"spiral_zone": "siz"})
else:
    print("🧪 Available columns:", spiral_gdf.columns.tolist())
    raise ValueError("❌ Expected column 'spiral_zone' not found in spiral_gdf")

# 🌍🪄 Step 4: Reproject the spiral zones if CRS doesn't match schools
# A mismatch in projection would cause invalid spatial comparisons!
if spiral_gdf.crs != schools_gdf.crs:
    spiral_gdf = spiral_gdf.to_crs(schools_gdf.crs)

if "SIZ" in schools_df.columns:
    print("⚠️ Warning: Column 'SIZ' already exists in school CSV – will be overwritten.")

# 🧲🔗 Step 5: Spatial join using "within"
# Each school will get the 'siz' of the polygon it's inside
# Schools outside all polygons will get NaN
joined = gpd.sjoin(
    schools_gdf,
    spiral_gdf[["geometry", "siz"]],
    how="left",
    predicate="within"
)
# 📝📤 Step 6: Export result with SIZ assignments
# This CSV will include all schools, with 'siz' column added
output_path = r"C:\Users\Maxdesk\Documents"

joined.drop(columns=["index_right"], errors="ignore").to_csv(
    output_path + r"\schools_with_siz.csv", index=False
)

# 🚫🔍 Step 7 (optional): Export schools that did NOT match any SIZ
# Useful for debugging cases near zone edges or missing data
missing = joined[joined["siz"].isna()]
missing.to_csv(output_path + r"\schools_without_siz.csv", index=False)

# ✅📦 Summary
print("✅ Done!")
print("→ schools_with_siz.csv (includes assigned SIZ)")
print("→ schools_without_siz.csv (schools with no zone match)")
# 🦉 🧿