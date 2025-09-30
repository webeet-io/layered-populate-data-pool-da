# 🎭 Theaters & Cinemas in Berlin — Data Source Discovery

## ⚡ Executive Summary (Day 1)
- **Primary Source**: OpenStreetMap (OSM) data for theaters & cinemas in Berlin.  
- **Supplementary Sources**: Nominatim (addresses), Wikidata (capacity, websites), Wheelmap (accessibility), Berlin Open Data (operators), external review links (Google/Yelp/Tripadvisor).  
- **Baseline Coverage**: Core fields (name, location) nearly complete; metadata fields (opening hours, genre, email) largely missing.  
- **Outcome**: Initial dataset exported (`berlin_theaters.csv`), enrichment pipeline planned with clear next steps.  

---

## 📑 Table of Contents
1. [Objective](#-objective)
2. [Primary Source](#-primary-source)
3. [Supplementary Sources](#-supplementary-sources)
4. [Baseline Coverage](#-baseline-coverage)
5. [Data Dictionary](#-data-dictionary)
6. [Next Steps](#-next-steps)

---

## 🎯 Objective
Identify and document open data sources for theaters and cinemas in Berlin, prepare an initial dataset schema, and outline enrichment opportunities for missing fields.

---
## 📂 Primary Source

### OpenStreetMap (via OSMnx / Overpass)
- **Origin**: [OpenStreetMap](https://www.openstreetmap.org)  
- **Access**: [OSMnx](https://osmnx.readthedocs.io/) / [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)  
- **Query Example**:
    ```python
  import osmnx as ox
  ox.features_from_place("Berlin, Germany", {"amenity": ["theatre", "cinema"]})
- **Update frequency**: Community-updated continuously (live data).
- **Data type**: Dynamic API (JSON/GeoJSON, reproducible queries).
- **Relevant fields**:
  
  * name

  * amenity (theatre, cinema)

  * Address: addr:street, addr:housenumber, addr:postcode, addr:city

  * Contact: phone, contact:phone, website, contact:website, email, contact:email

  * opening_hours

  * Theater/cinema details: theatre:genre, theatre:type, cinema:type

  * Accessibility: wheelchair

  * Geometry → centroid (lat, lon)

  ---

## 📂 Supplementary Sources
### 2. Nominatim (Reverse Geocoding)

- **Origin**: [Nominatim API](https://nominatim.openstreetmap.org/ui/search.html)

- **Update frequency**: Live API (subject to rate limits: 1 req/sec).

- **Data type**: Dynamic reverse geocoding service.

- **Relevant fields**:

* address (enriched from lat/lon)

- **New column(s)**:

* address (completed for missing rows)

  ---

  ### 3. Wikidata

- **Origin**: [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page)
 (linked via wikidata tag in OSM).

- **Update frequency**: Dynamic, community-maintained.

- **Data type**: Queryable via SPARQL endpoint
.

- **Relevant fields**:

* Official website (P856)

* Capacity (P1083)

* Inception / opening date (P571)

* Heritage status (P1435)

- **New column(s)**:

* official_website_wd

* capacity_wd

* inception_wd

  ### 4. Wheelmap API

- **Origin**: [Wheelmap.org API](https://wheelmap.org/api)

- **Update frequency**: Near real-time, crowd-sourced.

- **Data type**: REST API.

- **Relevant fields**:

* Wheelchair accessibility

-**New column(s)**:

* wheelchair_wm (enriched accessibility status)
## 5. Berlin Open Data (Cultural Venues)

- **Origin**: [Daten Berlin Portal](https://daten.berlin.de/)

- **Update frequency**: Static datasets, periodically refreshed.

- **Data type**: CSV/JSON/XML datasets.

- **Relevant fields**:

* Venue registry (addresses, operators)

* Possible ticketing information or categorization

-**New column(s)**:

* operator

* subsidy
  ## 6. External Review & Info Links

- **Origin**: Public search portals (Google, Yelp, Tripadvisor).

- **Update frequency**: Dynamic (live).

- **Data type**: Outbound links (no scraping or paid APIs).

- **Relevant fields**:

* Links to reviews, ratings, price ranges.

-**New column(s)**:

* reviews_url_google

* reviews_url_yelp

* reviews_url_tripadvisor

* Placeholders: price_range, rating, review_count

  ---

  # 📊 Current Observations (OSM Baseline Coverage)

| Field             | Missing % |
| ----------------- | --------- |
| `cinema:type`     | 99.6%     |
| `theatre:type`    | 92.1%     |
| `opening_hours`   | 83.2%     |
| `theatre:genre`   | 81.8%     |
| `email`           | 71.8%     |
| `phone`           | 42.5%     |
| `wheelchair`      | 26.1%     |
| `address`         | 22.1%     |
| `website`         | 17.5%     |
| `name`            | 1.4%      |
| `amenity/lat/lon` | 0.0%      |

---

# 📖 Data Dictionary (Proposed Final Schema)
| Column          | Source(s)         | Description                               |
| --------------- | ----------------- | ----------------------------------------- |
| `name`          | OSM               | Venue name                                |
| `amenity`       | OSM               | Type (`theatre`, `cinema`)                |
| `address`       | OSM / Nominatim   | Street, housenumber, postcode, city       |
| `phone`         | OSM / Berlin Data | Contact number                            |
| `website`       | OSM / Wikidata    | Official website                          |
| `email`         | OSM               | Contact email                             |
| `opening_hours` | OSM / Yelp        | Hours of operation                        |
| `theatre:genre` | OSM               | Type of performances (drama, opera, etc.) |
| `theatre:type`  | OSM               | Stage type (open\_air, etc.)              |
| `cinema:type`   | OSM               | Cinema type (multiplex, IMAX, 3D)         |
| `wheelchair`    | OSM               | Accessibility info                        |
| `wheelchair_wm` | Wheelmap API      | Enriched accessibility                    |
| `capacity_wd`   | Wikidata          | Audience capacity                         |
| `inception_wd`  | Wikidata          | Opening date                              |
| `operator`      | Berlin Open Data  | Operating organization                    |
| `subsidy`       | Berlin Open Data  | Funding/subsidy info                      |
| `reviews_url_*` | External links    | Google/Yelp/Tripadvisor search URLs       |
| `price_range`   | Placeholder       | Ticket pricing range (to be enriched)     |
| `rating`        | Placeholder       | Average rating (to be enriched)           |
| `review_count`  | Placeholder       | Number of reviews (to be enriched)        |
| `lat` / `lon`   | OSM (geometry)    | Coordinates (centroid)                    |
| `source`        | OSM + enrichment  | Data origin                               |
| `last_updated`  | Script timestamp  | ISO datetime of last update               |

---

# ✅ Next Steps

*  Fill missing addresses via Nominatim reverse geocoding.

*  Enrich metadata from Wikidata (capacity, inception, official website).

*  Improve accessibility data using Wheelmap.

*  Add review/search links (Google, Yelp, Tripadvisor) for discovery.

*  Introduce enrichment columns:

   official_website_wd, capacity_wd, inception_wd

   wheelchair_wm

   reviews_url_google, reviews_url_yelp, reviews_url_tripadvisor

   price_range, rating, review_count

*  Clean & deduplicate dataset: drop rows without names/coordinates, normalize phone numbers, remove duplicates.

*  Prepare transformation notebook for integration into the layered DB schema.

---

📁 This file documents potential data sources and their integration paths for the theaters data layer in EPIC 2: Data Foundation & Frontend Context.














  
