# transform_osm_gyms.py
# Script to clean and map OSM gym data for database import

import pandas as pd
import numpy as np

# === Step 1: Load exported OSM data (Update filename as needed!) ===
raw_file = '../sources/gyms_osm_berlin_2025-09-23.csv'
df = pd.read_csv(raw_file)

# === Step 2: Field mapping and renaming ===
# If your export columns already match these, this will just be for clarity!
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

# Prefer 'leisure' (fitness_centre) for type, fallback to 'sport' (e.g. yoga)
df['type'] = df['type'].fillna('')
df['type'] = np.where(df['type'] != '', df['type'], df['type_alt'])
df.drop(columns=['type_alt'], inplace=True)

# Fill missing names and addresses
df['name'] = df['name'].fillna('Unknown Gym')
df['street'] = df['street'].fillna('')
df['housenumber'] = df['housenumber'].fillna('')
df['postcode'] = df['postcode'].fillna('')
df['city'] = df['city'].fillna('Berlin')  # default: Berlin

# Clean website and phone fields
df['website'] = df['website'].fillna('').str.lower().str.strip()
df['phone'] = df['phone'].fillna('').str.strip()

# Opening hours and wheelchair accessible fields
df['opening_hours'] = df['opening_hours'].fillna('')
df['wheelchair'] = df['wheelchair'].fillna('unknown')

# Clean and convert coordinates
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# OSM fields
df['osm_id'] = df['osm_id'].fillna('').astype(str)
df['osm_type'] = df['osm_type'].fillna('')
df['source'] = df['source'].fillna('OSM Overpass')

# === Step 4: Add placeholder for district_id (to be filled in a later step) ===
df['district_id'] = ''

# === Step 5: Save cleaned, mapped data ===
cleaned_file = '../sources/gyms_cleaned_for_db.csv'
df.to_csv(cleaned_file, index=False)

print(f"Cleaned data saved to {cleaned_file} ({len(df)} rows)")
