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
## Planned Table Schema: `listings`

Our team agreed on the following schema for storing long-term listings

| Column                     | Example Value                                         | SQL Datatype       | Notes |
|----------------------------|-------------------------------------------------------|--------------------|-------|
| `link`                     | `https://www.immowelt.de/expose/...`                  | `VARCHAR(500)`     | Full listing URL. |
| `type`                     | `Wohnung`                                             | `VARCHAR(20)`      | Enum: `Wohnung`, `Studio`, `Haus`, `WG`. |
| `first_tenant`             | `Erstbezug` / `NULL`                                  | `VARCHAR(20)`      | Optional field, may be null. |
| `price_euro`               | `1100`                                                | `INTEGER`          | Price without € or separators. |
| `number_of_rooms`          | `2.5`                                                 | `DECIMAL(3,1)`     | Allows half rooms (e.g., 2.5). |
| `surface_m2`               | `53.0`                                                | `DECIMAL(6,2)`     | Living area in square meters. |
| `floor`                    | `1` / `EG`                                            | `VARCHAR(10)`      | Store as integer or string if special values (e.g., "EG"). |
| `street_and_house_number`  | `Edisonstraße 31A`                                    | `VARCHAR(100)`     | Street name and house number. |
| `bezirk`                   | `Oberschöneweide` / `Köpenick`                        | `VARCHAR(50)`      | Berlin borough or sub-borough. |
| `city`                     | `Berlin`                                              | `VARCHAR(50)`      | Usually constant. |
| `postalcode`               | `12459`                                               | `VARCHAR(10)`      | Keep as string to preserve leading zeros. |


## Example Data

See [sample.csv](long_term_listing/examples/immowelt_page_1.csv) for a small example of the raw data before cleaning.


