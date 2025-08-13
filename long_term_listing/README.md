Readme for PR 205

# 📊 Data Sources for Long-Term Listings in Berlin

This document lists potential datasets for enriching the **Long-Term Listings in Berlin (Immowelt)** layer.  
Each entry includes the origin, update frequency, data type, and relevant fields.

---

## Data Sources

| Source Name | Origin | Update Frequency | Data Type | Relevant Fields | Link |
|-------------|--------|------------------|-----------|-----------------|------|
| **Immowelt** | Real estate platform (Germany) | Daily | Dynamic (Scraper) | Listing ID, Title, Price, Size, Location, Amenities | [Website](https://www.immowelt.de/) |
| **Berlin Open Data Portal** | Government portal | Varies | Static (Download) | Neighborhood boundaries, demographic stats, infrastructure | [Portal](https://daten.berlin.de/) |
| **OpenStreetMap** | Crowdsourced mapping platform | Weekly | Dynamic (API) | Coordinates, POIs, transport stops, boundaries | [Website](https://www.openstreetmap.org/) |
| **Destatis – German Federal Statistical Office** | Government statistics agency | Yearly | Static (Download) | Population, income levels, housing statistics | [Website](https://www.destatis.de/EN/Home/_node.html) |
| **Berlin Apartment Listings (Kaggle)** | Kaggle community dataset | One-time snapshot | Static (Download) | Price, Size, Rooms, District | [Dataset](https://www.kaggle.com/datasets/doubleshield/apartment-berlin) |

---
Planned Tables Schema Example
listings (
  id INT,
  title VARCHAR,
  price DECIMAL,
  size_sq_m DECIMAL,
  rooms INT or DECIMAL ,
  listing_date DATE,
  updated_date DATE,
  address VARCHAR,
  latitude DECIMAL,
  longitude DECIMAL,
  neighborhood VARCHAR,
  contact_info VARCHAR,
  features JSON,
  source_link VARCHAR
)


