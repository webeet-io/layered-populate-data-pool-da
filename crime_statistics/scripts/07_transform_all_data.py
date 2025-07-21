
#!/usr/bin/env python3
"""
Complete Crime Atlas Data Transformation
Transforms all years of data with English translations and proper formatting
"""

import pandas as pd
import json
from pathlib import Path

def load_translation_mapping():
    """Load the German-English translation mapping"""
    json_file = Path("transformed_data/crime_type_translations.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    print(f"📋 Loaded translation mapping for {len(mapping)} crime types")
    return mapping

def transform_crime_data(file_path, translation_mapping):
    """Transform all crime data with English translations"""
    
    print("🔄 Transforming All Crime Atlas Data")
    print("=" * 50)
    
    all_transformed_data = []
    
    # Process all years 2015-2024
    years = range(2015, 2025)
    
    for year in years:
        print(f"\n--- Processing Year {year} ---")
        
        # Process both case numbers and frequency data
        for data_type, sheet_prefix in [('cases', 'Fallzahlen'), ('frequency', 'HZ')]:
            sheet_name = f"{sheet_prefix}_{year}"
            
            try:
                print(f"📊 Processing {sheet_name} ({data_type})")
                
                # Read data starting from row 5 (after headers)
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=4)
                
                # Set column names
                df.columns = ['area_id', 'area_name'] + [f'col_{i}' for i in range(2, len(df.columns))]
                
                # Clean data
                df = df.dropna(how='all')
                df = df[df['area_id'].notna()]
                df['area_id'] = df['area_id'].astype(str).str.strip()
                df = df[~df['area_id'].str.contains('LOR-Schlüssel|Unnamed', na=False)]
                
                # Get crime type names from the header row
                header_df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=3, nrows=1)
                crime_names = []
                for i in range(2, len(header_df.columns)):
                    crime_name = str(header_df.iloc[0, i]).replace('\n', ' ').replace('  ', ' ').strip()
                    crime_names.append(crime_name)
                
                # Rename crime columns with actual names
                crime_columns = ['area_id', 'area_name'] + crime_names
                df.columns = crime_columns[:len(df.columns)]
                
                # Transform to long format (one row per area-crime combination)
                id_vars = ['area_id', 'area_name']
                crime_cols = [col for col in df.columns if col not in id_vars]
                
                df_long = pd.melt(df, id_vars=id_vars, value_vars=crime_cols,
                                var_name='crime_type_german', value_name='value')
                
                # Add English translations
                df_long['crime_type_english'] = df_long['crime_type_german'].map(
                    lambda x: translation_mapping.get(x, {}).get('english', x)
                )
                df_long['category'] = df_long['crime_type_german'].map(
                    lambda x: translation_mapping.get(x, {}).get('category', 'Unknown')
                )
                df_long['severity_weight'] = df_long['crime_type_german'].map(
                    lambda x: translation_mapping.get(x, {}).get('severity', 1.0)
                )
                
                # Add metadata
                df_long['year'] = year
                df_long['data_type'] = data_type
                
                # Clean values (convert to numeric, handle errors)
                df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')
                df_long = df_long.dropna(subset=['value'])
                
                print(f"   ✅ Transformed {len(df_long)} records")
                all_transformed_data.append(df_long)
                
            except Exception as e:
                print(f"   ❌ Error processing {sheet_name}: {e}")
                continue
    
    # Combine all data
    if all_transformed_data:
        final_df = pd.concat(all_transformed_data, ignore_index=True)
        
        # Final cleanup and formatting
        final_df = final_df[final_df['value'] >= 0]  # Remove negative values
        
        # Reorder columns
        column_order = [
            'area_id', 'area_name', 'year', 'data_type',
            'crime_type_german', 'crime_type_english', 'category',
            'value', 'severity_weight'
        ]
        final_df = final_df[column_order]
        
        # Sort data
        final_df = final_df.sort_values(['year', 'area_id', 'data_type', 'crime_type_english'])
        
        return final_df
    
    return None

def main():
    file_path = Path("sources/crime_atlas/kriminalitaetsatlas_2015-2024.xlsx")
    output_dir = Path("transformed_data")
    
    # Load translation mapping
    translation_mapping = load_translation_mapping()
    
    # Transform all data
    transformed_df = transform_crime_data(file_path, translation_mapping)
    
    if transformed_df is not None:
        # Save final transformed data
        output_file = output_dir / "berlin_crime_statistics_transformed.csv"
        transformed_df.to_csv(output_file, index=False)
        
        print(f"\n🎉 TRANSFORMATION COMPLETE!")
        print(f"📁 Output: {output_file}")
        print(f"📊 Total records: {len(transformed_df):,}")
        print(f"🗓️ Years: {sorted(transformed_df['year'].unique())}")
        print(f"🏛️ Areas: {transformed_df['area_name'].nunique()}")
        print(f"🚨 Crime types: {transformed_df['crime_type_english'].nunique()}")
        print(f"📋 Data types: {list(transformed_df['data_type'].unique())}")
        
        # Show sample of final data
        print(f"\n📋 Sample of Final Transformed Data:")
        sample_cols = ['area_name', 'year', 'data_type', 'crime_type_english', 'value']
        print(transformed_df[sample_cols].head(10))
        
        # Show data summary by category
        print(f"\n📈 Records by Crime Category:")
        category_counts = transformed_df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"   {category}: {count:,} records")
            
    else:
        print("❌ No data transformed")

if __name__ == "__main__":
    main()
