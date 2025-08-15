# Berlin Places Extractor

This script queries the [Overpass API](https://overpass-api.de/) to retrieve information about restaurants, cafés, and bars located in Berlin, then exports the results to a CSV file.

## Features
- Retrieves data for amenities: `restaurant`, `cafe`, `bar`.
- Extracts:
  - Name
  - Category (amenity type)
  - Cuisine type (if available)
  - Full address
  - Latitude/Longitude coordinates
  - Website
  - Phone number
  - Opening hours
  - Takeaway availability
  - Wheelchair accessibility
- Saves the data as `berlin_places.csv`.

## Requirements
- Python 3.8+
- Packages:
  ```bash
  pip install requests pandas folium
  ```

## How It Works
1. **Overpass API query**  
   The script sends a POST request to the Overpass API to select all amenities (`restaurant`, `cafe`, `bar`) within the Berlin administrative area.

2. **Data extraction**  
   For each element returned, the script retrieves:
   - Tags like `name`, `amenity`, `cuisine`, etc.
   - Address fields (`addr:street`, `addr:housenumber`, `addr:postcode`, `addr:city`)
   - Coordinates (directly from the node or from the `center` of a way/relation)

3. **CSV export**  
   The extracted data is written to `berlin_places.csv` in UTF-8 encoding.

## Running the Script
```bash
python Untitled-1.py
```
The script will:
- Print **"Executing Overpass query..."** to indicate it’s querying the API.
- Print the number of elements extracted.
- Save the CSV file in the current directory.

## Output Example
| name         | category   | cuisine   | address                   | lat       | lon       | website        | phone      | opening_hours         | takeaway | wheelchair |
|--------------|-----------|-----------|---------------------------|-----------|-----------|----------------|------------|-----------------------|----------|------------|
| Example Café | cafe       | coffee    | Example St 10, 10115 Berlin| 52.5200   | 13.4050   | example.com    | +49 30 ... | Mo-Fr 08:00-18:00     | yes      | yes        |


# Reverse Geolocation to Create `district` Column

**Objective:**  
We want to convert latitude and longitude coordinates into a human-readable administrative area, specifically the **district**, and add it as a new column in our dataset.

---

## 1. What is Reverse Geolocation?

Reverse geolocation (or reverse geocoding) is the process of converting geographic coordinates (latitude and longitude) into a readable address or place name. This can include:

- Street name  
- City  
- District or administrative region  
- Country  

For example:  
Latitude: 40.730610, Longitude: -73.935242 → District: Manhattan

---

## 2. Tools in Python

Common Python libraries for reverse geocoding:

1. **`geopy`**  
   - Provides easy access to multiple geocoding services.
   - Example services: Nominatim (OpenStreetMap), GoogleV3 (Google Maps API).
   
2. **`pandas`**  
   - To handle your dataset and create a new column.

---

## 3. Example Workflow

```python
# Import libraries
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Load your dataset
df = pd.read_csv("your_data.csv")

# Initialize geocoder
geolocator = Nominatim(user_agent="geoapiExercises")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Define a function to extract district from coordinates
def get_district(lat, lon):
    location = reverse((lat, lon), language='en')
    if location and 'address' in location.raw:
        return location.raw['address'].get('suburb') or location.raw['address'].get('city_district') or location.raw['address'].get('city')
    return None

# Apply function to create 'district' column
df['district'] = df.apply(lambda row: get_district(row['latitude'], row['longitude']), axis=1)

# Preview
df.head()


# Data Transformation and Creation of the Opening Hours Library

**Objective:**  
Transform raw operational data into a structured format and create a reusable **Opening Hours library** that standardizes store or service hours for analysis.

---

## 1. Raw Data Overview

Typical raw data might include:

| Store | Monday | Tuesday | ... | Sunday |
|-------|--------|---------|-----|--------|
| Store A | 9:00-17:00 | 9:00-17:00 | ... | Closed |
| Store B | 10:00-18:00 | 10:00-18:00 | ... | 10:00-14:00 |

**Challenges:**
- Different formats (`9-5`, `09:00-17:00`, `Closed`)  
- Missing or inconsistent entries  
- Need for machine-readable, standardized representation

---

## 2. Transformation Goals

1. Standardize the time format to `HH:MM-HH:MM`.
2. Handle special cases like `Closed` or `24h`.
3. Convert into a **dictionary or library** that can be reused for analysis.

---

## 3. Example Workflow in Python

```python
import pandas as pd

# Load raw data
df = pd.read_csv("raw_opening_hours.csv")

# Function to standardize time
def standardize_time(time_str):
    if pd.isna(time_str) or time_str.lower() == "closed":
        return None
    # Handle 9-5 or 09:00-17:00 formats
    parts = time_str.replace(" ", "").split("-")
    start = parts[0] if ":" in parts[0] else parts[0]+":00"
    end = parts[1] if ":" in parts[1] else parts[1]+":00"
    return f"{start}-{end}"

# Apply standardization
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