
## Project Update - Database Table Design
### Date: 21/08/2025

Today, our group reached key milestones in preparing our property listings database:

- Agreed on table constraints: We defined and approved essential constraints to ensure data integrity in the database.
- Finalized table structure: The columns and their types are now fixed, aligned with our data needs and analysis plans.
- Unique identifiers: We established district_id as a foreign key (linking each listing to its district) and listing_id as the primary key for each record, ensuring every          row is uniquely identifiable.

Next steps will focus on implementing these definitions in the database system and preparing our data for import.

## Data Transformation & Documentation

### Date: 20/08/2025

## Task Division & Progress

### Sumi – Documentation

- Created and updated the README file.

- Documented workflows, dependencies, and usage instructions.

### Maria – Python Scripts

- Developed and refined Python transformation scripts.

- Automated data cleaning and preparation steps.

### Jyoti – Data Appending

- Integrated processed data into Google Sheets.

- Ensured updates were consistent and accessible for the team.

### Parallel Workflows

- All tasks executed simultaneously to save time and leverage team expertise.

- Dependencies between tasks were clearly identified and managed.

- Collaboration & Alignment

- Regular check-ins to sync progress.

- Smooth handoffs between script outputs (Maria), data appending (Jyoti), and documentation (Sumi).







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


-------------------------------------------------------------------
## Data Cleaning

Today, our group began the data cleaning process on the raw dataset. Specifically, we:

 - Applied Python cleaning functions to explore the dataset after transformations.

 - Checked for inconsistencies in formatting (e.g., variations in values across columns).

 - Identified empty and missing values that need to be addressed.

This work gives us a clearer picture of the dataset’s current state and helps define the next steps for standardizing the data.



