# Population Statistics in Berlin
🔍 Data Source Used


* File: SB_A01-05-00_2024h02_BE.xlsx


* Source: Statistik Berlin-Brandenburg [statistik-berlin-brandenburg.de](https://www.statistik-berlin-brandenburg.de/bevoelkerung)


*  Description: Population by age group and gender, broken down by Berlin districts and postal codes


*  Type: Static (semi-annual release)


*  Update Frequency: Twice a year (H1 and H2)


*  License: Open public data


✅ Modelling & Planning


📌 Key Parameters / Columns from Raw Data


File: SB_A01-05-00_2024h02_BE.xlsx (Population by age groups, neighbourhood and gender)


 Relevant Columns:

 
* Neighbourhood
* Postcode
* Gender (M, F)
* Age_Groups (0–5, 6–10, ..., 80+)
* nationality
* Population_Count
* last_updated_date


🧩 How This Data Connects to Existing Tables


*  Primary Join Field: Neighbourhood(matching neighborhood or district name in listings dataset) and postcode.


🗂️ Planned Schema for Population_stats


| Column                 | Type      | Description                                         |
|------------------------|-----------|-----------------------------------------------------|
| `neighbourhood`                   | STRING      | District name (Bezirk)         |
| `postcode`                 | STRING      | Postal code                                |
| `gender`             | STRING      | "M" / "F"                               |
| `age_group`            | STRING      | Age range (e.g., "0-5", "60+")                      |
| `nationality`     | STRING      | Nationality group if applicable    |
| `population_count`       | INTEGER      | Count of people           |
| `last_updated_date` | DATE      | Date of data file(e.g., 2024-07-01 for H2 2024)   |

---


⚠️ Known Data Issues or Inconsistencies


* Inconsistent naming for districts.


* Age groups may be non-uniform across files


* Some totals are duplicated across gender/nationality aggregations (double counting possible)



🔄 Transformation Plan


1. Load & Normalize:


    *  Import CSV files into dataframes.


    *  Normalize all column headers.


2. Unpivot Age/Nationality Columns:


    *  Reshape wide age/nationality columns into long format (age_group, nationality)


3. Join Mapping Tables:


    *  Primary Join Field: Neighbourhood(matching neighborhood or district name in listings dataset) and postcode.


4. Standardize Columns:


    *  Rename columns consistently.


    *  Convert types (e.g., integers, strings).


5. Deduplicate:


    *  Remove total rows or repeated counts.


6. Save Cleaned File:


    *  Output as CSV  under a transformed/ directory for loading.
