# Venue Scraper (Multi-City) — Restaurants, Cafes, and Bars

This Python scraper collects structured venue data for restaurants, cafes, and bars using **OpenStreetMap's Overpass API**.  
It is reusable for any city by specifying coordinates and search radius.

---

## Features
- **Multi-city support**: scrape any location by latitude/longitude.
- **Structured output**: saves to both JSON and CSV with consistent schema.
- **Robust**: retries on network failures, logs progress, and handles API errors.
- **Free data source**: no API keys or billing required.

---

## Requirements

- **Python** 3.10+
- Virtual environment recommended

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-org>/layered-populate-data-pool-da.git
   cd layered-populate-data-pool-da
