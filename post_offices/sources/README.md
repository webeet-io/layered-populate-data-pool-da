## Data Source

The primary data source for this project is a JSON file containing detailed information about **Deutsche Post** service locations within Berlin.

The data was obtained from the official [Deutsche Post](https://www.deutschepost.de/de/s/standorte.html) store locator website. Since a direct download of the location data is not provided, the file was acquired by:
1.  Using the browser's **Developer Tools** to monitor the **Network** tab.
2.  Performing a search for "Berlin" on the page.
3.  Applying a filter by selecting the "Postfiliale" service type. This action triggered the specific API request containing the desired data.

The server's response was a structured JSON file, which serves as the raw data for this project. This file includes key information for each service point, such as:

* Full address details (street, house number, zip code, city, and district).
* Geospatial coordinates (latitude and longitude).
* The name and type of the location.
* Detailed opening hours and other services stored in nested objects.

### Update Frequency

* The live data on the Deutsche Post server is updated **continuously** as locations are added, removed, or their details change. It is not on a fixed hourly or daily schedule.
* Our captured file (`raw_post.json`) represents a **snapshot** of the data at the moment it was downloaded and will not update on its own.

### Data Type

* **Source:** The source is **dynamic**. To get the most current data, the capture process must be repeated.
* **Our File:** Our `raw_post.json` is a **static, one-time import**.

### Relevant Data Fields

The raw JSON contains numerous fields. The most relevant for this project are:
* `zipCode`, `city`, `district`, `street`, `houseNo`: Full address components.
* `locationName`: The name of the service point.
* `keyWord`: The primary type of the location (e.g., *Postfiliale*).
* `geoPosition`: A nested object containing `latitude` and `longitude`.
* `pfTimeinfos`: A nested list of objects containing detailed opening hours for each day of the week.

## Data Transformation and Cleaning

The raw JSON data was not suitable for direct analysis due to its nested structure. A data processing pipeline was executed using **Python** and the **pandas** library to clean and transform the data into a usable, flat format.

The process consisted of the following steps:

1.  **Initial Conversion:** The raw `raw_post.json` file was read, and the primary list of locations (found under the `pfLocations` key) was extracted and converted into a base CSV file (`deutschepost_raw.csv`). This step flattened the main structure but left complex data (like opening hours and geo-coordinates) as string representations of objects in their respective columns.

2.  **Feature Extraction and Cleaning:** A second script processed the raw CSV file to extract valuable features from the complex columns:
    * **Opening Hours Parsing:** The `pfTimeinfos` column, containing a list of dictionaries as a string, was parsed using `ast.literal_eval`. Instead of creating separate columns for each day, the opening hours were extracted and consolidated into a single, formatted string in a new `opening_hours` column (e.g., `"Monday: 08:00-18:00; Tuesday: 08:00-18:00"`).
    * **Geocoordinate Extraction:** The `geoPosition` column, which contained a dictionary as a string, was similarly parsed to create two new dedicated columns: `latitude` and `longitude`.
  
3.  **Finalization:** The original, complex columns that were successfully parsed (`pfTimeinfos`, `geoPosition`) and the intermediate `distance` column were dropped. However, a number of other columns containing internal system IDs, formatting codes, or unprocessed complex data (e.g., `format1`, `pfServicetypes`, `pfOtherinfos`) were kept in the final dataset. Further cleaning and column selection would be the next step in a full analysis. The result was saved to `deutschepost_final_data_raw.csv`.

---
## Project Files Description

* `post_offices/sources/raw_post.json`: The original, raw data captured from the Deutsche Post website's API. Contains the complete, unfiltered information in a nested JSON format.

* `post_offices/sources/deutschepost_raw.csv`: An intermediate CSV file created from the raw JSON. The main structure is flattened, but some columns still contain complex data as strings.

* `post_offices/sources/deutschepost_final_data_raw.csv`: **The final, cleaned dataset.** This file is in a flat, tabular format, with opening hours and geo-coordinates extracted into their own columns, ready for analysis and visualization.

* `[convert_and_clean].ipynb`: The Jupyter Notebook containing all the Python and pandas code used to perform the data transformation and cleaning steps described above.

