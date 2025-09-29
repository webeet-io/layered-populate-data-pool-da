# transform_osm_gyms.py
# Script to clean and map OSM gym data for database import

import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime

# === Step 1: Find and load the latest exported OSM data ===
pattern = os.path.join('gyms/sources', 'gyms_osm_berlin_*.csv')
osm_files = glob.glob(pattern)

if not osm_files:
    raise FileNotFoundError("No OSM gym export file found in ../sources/")

def extract_date(fname):
    basename = os.path.basename(fname)
    date_str = basename.replace('gyms_osm_berlin_', '').replace('.csv', '')
    return datetime.strptime(date_str, "%Y-%m-%d")

osm_files_sorted = sorted(osm_files, key=extract_date)
raw_file = osm_files_sorted[-1]  # most recent

print(f"Loading OSM export: {raw_file}")
df = pd.read_csv(raw_file)

# === Step 2: Field mapping and renaming ===
df = df.rename(columns={
    'name': 'name',
    'leisure': 'type',         # main type (fitness_centre or empty)
    'sport': 'type_alt',       # backup type (e.g., yoga)
    'street': 'street',
    'housenumber': 'housenumber',
    'postcode': 'postcode',
    'city': 'city',
    'opening_hours': 'opening_hours',
    'phone': 'phone',
    'website': 'website',
    'wheelchair': 'wheelchair',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'osm_id': 'osm_id',
    'osm_type': 'osm_type',
    'source': 'source'
})

# === Step 3: Data cleaning ===
df['type'] = df['type'].fillna('')
df['type'] = np.where(df['type'] != '', df['type'], df['type_alt'])
df.drop(columns=['type_alt'], inplace=True)

df['name'] = df['name'].fillna('Unknown Gym')
df['street'] = df['street'].fillna('')
df['housenumber'] = df['housenumber'].fillna('')
df['postcode'] = df['postcode'].fillna('')
df['city'] = df['city'].fillna('Berlin')  # default: Berlin

df['website'] = df['website'].fillna('').str.lower().str.strip()
df['phone'] = df['phone'].fillna('').str.strip()

df['opening_hours'] = df['opening_hours'].fillna('')
df['wheelchair'] = df['wheelchair'].fillna('unknown')

df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

df['osm_id'] = df['osm_id'].fillna('').astype(str)
df['osm_type'] = df['osm_type'].fillna('')
df['source'] = df['source'].fillna('OSM Overpass')

# === Step 4: Add placeholder for district_id (to be filled in a later step) ===
df['district_id'] = ''

# === Step 5: Save cleaned, mapped data ===
cleaned_file = 'gyms/sources/gyms_cleaned_for_db.csv'
df.to_csv(cleaned_file, index=False)

print(f"Cleaned data saved to {cleaned_file} ({len(df)} rows)")
