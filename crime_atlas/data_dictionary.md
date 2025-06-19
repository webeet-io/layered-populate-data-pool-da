# Berlin Crime Statistics Data Dictionary

## Crime Atlas Data (crime_atlas/kriminalitaetsatlas_2014-2023.xlsx)

### Expected Columns:
- **Bezirk** (District): Berlin district name (e.g., "Mitte", "Charlottenburg-Wilmersdorf")
- **Bezirksregion** (District Region): Sub-district area name
- **RAUMID**: Unique area identifier (7-digit LOR code)
- **Delikt** (Crime Type): German crime category name
- **Jahr** (Year): Year of data (2014-2023)
- **Fallzahl** (Case Count): Absolute number of reported cases
- **Häufigkeitszahl** (Frequency Number): Cases per 100,000 inhabitants
- **EinwohnerInnen** (Residents): Population base for calculation

### Crime Types (German → English):
- Diebstahl → Theft
- Straßenraub → Street Robbery  
- Wohnungseinbruch → Residential Burglary
- Fahrraddiebstahl → Bicycle Theft
- Rauschgiftdelikte → Drug Crimes
- Sachbeschädigung → Property Damage
- Körperverletzung → Assault
- Betrug → Fraud

## Emergency Services Data (emergency_services/)

### Daily Mission Data (bf_mission_data_daily.csv):
- **Date**: Date of incidents
- **Total_Missions**: Total emergency calls
- **Fire_Missions**: Fire-related emergencies
- **Medical_Missions**: Medical emergencies
- **Technical_Missions**: Technical assistance calls
- **Avg_Response_Time**: Average response time in minutes
- **Units_Deployed**: Total emergency units dispatched

### Call Data (bf_calls_data_daily.csv):
- **Timestamp**: Date and time of emergency call
- **Call_Type**: Type of emergency (Fire/Medical/Technical)
- **Response_Time**: Time to first unit arrival (minutes)
- **Location_Anonymized**: Anonymized location information
- **Severity**: Incident severity level
- **Outcome**: Resolution status

## Demographics Data (demographics/)

### Population by LOR (berlin_population_lor_2023.csv):
- **RAUMID**: LOR area identifier (matches crime data)
- **Raumname**: Area name
- **EW_Gesamt**: Total population
- **EW_Dichte**: Population density per km²
- **EW_0_17**: Population aged 0-17
- **EW_18_64**: Population aged 18-64
- **EW_65_Plus**: Population aged 65+

### Migration Background (migration_background_2023.csv):
- **RAUMID**: LOR area identifier
- **MigHint_Gesamt**: Total with migration background
- **MigHint_Anteil**: Percentage with migration background
- **EU_Auslaender**: EU citizens
- **NichtEU_Auslaender**: Non-EU citizens

## Spatial Data (spatial_data/)

### LOR District Regions (LOR_bezirksregionen.geojson):
GeoJSON format with features containing:
- **properties.RAUMID**: Area identifier
- **properties.RAUMNAME**: Area name
- **properties.BEZIRK**: Parent district
- **geometry**: Polygon boundaries

### District Boundaries (berlin_districts.geojson):
- **properties.BEZIRK_NAME**: District name
- **properties.BEZIRK_ID**: Numeric district ID (1-12)
- **geometry**: District polygon boundaries

## Data Quality Notes

### Known Issues:
1. **Missing Years**: Crime atlas data is biennial (gaps need interpolation)
2. **Coordinate Precision**: Emergency locations may be anonymized for privacy
3. **Language**: Original data in German requires translation
4. **Spatial Alignment**: Different datasets may use slightly different boundaries

### Validation Checks:
- Population figures should match between datasets
- RAUMID codes should be consistent across sources
- Geographic boundaries should align properly
- Crime totals should be reasonable (no negative values)

### Processing Notes:
- All coordinates should be converted to EPSG:4326 (WGS84)
- Crime types need standardized English translation
- Areas without data should be flagged, not ignored
- Temporal interpolation needed for missing years
