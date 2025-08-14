Step 2: Data Transformation – S-Bahn Berlin

This step transforms the cleaned S-Bahn stations dataset so it matches the database schema.

Changes
- Loaded `sources/sbahn_stations_clean.csv` into a DataFrame
- Renamed columns to match `ubahn` schema
- Added placeholder columns for future enrichment
- Reordered columns to match schema
- Performed data quality checks:
  - Validated coordinates
  - Counted total and unique stations
  - Identified duplicate station names
- Saved result as `sources/sbahn_stations_transformed.csv`

Notes
- No database insertion is performed at this stage - as requested
- Duplicate station names are retained for now 
