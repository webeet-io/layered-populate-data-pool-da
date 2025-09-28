# Layer: Gyms (Fitness Studios, Yoga and Fitness Centers) in Berlin

## Purpose
Integration and mapping of fitness studios, yoga studios, and fitness centers in Berlin as a new data layer within our existing database structure.

## Motivation
By adding the "gyms" layer, we can analyze and visualize fitness offerings in Berlin and connect this data with other city Points of Interest (POIs).

## Layer Structure
- gyms/
  - sources/      # Storage and documentation of raw data sources
  - scripts/      # Scripts for data collection, transformation and database import

## Data Update Strategy
- Data is collected using the [OpenStreetMap Overpass API](https://overpass-api.de/api/interpreter).
- The script `gyms/scripts/get_osm_gyms.py` can be run at any time to fetch and export the latest gym data as CSV.
- We recommend regular updates (e.g., monthly) to keep the data fresh. Automation (e.g., via cron or CI) is possible for production use.

## Status
Research and data acquisition phase completed – initial data export and documentation in place.
Next step: data transformation and mapping to the database schema.
