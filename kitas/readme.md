# Kindergarten Data Sources

## 1. Berlin Official Kita List
- Source: [Berlin Senate Department](https://www.berlin.de/...)
- Update: Monthly
- Format: Excel
- Fields: Name, address, capacity, contact info
- Transformation Steps:
  1. Extract relevant worksheets
  2. Standardize address format
  3. Geocode missing locations

## 2. OSM Kindergarten Data
- Source: Overpass API query
- Update: Real-time
- Format: GeoJSON
- Fields: Name, location, tags
- Transformation Steps:
  1. Filter for Berlin features
  2. Extract relevant tags
  3. Merge with official data
 
- kindergartens-data-model

Objective
Define the unified schema for storing Berlin kindergarten data from multiple sources (Berlin Gov Open Data & OpenStreetMap).
This schema will guide all transformation and loading steps.

Source Overview
Data will be ingested and unified from:

Berlin Government Open Data Portal

Official list of kindergartens

Includes district, provider, address, capacity, coordinates

OpenStreetMap (OSM) via Overpass API

Community-maintained dataset

Includes coordinates, names, providers, and sometimes capacity

Schema Definition
The unified schema is stored in the kindergartens table.

Column Name	Data Type	Description
id	SERIAL PRIMARY KEY	Unique identifier for each record
name	TEXT	Name of the kindergarten
address	TEXT	Street address including house number
postal_code	VARCHAR(10)	Postal code (PLZ)
district	TEXT	Administrative district in Berlin
type	TEXT	Type of kindergarten (e.g., public, private)
provider	TEXT	Organization or individual operating the kindergarten
capacity	INTEGER	Number of allowed places
latitude	NUMERIC(9,6)	Latitude in WGS84 format
longitude	NUMERIC(9,6)	Longitude in WGS84 format
source	TEXT	Data source (BerlinGov or OSM)
created_at	TIMESTAMP DEFAULT CURRENT_TIMESTAMP	Record creation timestamp

