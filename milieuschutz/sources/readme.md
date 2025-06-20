# [Data Integration] Milieuschutz in Berlin #67

This issue outlines the process for integrating a new data layer on topic Milieuschutz in Berlin into the database. The work should be completed in 3 PRs, one for each major step.


# Data Sources and Transformation Plan

## Data Sources Used
## Data Sources / Links Used:

- **Berlin Erhaltungsverordnungsgebiete (WFS):**
    - Official Berlin Geoportal OGC WFS service providing geospatial data on social conservation areas (Milieuschutzgebiete).
    - Dynamic, API-based, updated as new areas are designated.
- **Milieuschutzgebiet Street Lists (PDF/CSV):**
    - Official street lists from the Berlin Senate Department for Urban Development, available as PDF and converted to CSV for analysis.
    - Static, updated with new designations or changes.
- **GENESIS-Online Statistical API:**
    - Federal Statistical Office API for demographic and statistical data.
    - Dynamic, regularly updated.
- **Berlin Open Data Portal:**
    - Additional datasets for enrichment, both static and dynamic.
- [Berliner Mieterverein: Info 68 Milieuschutzgebiete](https://www.berliner-mieterverein.de/recht/infoblaetter/info-68-milieuschutzgebiete-was-mieter-wissen-sollten.htm)  
    Information page about Berlin's social conservation areas (Milieuschutz) for tenants.
- [Berlin.de: Städtebauliche Bauberatung Charlottenburg-Wilmersdorf](https://www.berlin.de/ba-charlottenburg-wilmersdorf/verwaltung/aemter/stadtentwicklung/stadtplanung/staedtebauliche-bauberatung/artikel.652304.php)  
    Official city planning and urban development information for the Charlottenburg-Wilmersdorf district.
- [OGC WMS Standard](https://www.ogc.org/standards/wms/)  
    Official documentation for the OGC Web Map Service (WMS) standard for serving georeferenced map images.
- [GENESIS-Online Webservice-Schnittstelle (API)](https://www-genesis.destatis.de/datenbank/online/statistics#modal=web-service-api)  
    Webservice interface (API): By using the RESTful/JSON interface, the GENESIS-Online database can be integrated into automated processes. Using the webservice requires free registration on GENESIS-Online.  
    Documentation: Linguistic interface description (PDF), code examples (Python, VBA), explanation of structural changes to the flatfile CSV format, technical interface description (WADL).
- [Berlin.de: Übersicht der Erhaltungsgebiete (Mitte)](https://www.berlin.de/ba-mitte/politik-und-verwaltung/aemter/stadtentwicklungsamt/stadtplanung/staedtebaufoerderung/erhaltungsgebiete/uebersicht-der-erhaltungsgebiete-1393066.php)  
    Contacts for property owners and developers: If your property is located in a social conservation area (Milieuschutzgebiet), get in touch with the responsible caseworkers. This ensures your planning is legally secure. We answer your questions and support your planning process for a smooth implementation.

## Data Transformation Plan

**1. Key Parameters/Columns:**
- Select columns such as street name, district (Bezirk), area name (Gebietsname), and any unique identifiers relevant to the use case.

**2. Data Connections:**
- Link data to existing tables using coordinates, district names, or neighborhood codes to enable spatial joins and enrich analysis.

**3. Planned Schema:**
- Draft a new table schema with fields: `id`, `street_name`, `district`, `area_name`, `coordinates`, and any additional attributes needed for the project.

**4. Known Data Issues:**
- Possible inconsistencies in street naming conventions
- Missing or incomplete coordinate data
- Duplicate entries or overlapping areas

**5. Transformation Steps:**
- Clean and standardize street and district names
- Normalize area names and codes
- Remove duplicates and handle missing values
- Structure the data to match the planned schema
- Validate connections to existing tables (spatial and tabular)

_This plan will guide the cleaning, normalization, and integration of the latest dataframe into the project database for further analysis._
