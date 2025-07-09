
# Airbnb Berlin Short-Term Listings Data Integration


## 🔍 1. Data Source Discovery

### 📂 Data Source
The data is obtained from [Inside Airbnb](https://insideairbnb.com/get-the-data/), which provides publicly available datasets collected through web scraping Airbnb listings worldwide, including Berlin.

### 🌐 Source & Origin
- Public dataset available as downloadable CSV files.
- Data collected via web scrapers targeting Airbnb’s public listing pages.

### ⏳ Update Frequency
- Monthly snapshots are generally published, with some cities potentially having more frequent updates.

### 🗃️ Data Type
- Static snapshots (monthly CSV dumps), not live API data.

### 📄 License
- This data is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

---

## 🧩 2. Modelling & Planning

### 📌 Key Parameters Selected
We focused on columns covering:  
- Listing details (e.g., price, availability, room type)  
- Host information (e.g., host IDs, listing counts)  
- Neighborhood and district details  
- Reviews and ratings (including detailed review scores)  
- Location coordinates and geometry data  

### 🔗 Data Relationships
- Listings are linked to neighborhoods via the `neighborhood` column.  
- Hosts are uniquely identified by `host_id`.  
- Geospatial information is represented by `latitude`, `longitude`, and the `geometry` column for spatial analysis.  

### 📝 Planned Schema
The schema is designed to:  
- Capture core listing attributes and pricing  
- Normalize host-related data for consistency  
- Reference neighborhoods to maintain data integrity  
- Incorporate geospatial data to enable location-based analysis and visualization  

---

## 📊 3. Dataset Overview

| Column Name                | Data Type | Description                                                                                   |
|----------------------------|-----------|-----------------------------------------------------------------------------------------------|
| `id`                       |int64      | Unique identifier for each listing.                                                           |
| `host_id`                  |int64      | Unique identifier for the host.                                                               |
| `host_listings_count`      |Int64      | Number of listings currently managed by the host.                                            |
| `host_total_listings_count`|Int64      | Total number of listings ever managed by the host (including inactive).                       |
| `neighborhood`             |object     | Name of the neighborhood where the listing is located.                                       |
| `district`                 |string     | Larger administrative area or district containing the neighborhood.                          |
| `latitude`                 |float64    | Latitude coordinate of the listing.                                                          |
| `longitude`                |float64    | Longitude coordinate of the listing.                                                         |
| `property_type`            |string     | Type of property (e.g., apartment, house).                                                   |
| `room_type`                |string     | Room type offered (e.g., entire home/apt, private room, shared room).                         |
| `accommodates`             |int64      | Maximum number of guests the listing can accommodate.                                        |
| `bedrooms`                 |Int64      | Number of bedrooms in the listing.                                                           |
| `beds`                     |Int64      | Number of beds available in the listing.                                                     |
| `amenities`                |string     | List of amenities offered (raw string with multiple items).                                  |
| `price`                    |float64    | Price per night for the listing (cleaned of symbols and commas) in USD ($)                   |
| `minimum_nights`           |int64      | Minimum number of nights required for booking.                                              |
| `maximum_nights`           |int64      | Maximum number of nights allowed for booking.                                               |
| `number_of_reviews`        |int64      | Total number of reviews received by the listing.                                            |
| `review_scores_rating`     |float64    | Overall rating score given by reviewers.                                                    |
| `review_scores_accuracy`   |float64    | Rating score for accuracy of the listing description.                                       |
| `review_scores_cleanliness`|float64    | Rating score for cleanliness.                                                               |
| `review_scores_checkin`    |float64    | Rating score for the check-in experience.                                                   |
| `review_scores_communication`|float64  | Rating score for communication with the host.                                               |
| `review_scores_location`   |float64    | Rating score for the location of the listing.                                              |
| `review_scores_value`      |float64    | Rating score for value for money.                                                           |
| `reviews_per_month`        |float64    | Average number of reviews the listing receives per month.                                   |
| `bathrooms`                |float64    | Number of bathrooms (can be fractional, e.g., 1.5).                                         |
| `is_shared`                |Int64      | Boolean indicating if the bathroom is shared (1 for shared, 0 for private).                 |
| `geometry`                 |geometry   | Geospatial data representing the exact location and shape of the listing (point coordinates).|

---

## ⚠️ 4. Known Issues

- Missing or inconsistent data in review scores and price fields.

---

## 🧹 5. Data Cleaning and Transformation

- Prices cleaned by removing currency symbols and commas, then converted to float.

- Text columns cleaned for consistent capitalization and removal of special characters.

- Amenities remain as raw strings and can be parsed into lists for detailed feature analysis.

- Missing values handled contextually using techniques like median imputation or left as nulls where appropriate.

- Standardized `neighbourhood_group_cleansed`:

    - Stripped extra white spaces to ensure clean matching.

    - Applied a mapping dictionary to rename values to human-readable and standardized district names (e.g., 'Charlottenburg-Wilm.' → 'Charlottenburg-Wilmersdorf').

    - Renamed the column to `district` for simplicity and clarity.
