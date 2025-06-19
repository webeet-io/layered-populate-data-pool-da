
#!/usr/bin/env python3
"""
Berlin Crime Statistics Data Download Script
This script downloads the primary data sources for the crime statistics layer.
Run this during Step 1: Data Modeling phase to populate the sources directory.
"""

import os
import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BerlinDataDownloader:
    def __init__(self, base_dir="sources"):
        self.base_dir = Path(base_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Berlin-Crime-Data-Integration/1.0 (Research Project)'
        })
        
    def create_directories(self):
        """Create the required directory structure"""
        directories = [
            'crime_atlas',
            'emergency_services', 
            'demographics',
            'spatial_data',
            'historical'
        ]
        
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def download_crime_atlas_data(self):
        """Download Berlin Crime Atlas data from Open Data Portal"""
        logger.info("Downloading Berlin Crime Atlas data...")
        
        # Primary URL for the latest crime atlas data
        crime_atlas_url = "https://daten.berlin.de/sites/default/files/adressen/csv/kriminalitaetsatlas_berlin.xlsx"
        
        try:
            response = self.session.get(crime_atlas_url, timeout=30)
            response.raise_for_status()
            
            output_path = self.base_dir / "crime_atlas" / "kriminalitaetsatlas_2014-2023.xlsx"
            with open(output_path, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"Downloaded crime atlas data to: {output_path}")
            
            # Create metadata file
            metadata = {
                "source_url": crime_atlas_url,
                "download_date": datetime.now().isoformat(),
                "file_size_bytes": len(response.content),
                "description": "Berlin Police Crime Statistics Atlas 2014-2023",
                "format": "XLSX",
                "license": "CC-BY-SA",
                "update_frequency": "Biennial"
            }
            
            metadata_path = self.base_dir / "crime_atlas" / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except requests.RequestException as e:
            logger.error(f"Failed to download crime atlas data: {e}")
            # Create placeholder file with instructions
            placeholder_path = self.base_dir / "crime_atlas" / "DOWNLOAD_INSTRUCTIONS.txt"
            with open(placeholder_path, 'w') as f:
                f.write("""
Berlin Crime Atlas Data Download Instructions
===========================================

Automatic download failed. Please manually download from:
https://daten.berlin.de/datensaetze/kriminalitatsatlas-berlin

Steps:
1. Visit the URL above
2. Look for the download link for the Excel/XLSX file
3. Save as: kriminalitaetsatlas_2014-2023.xlsx
4. Place in this directory (sources/crime_atlas/)

Alternative sources:
- Direct portal: https://www.kriminalitaetsatlas.berlin.de/
- Historical data: Check archive sections for previous years
""")
    
    def download_emergency_services_data(self):
        """Download Berlin Fire Department emergency services data"""
        logger.info("Downloading emergency services data...")
        
        # GitHub repository for Berlin Fire Department Open Data
        base_url = "https://raw.githubusercontent.com/Berliner-Feuerwehr/BF-Open-Data/main"
        
        files_to_download = [
            ("Daily_Data/BFw_mission_data_daily.csv", "bf_mission_data_daily.csv"),
            ("Daily_Data/BFw_calls_data_daily.csv", "bf_calls_data_daily.csv"),
            ("Monthly_Data/BFw_mission_data_monthly.csv", "bf_mission_data_monthly.csv")
        ]
        
        for source_file, local_file in files_to_download:
            try:
                url = f"{base_url}/{source_file}"
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                output_path = self.base_dir / "emergency_services" / local_file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                    
                logger.info(f"Downloaded: {local_file}")
                
            except requests.RequestException as e:
                logger.warning(f"Failed to download {source_file}: {e}")
                # Create placeholder
                placeholder_path = self.base_dir / "emergency_services" / f"{local_file}.placeholder"
                with open(placeholder_path, 'w') as f:
                    f.write(f"Download failed for: {url}\nManual download required.")
    
    def download_demographic_data(self):
        """Download demographic and spatial data from Berlin Open Data"""
        logger.info("Downloading demographic data...")
        
        # These are example URLs - actual URLs may vary
        demographic_sources = [
            {
                "url": "https://daten.berlin.de/sites/default/files/adressen/csv/einwohner_nach_lor.csv",
                "filename": "berlin_population_lor_2023.csv",
                "description": "Population by LOR areas"
            },
            {
                "url": "https://daten.berlin.de/sites/default/files/adressen/csv/migration_background.csv", 
                "filename": "migration_background_2023.csv",
                "description": "Population with migration background"
            }
        ]
        
        for source in demographic_sources:
            try:
                response = self.session.get(source["url"], timeout=30)
                response.raise_for_status()
                
                output_path = self.base_dir / "demographics" / source["filename"]
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                    
                logger.info(f"Downloaded: {source['filename']}")
                
            except requests.RequestException as e:
                logger.warning(f"Failed to download {source['filename']}: {e}")
                # Create instructions file
                instructions_path = self.base_dir / "demographics" / f"{source['filename']}.instructions"
                with open(instructions_path, 'w') as f:
                    f.write(f"""
Manual Download Required
=======================
URL: {source['url']}
Description: {source['description']}
Target filename: {source['filename']}

Search Berlin Open Data Portal for demographic datasets:
https://daten.berlin.de/kategorie/bevoelkerung
""")
    
    def download_spatial_data(self):
        """Download Berlin spatial/geographic data"""
        logger.info("Downloading spatial data...")
        
        # LOR boundaries and geographic data
        spatial_sources = [
            {
                "url": "https://daten.berlin.de/sites/default/files/adressen/geojson/lor_bezirksregionen.geojson",
                "filename": "LOR_bezirksregionen.geojson",
                "description": "LOR district regions boundaries"
            },
            {
                "url": "https://daten.berlin.de/sites/default/files/adressen/geojson/bezirksgrenzen.geojson",
                "filename": "berlin_districts.geojson", 
                "description": "Berlin district boundaries"
            }
        ]
        
        for source in spatial_sources:
            try:
                response = self.session.get(source["url"], timeout=30)
                response.raise_for_status()
                
                output_path = self.base_dir / "spatial_data" / source["filename"]
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                    
                logger.info(f"Downloaded: {source['filename']}")
                
                # Validate GeoJSON
                try:
                    import json
                    geojson_data = json.loads(response.text)
                    if geojson_data.get('type') == 'FeatureCollection':
                        logger.info(f"Validated GeoJSON: {len(geojson_data.get('features', []))} features")
                except:
                    logger.warning(f"Could not validate GeoJSON for {source['filename']}")
                    
            except requests.RequestException as e:
                logger.warning(f"Failed to download {source['filename']}: {e}")
                
    def download_historical_data(self):
        """Download historical crime data for validation"""
        logger.info("Downloading historical reference data...")
        
        # Create instructions for Kaggle dataset (requires account)
        instructions_path = self.base_dir / "historical" / "KAGGLE_DOWNLOAD_INSTRUCTIONS.txt"
        with open(instructions_path, 'w') as f:
            f.write("""
Historical Crime Data Download Instructions
==========================================

The historical Berlin crime data (2012-2019) is available on Kaggle:
https://www.kaggle.com/datasets/danilzyryanov/crime-in-berlin-2012-2019

To download:
1. Create a free Kaggle account if you don't have one
2. Visit the URL above
3. Click "Download" to get the CSV file
4. Save as: crime_berlin_2012-2019.csv
5. Place in this directory (sources/historical/)

This data will be used for:
- Historical trend validation
- Data quality cross-checking  
- Model development and testing

File should contain columns like:
- Year, District, Crime Type, Cases, etc.
""")
    
    def create_data_dictionary(self):
        """Create data dictionary documentation"""
        logger.info("Creating data dictionary...")
        
        data_dict_content = """# Berlin Crime Statistics Data Dictionary

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
"""

        dict_path = self.base_dir / "crime_atlas" / "data_dictionary.md"
        with open(dict_path, 'w', encoding='utf-8') as f:
            f.write(data_dict_content)
            
        logger.info(f"Created data dictionary: {dict_path}")
    
    def run_download(self):
        """Execute the complete download process"""
        logger.info("Starting Berlin crime statistics data download...")
        
        # Create directory structure
        self.create_directories()
        
        # Download all data sources
        self.download_crime_atlas_data()
        self.download_emergency_services_data()
        self.download_demographic_data()
        self.download_spatial_data()
        self.download_historical_data()
        
        # Create documentation
        self.create_data_dictionary()
        
        # Create summary report
        self.create_download_report()
        
        logger.info("Download process completed!")
    
    def create_download_report(self):
        """Create a summary report of downloaded files"""
        report_content = f"""# Berlin Crime Statistics - Data Download Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Download Summary

### Files Successfully Downloaded:
"""
        
        # Check which files exist
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if not file.startswith('.') and not file.endswith('.placeholder'):
                    file_path = Path(root) / file
                    file_size = file_path.stat().st_size
                    relative_path = file_path.relative_to(self.base_dir)
                    report_content += f"- {relative_path} ({file_size:,} bytes)\n"
        
        report_content += """
### Next Steps:
1. Review downloaded files for completeness
2. Run data quality validation scripts
3. Begin transformation script development
4. Update database schema based on actual data structure

### Data Quality Checklist:
- [ ] Crime atlas XLSX file opens correctly
- [ ] Emergency services CSV files have valid structure
- [ ] GeoJSON files are valid and have expected properties
- [ ] Demographic data matches expected LOR structure
- [ ] All RAUMID codes are consistent across datasets

### Known Manual Downloads Required:
- Historical Kaggle dataset (requires account)
- Any files marked with .placeholder extension
- Additional demographic datasets from Berlin Open Data Portal
"""
        
        report_path = self.base_dir / "download_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logger.info(f"Created download report: {report_path}")

def main():
    """Main execution function"""
    downloader = BerlinDataDownloader()
    downloader.run_download()

if __name__ == "__main__":
    main()
