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
