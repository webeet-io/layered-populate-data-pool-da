## Berlin Places Extractor

This project retrieves information about restaurants, cafés, and bars in Berlin using the Overpass API and transforms the data for further analysis, including reverse geolocation and standardized opening hours.

⸻

Table of Contents
	1.	Features
	2.	Requirements
	3.	How It Works
	4.	Running the Script
	5.	Output Example
	6.	Reverse Geolocation to Create district Column
	7.	Data Transformation and Opening Hours Library

⸻

Features
	•	Retrieves data for amenities: restaurant, cafe, bar.
	•	Extracts:
	•	Name
	•	Category (amenity type)
	•	Cuisine type (if available)
	•	Full address
	•	Latitude/Longitude coordinates
	•	Website
	•	Phone number
	•	Opening hours
	•	Takeaway availability
	•	Wheelchair accessibility
	•	Saves the data as berlin_places.csv.

⸻

Requirements
	•	Python 3.8+
	•	Packages:

pip install requests pandas folium geopy


⸻

How It Works
	1.	Overpass API Query
The script sends a POST request to the Overpass API to select all amenities (restaurant, cafe, bar) within Berlin.
	2.	Data Extraction
For each element returned, the script retrieves:
	•	Tags like name, amenity, cuisine, etc.
	•	Address fields (addr:street, addr:housenumber, addr:postcode, addr:city)
	•	Coordinates (from the node or center of a way/relation)
	3.	CSV Export
Extracted data is written to berlin_places.csv in UTF-8 encoding.

⸻

Running the Script

python Untitled-1.py

The script will:
	•	Print “Executing Overpass query…”
	•	Print the number of elements extracted
	•	Save the CSV file in the current directory

⸻

Output Example

name	category	cuisine	address	lat	lon	website	phone	opening_hours	takeaway	wheelchair
Example Café	cafe	coffee	Example St 10, 10115 Berlin	52.5200	13.4050	example.com	+49 30 …	Mo-Fr 08:00-18:00	yes	yes


⸻

Reverse Geolocation to Create district Column

Objective: Convert latitude and longitude into a human-readable administrative district and add it as a new column.

What is Reverse Geolocation?

Reverse geolocation converts geographic coordinates (latitude/longitude) into a readable address, such as:
	•	Street
	•	City
	•	District
	•	Country

Example:

Latitude: 40.730610, Longitude: -73.935242 → District: Manhattan

Tools in Python
	•	geopy: Provides access to multiple geocoding services (Nominatim, GoogleV3)
	•	pandas: For dataset handling

Example Workflow

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Load dataset
df = pd.read_csv("your_data.csv")

# Initialize geocoder
geolocator = Nominatim(user_agent="geoapiExercises")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Function to extract district
def get_district(lat, lon):
    location = reverse((lat, lon), language='en')
    if location and 'address' in location.raw:
        return location.raw['address'].get('suburb') \
            or location.raw['address'].get('city_district') \
            or location.raw['address'].get('city')
    return None

# Create 'district' column
df['district'] = df.apply(lambda row: get_district(row['latitude'], row['longitude']), axis=1)

# Preview
df.head()


⸻

Data Transformation and Opening Hours Library

Objective: Transform raw operational data into a structured format and create a reusable Opening Hours library.

Raw Data Overview

Example input:

Store	Monday	Tuesday	…	Sunday
Store A	9:00-17:00	9:00-17:00	…	Closed
Store B	10:00-18:00	10:00-18:00	…	10:00-14:00

Challenges:
	•	Inconsistent formats (9-5, 09:00-17:00, Closed)
	•	Missing entries
	•	Need for standardized, machine-readable format

Transformation Goals
	1.	Standardize time to HH:MM-HH:MM
	2.	Handle special cases (Closed, 24h)
	3.	Create a reusable dictionary/library for analysis

Example Workflow

import pandas as pd

# Load raw opening hours
df = pd.read_csv("raw_opening_hours.csv")

# Standardize time function
def standardize_time(time_str):
    if pd.isna(time_str) or time_str.lower() == "closed":
        return None
    parts = time_str.replace(" ", "").split("-")
    start = parts[0] if ":" in parts[0] else parts[0]+":00"
    end = parts[1] if ":" in parts[1] else parts[1]+":00"
    return f"{start}-{end}"

# Apply to all days
for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
    df[day] = df[day].apply(standardize_time)

# Create opening hours library
opening_hours_library = {}
for index, row in df.iterrows():
    opening_hours_library[row['Store']] = {
        day: row[day] for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    }

# Example output
print(opening_hours_library['Store A'])

Sample Output:

{
  'Monday': '09:00-17:00',
  'Tuesday': '09:00-17:00',
  'Wednesday': '09:00-17:00',
  'Thursday': '09:00-17:00',
  'Friday': '09:00-17:00',
  'Saturday': None,
  'Sunday': None
}