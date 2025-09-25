# 0 General OSM
🌍 OpenStreetMap (OSM) is a free, collaborative map of the world that anyone can edit.
- It contains geospatial data: roads, railways, buildings, parks, rivers, amenities (cafés, hospitals, schools, etc.).
- Data is stored as:
  - Nodes (points, e.g. bus stops, cafés).
  - Ways (lines/polygons, e.g. roads, parks, building outlines).
  - Relations (groupings, e.g. bus routes, administrative boundaries).
- Everything is tagged with simple key=value pairs (e.g. amenity=cafe, highway=residential).

Most OSM objects will at least have:
- Identity (name, operator, brand)
- Location (addr:*)
- Availability (opening_hours, access)
- Contact (phone, website)
- Accessibility (wheelchair)

Data can be retrieved by using the following Python code:
```
import osmnx as ox
import geopandas as gpd
import pandas as pd

# populating a dataframe
tags = {"amenity": "university"}
university_gdf = ox.features_from_place("Berlin, Germany", tags)
university_gdf.info()
```
Example output:
```
<class 'geopandas.geodataframe.GeoDataFrame'>
MultiIndex: 117 entries, ('node', np.int64(278540049)) to ('way', np.int64(1211946568))
Data columns (total 87 columns):
 #   Column                     Non-Null Count  Dtype   
---  ------                     --------------  -----   
 0   geometry                   117 non-null    geometry
 1   addr:city                  62 non-null     object  
 2   addr:country               42 non-null     object  
 3   addr:housenumber           61 non-null     object  
 4   addr:postcode              61 non-null     object  
 5   addr:street                62 non-null     object  
 6   addr:suburb                44 non-null     object  
 7   amenity                    117 non-null    object  
 8   contact:phone              8 non-null      object  
 9   name                       109 non-null    object  
 10  operator                   59 non-null     object  
 ...
```
geometry contains information about longitude and latitude of an object and is provided in the format: POINT (13.35074 52.42464)

# 1 Columns of OSM to be used in all layers

| Columns name | Description | OSM object name |  mapping instruction | example |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| name | stores the primary, commonly used name of an object | name | 1:1 | Volkspark Friedrichshain, Café Einstein | 
| operator | organization that runs it | operator | 1:1 | S-Bahn Berlin GmbH | 
| brand | chain brand | brand | 1:1 | Starbucks | 
| longitude | east–west position on Earth | geometry | retrieve from first number in brackets | 13.34455 | 
| latitude | specifies how far north or south a point is from the Equator (0°) | geometry | retrieve from second number in brackets | 52.4988 | 
| country | country where object is located | addr:country | rename | DE | 
| city | city where object is located | addr:city | rename | Berlin | 
| street | street where object is located | addr:street | rename | Friedrichstraße | 
| housenumber | housenumber of street where object is located | addr:housenumber | rename | 180 | 
| postcode | postcode of city and street where object is located | addr:postcode | rename | 10117 | 
| neighborhood | neighborhood of object | addr:suburb | rename | Mitte | 
| phone | contact: phone number | contact:phone or phone | rename or 1:1 | +493045040 | 
| website | contact: website | contact:website or website| rename or 1:1 | | 
| wheelchair |accessibility for wheelchair | wheelchair | 1:1 | yes/no/limited |
| wheelchair_toilets |toilets accessible for wheelchairs | toilets:wheelchair | 1:1 | yes/no |
| opening_hours |opening hours of object in a standard machine-readable syntax| opening_hours | 1:1 | Mo-Su 08:00-20:00 |

## 1.1: in addition **district and district_id** shouild be added to all layers

# 2 Layer-by-Layer Review of Existing Data Sources
All columns shown in the table above should be added to all layers, independently if they are available in the legacy database or not.
In addition to these OSM or non-OSM columns have to be added according to legacy database.

| Layer Name  | Current Data Source | Can OSM Replace? | Tag in OSM  | Replacement Scope (Full/Partial) | additional new Columns in OSM | Columns Missing from OSM | Notes/Matching Stragegy |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |  ----------- |  ----------- |
| banks | OSM  |  |  |   |  |   |  |
| boundary / mileuschutz | gdi.berlin.de/ ../erhaltungs verordnungsgebiete | no well-established OSM tag/schema |  |  |   |   |  |
| colleges | edurank.org | yes | amenity, university | partial |  | university_id |  |
| | | | | |  | rank_in_berlin_brandenburg |  |
| | | | | |  | rank_in_germany |  |
| | | | | |  | enrollment |  |
| | | | | |  | founded |  |
| crime_statistics | Publisher: Berlin Police Department | no |  |   |   |  |  |
| dental_offices | OSM |  |  |   |   |  |  |
|  | Berlin Open Data Portal |  |  |   |   |  |  |
| gym | OSM |  |  |   |   |  |  |
| hospitals | deutsches-krankenhaus-verzeichnis.de | yes | amenity, hospital | partial | emergency (whether emergeny care is available): yes, no, designated | cases |  |
|  |  |  |  |   |   |  |  |
|  |  |  |  |   |   |  |  |
