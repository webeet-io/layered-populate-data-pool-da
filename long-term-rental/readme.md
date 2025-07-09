# 🏡 Immowelt Berlin Long-Term Listings Data Integration

## 🔍 1. Data Source Discovery

### 📂 Data Source  
The dataset is collected from [Immowelt](https://www.immowelt.de/), one of Germany’s leading real estate platforms, offering detailed long-term rental listings across Berlin.

### 🌐 Source & Origin  
- Data was scraped from publicly available Immowelt listing pages.  
- Listings represent long-term residential rental offerings in Berlin.

### ⏳ Update Frequency  
- Data was collected as a one-time snapshot, with potential for scheduled updates in future phases.

### 🗃️ Data Type  
- Static CSV snapshot of all active listings at time of collection.  
- No live API used.

---

## 🧩 2. Modelling & Planning

### 📌 Key Parameters Selected  
Focus was placed on features relevant for long-term residential analysis, including:
- Location data (address, coordinates, district)  
- Property characteristics (rooms, area, amenities)  
- Rental pricing  
- Contact and listing meta details

### 🔗 Data Relationships  
- Each listing is uniquely identified by `immo_id`.  
- Listings are mapped to Berlin districts via the `district` field.  
- Geospatial information is available via `latitude` and `longitude`.

### 📝 Planned Schema  
The schema is flat but structured to allow normalization for scalability (e.g., amenities or contact data could be factored out into separate tables in a relational setup).

---

## 📊 3. Dataset Overview

| Column Name     | Data Type        | Description                                                                 |
|------------------|------------------|-----------------------------------------------------------------------------|
| `immo_id`        | object (string)  | Unique identifier for each listing on Immowelt                              |
| `title`          | object (string)  | Title or short headline for the listing                                     |
| `address`        | object (string)  | Full address of the rental unit                                             |
| `zip_code`       | int64            | ZIP code of the property location                                           |
| `latitude`       | float64          | Latitude coordinate of the property                                         |
| `longitude`      | float64          | Longitude coordinate of the property                                        |
| `contact_name`   | object (string)  | Name of the listing agent or landlord (if available)                        |
| `kitchen`        | int64 (binary)   | Presence of a kitchen (1 = yes, 0 = no)                                     |
| `balcony`        | int64 (binary)   | Presence of a balcony (1 = yes, 0 = no)                                     |
| `garden`         | int64 (binary)   | Presence of a garden (1 = yes, 0 = no)                                      |
| `cellar`         | int64 (binary)   | Availability of a basement/cellar (1 = yes, 0 = no)                         |
| `private`        | int64 (binary)   | Whether the listing is private (1 = yes, 0 = no)                            |
| `rooms`          | float64          | Number of rooms in the unit                                                 |
| `sqm`            | int64            | Living area in square meters                                                |
| `rent`           | float64          | Base rent in EUR (monthly)                                                  |
| `extra_costs`    | float64          | Additional costs (utilities, service charges), if listed                    |
| `district`       | object (string)  | Name of the administrative district (e.g., Charlottenburg, Neukölln)       |
| `media_count`    | int64            | Number of media files (photos, videos) attached to the listing             |
| `url`            | object (string)  | Direct link to the listing on Immowelt                                      |

---

## ⚠️ 4. Known Issues

- `contact_name` is missing in ~40% of entries.  
- `extra_costs` not available for all listings, which may lead to underestimation of total rent.  
- `district` values are not always normalized (e.g., slight differences in spelling or casing).  
- Listings may include advertisements or placeholders not suitable for analysis.

---

## 🧹 5. Data Cleaning and Transformation

- Text fields (`title`, `address`, `contact_name`) were stripped of leading/trailing whitespace and standardized to UTF-8.  
- Boolean fields (`kitchen`, `balcony`, `garden`, `cellar`, `private`) were cast to integers (1/0).  
- Coordinate fields converted to `float` and verified for Berlin bounding box limits.  
- Rent-related fields (`rent`, `extra_costs`) converted to numeric format, ensuring decimal precision.  
- Listings with missing `latitude`/`longitude` or obviously incorrect `rooms` or `sqm` values were flagged for review.  
- District names partially normalized using a mapping dictionary for consistency in visualization tools.  
- Duplicate `immo_id`s removed to ensure listing uniqueness.

---

## 📌 Use Cases

This dataset enables:  
- Price analysis across Berlin districts  
- Geospatial clustering of high-rent or high-density areas  
- Amenity-based filtering for user preference modeling  
- Housing supply trends in long-term rental markets

