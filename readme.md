
# Crime Statistics in Berlin - Data Sources

## Overview

This directory contains all raw data files and documentation for integrating Berlin crime statistics into our database. The data layer focuses on providing comprehensive crime and safety metrics to enrich property listings and neighborhood analysis.

## Data Sources Used

### 1. Berlin Crime Atlas (Primary Source)
- **File**: `crime_atlas/kriminalitaetsatlas_2014-2023.xlsx`
- **Source**: Berlin Police Department via Berlin Open Data Portal
- **URL**: https://daten.berlin.de/datensaetze/kriminalitatsatlas-berlin
- **License**: Creative Commons Attribution Share-Alike (cc-by-sa)
- **Update Frequency**: Biennial (every 2 years)
- **Coverage**: 2014-2023, 12 districts, 138 district regions
- **Crime Types**: 17 categories including street robbery, bike theft, drug crimes, burglary
- **Data Format**: XLSX with absolute cases and frequency per 100,000 inhabitants

### 2. Berlin Fire Department Emergency Data (Secondary Source)
- **Files**: `emergency_services/bf_mission_data_daily.csv`, `emergency_services/bf_calls_data.csv`
- **Source**: Berlin Fire Brigade Open Data Repository
- **URL**: https://github.com/Berliner-Feuerwehr/BF-Open-Data
- **License**: Creative Commons Attribution 4.0 International
- **Update Frequency**: Daily updates
- **Coverage**: Emergency calls, response times, incident types, service quality metrics
- **Data Format**: CSV files with timestamped incident data

### 3. Berlin Demographics and Spatial Data (Supporting Source)
- **Files**: `demographics/berlin_population_lor.csv`, `spatial_data/LOR_areas.geojson`
- **Source**: Berlin Statistical Office via Open Data Portal
- **URL**: https://daten.berlin.de (multiple datasets)
- **Update Frequency**: Annual
- **Coverage**: Population, demographics, LOR spatial boundaries
- **Data Format**: CSV and GeoJSON

### 4. Historical Reference Data
- **File**: `historical/crime_berlin_2012-2019.csv`
- **Source**: Kaggle community dataset
- **URL**: https://www.kaggle.com/datasets/danilzyryanov/crime-in-berlin-2012-2019
- **Purpose**: Historical validation and trend analysis
- **Data Format**: CSV

## Planned Transformation Steps

### Phase 1: Data Cleaning and Standardization
1. **Coordinate System Normalization**
   - Convert all spatial data to EPSG:4326 (WGS84)
   - Validate coordinate accuracy through spot checks
   - Generate centroids for areas without explicit coordinates

2. **Crime Type Classification**
   - Translate German crime categories to English
   - Standardize crime type naming conventions
   - Map to consistent taxonomy across datasets

3. **Spatial Unit Harmonization**
   - Reconcile LOR areas with existing neighborhood boundaries
   - Create mapping tables between different spatial systems
   - Validate geographic relationships

### Phase 2: Data Integration and Enrichment
1. **Temporal Alignment**
   - Handle biennial crime data gaps through interpolation
   - Align demographic snapshots with crime reporting periods
   - Create consistent time series data

2. **Metric Calculation**
   - Generate safety scores and risk indicators
   - Calculate population-weighted crime rates
   - Create neighborhood-level aggregations

3. **Quality Assurance**
   - Validate population figures against official statistics
   - Cross-reference crime patterns with known factors
   - Test spatial join accuracy

### Phase 3: Database Integration
1. **Schema Implementation**
   - Create tables for crime statistics, emergency services, demographics
   - Establish foreign key relationships with existing neighborhood/listing tables
   - Implement spatial indexes for performance

2. **Data Loading**
   - Bulk insert cleaned and validated data
   - Create update mechanisms for dynamic data sources
   - Implement data versioning for historical tracking

## Data Quality Considerations

### Known Issues
- **Temporal Gaps**: Crime atlas published every 2 years, requiring interpolation
- **Spatial Complexity**: Multiple overlapping geographic unit systems
- **Language Barriers**: Original data in German requires translation
- **Privacy Constraints**: Emergency location data may have accuracy limitations

### Mitigation Strategies
- Use demographic data to validate population-based calculations
- Cross-reference multiple spatial datasets for boundary accuracy
- Implement data quality flags for interpolated vs. actual values
- Document assumptions and limitations clearly

## File Structure
sources/
├── README.md                           # This file
├── crime_atlas/
│   ├── kriminalitaetsatlas_2014-2023.xlsx
│   ├── metadata.json
│   └── data_dictionary.md
├── emergency_services/
│   ├── bf_mission_data_daily.csv
│   ├── bf_calls_data.csv
│   └── schema_documentation.md
├── demographics/
│   ├── berlin_population_lor_2023.csv
│   ├── migration_background_2023.csv
│   └── age_distribution_2023.csv
├── spatial_data/
│   ├── LOR_bezirksregionen.geojson
│   ├── berlin_districts.geojson
│   └── coordinate_mappings.csv
└── historical/
├── crime_berlin_2012-2019.csv
└── validation_dataset.csv

## Next Steps

1. **Download Data Files** - Fetch all identified datasets from source URLs
2. **Data Quality Assessment** - Analyze structure, completeness, and accuracy
3. **Schema Validation** - Confirm database design matches actual data structure
4. **Transformation Scripts** - Develop Python/SQL scripts for data processing
5. **Testing** - Validate data integrity and spatial relationships

## Contact and Support

For questions about data sources or transformation approach:
- Review Berlin Open Data Portal documentation
- Consult Berlin Police Crime Atlas methodology notes
- Reference LOR spatial unit definitions from Berlin Statistical Office

Last Updated: $(date +%Y-%m-%d)
Data Collection Status: In Progress - Phase 1 (Research & Modeling)
