
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import warnings
warnings.filterwarnings('ignore')

#  💫🐞😬
def debug_gdf_state(gdf, step_name):
    print(f"\n🔍 DEBUG - {step_name}:")
    print(f"   Type: {type(gdf)}")
    print(f"   Length: {len(gdf) if hasattr(gdf, '__len__') else 'N/A'}")
    if hasattr(gdf, 'empty'):
        print(f"   Empty: {gdf.empty}")
    if hasattr(gdf, 'columns'):
        print(f"   Columns: {list(gdf.columns)}")
    if hasattr(gdf, 'crs'):
        print(f"   CRS: {gdf.crs}")
    if hasattr(gdf, 'geometry') and len(gdf) > 0:
        print(f"   Geometry types: {gdf.geometry.geom_type.value_counts().to_dict()}")
        print(f"   Valid geometries: {gdf.geometry.is_valid.sum()}")
        print(f"   Non-null geometries: {gdf.geometry.notna().sum()}")
    return gdf

    # 🏋️‍♂️
def safe_load_berlin_data():
    print("🔄 Loading Berlin data...")
    try:
        gdf = gpd.read_file("C:/Users/Maxdesk/Documents/indu_te_se2.gpkg", engine="pyogrio")
        debug_gdf_state(gdf, "Loaded from file")
        return gdf
    except Exception as e:
        print(f"❌ Could not load from file: {e}")
        raise

    #   🦋
def safe_transform_to_utm(gdf):
    print("🔄 Transforming to UTM...")
    try:
        if gdf.crs and 'utm' in str(gdf.crs).lower():
            print("   Already in UTM projection")
            return gdf
        gdf_utm = gdf.to_crs('EPSG:25833')
        debug_gdf_state(gdf_utm, "Transformed to UTM")
        return gdf_utm
    except Exception as e:
        print(f"❌ UTM transformation failed: {e}")
        raise

    #  🧹 & 👨‍🍳
def clean_and_prepare_gdf(gdf):
    print("🔄 Cleaning and preparing GeoDataFrame...")
    debug_gdf_state(gdf, "Input to clean_and_prepare_gdf")
    if gdf is None or len(gdf) == 0:
        raise ValueError("Input GeoDataFrame is empty or None!")
    if 'geometry' not in gdf.columns:
        raise ValueError("GeoDataFrame has no geometry column!")

    clean_gdf = gdf[gdf.geometry.notna() & gdf.geometry.is_valid & ~gdf.geometry.is_empty].copy()
    print(f"✅ Cleaned rows: {len(clean_gdf)} (from {len(gdf)} original)")

    if len(clean_gdf) == 0:
        raise ValueError("No valid geometries remaining after cleaning!")

    clean_gdf['area'] = clean_gdf.geometry.area
    if 'population' not in clean_gdf.columns:
        clean_gdf['population'] = np.random.randint(10000, 500000, len(clean_gdf))

    clean_gdf['centroid'] = clean_gdf.geometry.centroid
    clean_gdf['centroid_x'] = clean_gdf['centroid'].x
    clean_gdf['centroid_y'] = clean_gdf['centroid'].y

    debug_gdf_state(clean_gdf, "Cleaned and prepared")
    return clean_gdf
    
    # 🌌🏫
def create_spiral_zones(gdf):
    print("🔄 Creating spiral zones...")
    if len(gdf) == 0:
        raise ValueError("Cannot create spiral zones from empty GeoDataFrame!")

    center_x = gdf['centroid_x'].mean()
    center_y = gdf['centroid_y'].mean()
    print(f"   Spiral center: ({center_x:.2f}, {center_y:.2f})")

    gdf = gdf.copy()
    gdf['distance_from_center'] = np.sqrt((gdf['centroid_x'] - center_x)**2 + (gdf['centroid_y'] - center_y)**2)
    gdf['angle_from_center'] = np.arctan2(gdf['centroid_y'] - center_y, gdf['centroid_x'] - center_x)
    gdf['angle_from_center'] = np.where(gdf['angle_from_center'] < 0, gdf['angle_from_center'] + 2 * np.pi, gdf['angle_from_center'])
    gdf['spiral_param'] = gdf['distance_from_center'] * 0.1 + gdf['angle_from_center']
    gdf_sorted = gdf.sort_values('spiral_param').reset_index(drop=True)
    gdf_sorted['spiral_zone'] = range(1, len(gdf_sorted) + 1)
    print(f"✅ Created {len(gdf_sorted)} spiral zones")
    return gdf_sorted

# 👨‍🎨
def plot_spiral_zones(result):
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.colors as colors

    if result is not None:
        fig, ax = plt.subplots(figsize=(12, 12))

        norm = colors.Normalize(vmin=1, vmax=result['spiral_zone'].max())
        cmap = cm.get_cmap("viridis")

        result.plot(
            column='spiral_zone',
            cmap=cmap,
            linewidth=0.8,
            edgecolor='black',
            ax=ax,
            legend=True,
        )

        # 🧠 Label each zone with its spiral number
        for idx, row in result.iterrows():
            centroid = row['centroid']
            ax.text(centroid.x, centroid.y, str(row['spiral_zone']),
                    fontsize=6, ha='center', va='center', color='white')

        ax.set_title("🌀 Spiral-Induction Zones Berlin", fontsize=18)
        ax.axis('off')
        plt.tight_layout()

        # 💾 Save PNG
        plt.savefig("spiral_map_berlin.png", dpi=300)
        plt.show()

        # 💾 Save GeoJSON + GPKG
        try:
            result[['spiral_zone', 'geometry']].to_file("spiral_zones.geojson", driver="GeoJSON")
            result[['spiral_zone', 'geometry']].to_file("spiral_zones.gpkg", driver="GPKG")
            print("✅ Saved spiral_zones.geojson and spiral_zones.gpkg")
        except Exception as e:
            print(f"⚠️ Failed to write files: {e}")

    # 🥧
def main():
    print("🚀 Starting Berlin Spiral Logic Workflow")
    print("=" * 50)
    try:
        gdf = safe_load_berlin_data()
        gdf_utm = safe_transform_to_utm(gdf)
        gdf_clean = clean_and_prepare_gdf(gdf_utm)
        result = create_spiral_zones(gdf_clean)
        print(f"🎉 Workflow completed successfully! Final result has {len(result)} spiral zones")
        plot_spiral_zones(result)
    except Exception as e:
        print("DEBUG AFTER ERROR LINE")
        print(f"\n❌ ERROR in main workflow: {e}")
        import traceback
        traceback.print_exc()  
        
        # 🕵️📂
        schools_gdf = gpd.read_file("C:/Users/Maxdesk/Documents/berlin_schools_v1_with_geometry.csv")

        # 💃
        schools_gdf = schools_gdf.to_crs(result.crs)

        # 🖇️ 
        schools_with_siz = gpd.sjoin(
            schools_gdf,
            result[['spiral_zone', 'geometry']],
            how="left",
            predicate="within"
        )
    
        # 💾 
    result[['spiral_zone', 'geometry']].to_file("spiral_zones.geojson", driver="GeoJSON")
    result[['spiral_zone', 'geometry']].to_file("spiral_zones.gpkg", driver="GPKG")

if __name__ == "__main__":
    main()
         # 🙇🦥😸🐕‍🦺