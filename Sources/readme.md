# Transform pipeline outline:

# 1. Load the geojsons into GeoPandas or something compatible for my needs, i was told we use (As for EPSG:25833 (i think it is the german used format with metres )
      vs EPSG:4326 (the general used with decimal degrees) - both will work, in fact, ideally we'd map to school BOTH of these values (if available), but there is a higher chance that for other cities we can only get EPSG:4326. 
     Regarding geo data - we will most likely be using PostGis in Postgresql, so both formats can be stored)
# 2. Spatial join with induction_regions.geojsons → add induction_id, subdistrict/quarter

# 3. Merge on neighborhood? 