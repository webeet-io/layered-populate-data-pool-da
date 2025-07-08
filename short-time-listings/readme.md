
# Airbnb Berlin Short-Term Listings Data Integration


## 🔍 1. Data Source Discovery

### 📂 Data Source
The data is obtained from **Inside Airbnb**  [Inside Airbnb](https://insideairbnb.com/get-the-data/), which provides publicly available datasets collected through web scraping Airbnb listings worldwide, including Berlin.

### 🌐 Source & Origin
- Public dataset available as downloadable CSV files.
- Data collected via web scrapers targeting Airbnb’s public listing pages.

### ⏳ Update Frequency
- Monthly snapshots are generally published, with some cities potentially having more frequent updates.

### 🗃️ Data Type
- Static snapshots (monthly CSV dumps), not live API data.

---

## 🧩 2. Modelling & Planning

### 📌 Key Parameters Selected
We focused on columns related to:
- Listing details (price, availability, room type)
- Host information
- Neighborhood details
- Reviews and ratings
- Location coordinates

### 🔗 Data Relationships
- Listings are connected with neighborhoods.
- Hosts identified by `host_id`.
- Geospatial linkage through `latitude` and `longitude`.

### 📝 Planned Schema
The schema captures core listing information, normalized host data, and neighborhood references to maintain data integrity and facilitate analysis.

---

## 📊 3. Dataset Overview

| Column Name                | Data Type           | Description                                                                                   |
|----------------------------|---------------------|-----------------------------------------------------------------------------------------------|
| `id`                       | int64               | Unique identifier for each listing                                                           |
| `name`                     | object (string)     | Listing title/name                                                                           |
| `description`              | object (string)     | Description text of the listing                                                              |
| `host_id`                  | int64               | Unique identifier for the host                                                               |
| `host_name`                | object (string)     | Host's name (cleaned and normalized)                                                         |
| `host_since`               | datetime64[ns]      | Date when the host joined Airbnb                                                             |
| `host_is_superhost`        | boolean             | Whether the host is a superhost (True/False)                                                 |
| `host_listings_count`      | float64             | Number of listings managed by the host                                                       |
| `host_total_listings_count`| float64             | Total number of listings managed by the host (including inactive)                            |
| `host_identity_verified`   | boolean             | Whether the host identity is verified                                                        |
| `neighbourhood_cleansed`   | object (string)     | Cleaned neighborhood name                                                                     |
| `neighborhood`| object (string) | Higher-level neighborhood grouping (e.g., district)                                          |
| `latitude`                 | float64             | Latitude coordinate of the listing                                                           |
| `longitude`                | float64             | Longitude coordinate of the listing                                                          |
| `property_type`            | object (string)     | Type of property (e.g., apartment, house)                                                    |
| `room_type`                | object (string)     | Room type offered (entire home/apt, private room, shared room)                               |
| `accommodates`             | int64               | Number of guests the listing can accommodate                                                 |
| `bathrooms`                | float64             | Number of bathrooms                                                                          |
| `bedrooms`                 | float64             | Number of bedrooms                                                                           |
| `beds`                     | float64             | Number of beds                                                                              |
| `amenities`                | object (string)     | Amenities offered (raw string with multiple items)                                          |
| `price`                    | float64             | Price per night in local currency (cleaned of symbols and commas)                           |
| `minimum_nights`           | int64               | Minimum number of nights for a booking                                                      |
| `maximum_nights`           | int64               | Maximum number of nights for a booking                                                      |
| `has_availability`         | boolean             | Whether the listing currently has availability                                             |
| `availability_30`          | int64               | Number of available nights in the next 30 days                                            |
| `availability_60`          | int64               | Number of available nights in the next 60 days                                            |
| `availability_90`          | int64               | Number of available nights in the next 90 days                                            |
| `availability_365`         | int64               | Number of available nights in the next 365 days                                           |
| `number_of_reviews`        | int64               | Total number of reviews received                                                           |
| `number_of_reviews_ltm`    | int64               | Number of reviews in the last twelve months                                                |
| `number_of_reviews_l30d`   | int64               | Number of reviews in the last 30 days                                                     |
| `estimated_occupancy_l365d`| int64               | Estimated occupancy over the last 365 days                                                |
| `estimated_revenue_l365d`  | float64             | Estimated revenue over the last 365 days                                                  |
| `review_scores_rating`     | float64             | Overall review rating (out of 100 or 5 stars normalized)                                  |
| `review_scores_accuracy`   | float64             | Review score for accuracy                                                                  |
| `review_scores_cleanliness`| float64             | Review score for cleanliness                                                               |
| `review_scores_checkin`    | float64             | Review score for check-in experience                                                       |
| `review_scores_communication`| float64           | Review score for communication                                                             |
| `review_scores_location`   | float64             | Review score for location                                                                  |
| `review_scores_value`      | float64             | Review score for value                                                                     |
| `instant_bookable`         | boolean             | Whether the listing supports instant booking                                              |
| `reviews_per_month`        | float64             | Average number of reviews per month                                                       |

---

## ⚠️ 4. Known Issues

- Missing or inconsistent data in review scores and price fields.
- Some host names contain special characters or multiple hosts listed.

---

🧹 5. Data Cleaning and Transformation
Prices cleaned by removing currency symbols and commas, then converted to float.


Host-related columns normalized (e.g., converted host_is_superhost and host_identity_verified to boolean).


Date columns converted to datetime (host_since) for easier time-based analysis.


Text columns cleaned for consistent capitalization and removal of special characters.


Amenities remain as raw strings and can be parsed into lists for detailed feature analysis.


Missing values handled contextually using techniques like median imputation or left as nulls where appropriate.


Standardized neighbourhood_group_cleansed:


Stripped extra white spaces to ensure clean matching.


Applied a mapping dictionary to rename values to human-readable and standardized district names (e.g., 'Charlottenburg-Wilm.' → 'Charlottenburg-Wilmersdorf').


Renamed the column to neighborhood for simplicity and clarity.





