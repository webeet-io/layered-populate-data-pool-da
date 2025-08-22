"""
Smart Auto DataLoader
=====================================

Fully automated data loader implementing manager requirements:
- CSV/TSV: 95% priority (CRITICAL)
- Excel: 80% priority (HIGH)  
- JSON: 70% priority (MEDIUM)

Features:
- Universal loading with auto-delegation
- Automatic format, encoding, and parameter detection
- Comprehensive datetime parsing
- Performance monitoring and reporting
- Error handling with fallback strategies

Author: Generated from user requirements
"""

import re
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    import pandas as pd

@dataclass 
class LoadReport:
    """Comprehensive loading report as per README requirements"""
    file_path: str
    file_size_mb: float
    detected_format: str  # CSV/Excel/JSON (manager priorities: 95%/80%/70%)
    detected_encoding: str
    detected_delimiter: str
    has_header: bool
    total_rows: int
    total_columns: int
    column_info: Dict[str, str]
    date_columns_found: List[str]
    date_formats_detected: Dict[str, str]
    loading_time_seconds: float
    quality_score: int  # 0-100 as mentioned in README
    warnings: List[str]
    errors: List[str]
    success: bool

class SmartAutoDataLoader:
    """
    🎯 Smart Auto DataLoader - Implements README requirements
    
    Manager Requirements Implementation:
    ✅ Loading Functions (5): load(), load_csv(), load_excel(), load_json(), parse_datetimes()
    ✅ Detection Functions (3): detect_format(), detect_encoding(), sniff_csv_params() 
    ✅ Performance (1): estimate_memory_usage()
    ✅ Reporting & Error Handling (2): build_report(), detect_time_columns()
    
    Architecture: Unified Interface with Format-Specific Delegation
    - CSV/TSV: 95% priority (CRITICAL)
    - Excel: 80% priority (HIGH)  
    - JSON: 70% priority (MEDIUM)
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize Smart Auto DataLoader
        
        Args:
            verbose: Enable detailed logging (manager requirement)
        """
        self.verbose = verbose
        
        # Date patterns for automatic detection (manager priority)
        self.date_patterns = [
            (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d'),      # ISO format
            (r'\d{2}/\d{2}/\d{4}', '%d/%m/%Y'),      # EU format  
            (r'\d{2}\.\d{2}\.\d{4}', '%d.%m.%Y'),    # German format
            (r'\d{2}-\d{2}-\d{4}', '%d-%m-%Y'),      # UK format
            (r'\d{4}/\d{2}/\d{2}', '%Y/%m/%d'),      # US format
        ]
        
        if self.verbose:
            print("🎯 SmartAutoDataLoader ready!")
    
    # =================================================================
    # LOADING FUNCTIONS (5 methods - Manager Requirements)
    # =================================================================
    
    def load(self, source: str, **kwargs) -> 'pd.DataFrame':
        """
        1/5 Universal loading with auto-delegation (README: main method)
        
        Auto-detects format and delegates to appropriate specialist:
        - CSV/TSV → load_csv() (95% priority - CRITICAL)
        - Excel → load_excel() (80% priority - HIGH)
        - JSON → load_json() (70% priority - MEDIUM)
        """
        import pandas as pd
        
        start_time = time.time()
        path = Path(source)
        
        if self.verbose:
            print(f"🎯 Loading file: {Path(source).name}")
        
        # Auto-detect format and delegate (README requirement)
        detected_format = self.detect_format(source)
        
        if detected_format in ['csv', 'tsv']:
            return self.load_csv(source, **kwargs)
        elif detected_format == 'excel':
            return self.load_excel(source, **kwargs)
        elif detected_format == 'json':
            return self.load_json(source, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Supported formats are: csv, excel, json.")
    
    def load_csv(self, source: str, **kwargs) -> 'pd.DataFrame':
        """
        2/5 CSV loading with smart detection (README: 95% priority - CRITICAL)
        
        Implements CsvLoader functionality with:
        - Automatic encoding detection (manager priority)
        - Automatic delimiter detection (manager priority)
        - Parameter sniffing (README requirement)
        """
        import pandas as pd
        
        if self.verbose:
            print(f"📊 Loading CSV file...")
        
        path = Path(source)
        
        # Auto-detect encoding (README: CRITICAL for CSV)
        encoding = self.detect_encoding(source)
        
        # Auto-detect CSV parameters (README: sniff_csv_params)
        delimiter = self._sniff_delimiter(path, encoding)
        
        # Load with detected parameters
        df = pd.read_csv(source, encoding=encoding, sep=delimiter)
        
        # Auto-detect and parse datetimes (manager requirement)
        df = self.parse_datetimes(df)
        
        if self.verbose:
            print(f"✅ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        
        return df
    
    def load_excel(self, source: str, **kwargs) -> 'pd.DataFrame':
        """
        3/5 Excel loading with smart detection (README: 80% priority - HIGH)
        
        Implements ExcelLoader functionality with:
        - Sheet selection and detection (README requirement)
        - Auto-delegation from unified interface
        """
        import pandas as pd
        
        if self.verbose:
            print(f"📈 Loading Excel file...")
        
        try:
            # Check if file exists
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Excel file not found: {source}")
            
            # Get sheet name from kwargs or detect best sheet
            sheet_name = kwargs.get('sheet_name', None)
            
            if sheet_name is None:
                # Auto-detect best sheet (README: sheet selection)
                xl_file = pd.ExcelFile(source)
                sheet_names = xl_file.sheet_names
                
                if self.verbose:
                    print(f"   📋 Available sheets: {sheet_names}")
                
                # Use first sheet or find the largest one
                if len(sheet_names) == 1:
                    sheet_name = sheet_names[0]
                else:
                    # Find sheet with most data
                    max_rows = 0
                    best_sheet = sheet_names[0]
                    
                    for sheet in sheet_names:
                        try:
                            temp_df = pd.read_excel(source, sheet_name=sheet, nrows=1)
                            if len(temp_df.columns) > max_rows:
                                max_rows = len(temp_df.columns)
                                best_sheet = sheet
                        except:
                            continue
                    
                    sheet_name = best_sheet
                
                if self.verbose:
                    print(f"   ✅ Selected sheet: '{sheet_name}'")
            
            # Load Excel with selected sheet
            df = pd.read_excel(source, sheet_name=sheet_name, **{k: v for k, v in kwargs.items() if k != 'sheet_name'})
            
            # Check if DataFrame is empty
            if df.empty:
                if self.verbose:
                    print("   ⚠️ Warning: Excel file loaded but DataFrame is empty")
                return df
            
            # Auto-detect and parse datetimes
            df = self.parse_datetimes(df)
            
            if self.verbose:
                print(f"✅ Excel loaded: {len(df)} rows, {len(df.columns)} columns")
                print(f"   📊 Column names: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            error_msg = f"Error loading Excel file: {str(e)}"
            if self.verbose:
                print(f"❌ {error_msg}")
            raise ValueError(error_msg)
    
    def load_json(self, source: str, auto_deep_flatten: bool = True, **kwargs) -> 'pd.DataFrame':
        """
        4/5 JSON loading with smart detection (README: 70% priority - MEDIUM)
        
        Implements intelligent JSON loading with:
        - Automatic structure analysis
        - Smart flattening decision
        - Deep nested extraction
        - Comprehensive reporting
        
        Args:
            source: JSON file path
            auto_deep_flatten: Automatically analyze and apply deep flattening if beneficial
            **kwargs: Additional parameters
        """
        import pandas as pd
        import json
        
        if self.verbose:
            print(f"🗂️ Loading JSON file with intelligent analysis...")
        
        try:
            # Load raw JSON data first
            with open(source, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if self.verbose:
                print(f"   📋 JSON structure analysis:")
                print(f"   Type: {type(json_data)}")
                if isinstance(json_data, dict):
                    print(f"   Keys: {list(json_data.keys())}")
                elif isinstance(json_data, list):
                    print(f"   List length: {len(json_data)}")
                    if json_data and isinstance(json_data[0], dict):
                        print(f"   First item keys: {list(json_data[0].keys())}")
            
            # Phase 1: Standard flattening
            df_standard = pd.json_normalize(json_data, sep='_', max_level=None)
            
            if self.verbose:
                print(f"   📊 Standard flattening: {df_standard.shape}")
            
            # Phase 2: Intelligent analysis for deep flattening
            if auto_deep_flatten:
                complexity_score = self._analyze_json_complexity(json_data)
                
                if self.verbose:
                    print(f"   🧠 Complexity analysis: {complexity_score}")
                
                # Apply deep flattening if complex nested structure detected
                if complexity_score['needs_deep_flattening']:
                    if self.verbose:
                        print(f"   🔍 Applying deep flattening...")
                    
                    df_deep = self._smart_deep_flatten_json(json_data)
                    
                    # Compare results and choose best
                    improvement_ratio = len(df_deep.columns) / len(df_standard.columns)
                    
                    if self.verbose:
                        print(f"   📊 Deep flattening: {df_deep.shape}")
                        print(f"   📈 Improvement: {improvement_ratio:.1f}x more columns")
                    
                    # Use deep flattening if significant improvement (>2x columns)
                    if improvement_ratio > 2.0:
                        df = df_deep
                        if self.verbose:
                            print(f"   ✅ Using deep flattening (better data extraction)")
                    else:
                        df = df_standard
                        if self.verbose:
                            print(f"   ✅ Using standard flattening (minimal benefit from deep)")
                else:
                    df = df_standard
                    if self.verbose:
                        print(f"   ✅ Using standard flattening (simple structure)")
            else:
                df = df_standard
                if self.verbose:
                    print(f"   ✅ Using standard flattening (auto analysis disabled)")
            
            # Auto-detect and parse datetimes
            df = self.parse_datetimes(df)
            
            if self.verbose:
                print(f"✅ JSON loaded: {len(df)} rows, {len(df.columns)} columns")
                if len(df.columns) <= 15:
                    print(f"   📊 Columns: {list(df.columns)}")
                else:
                    print(f"   📊 First 10 columns: {list(df.columns[:10])}... (+{len(df.columns)-10} more)")
            
            return df
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Error loading JSON: {e}")
                import traceback
                traceback.print_exc()
            # Fallback to pandas default JSON loading
            try:
                df = pd.read_json(source, **kwargs)
                df = self.parse_datetimes(df)
                return df
            except:
                # Final fallback - return empty DataFrame
                return pd.DataFrame()

    def load_json_as_tables(self, source: str) -> Dict[str, 'pd.DataFrame']:
        """
        Load JSON and return all extracted relational tables
        
        Args:
            source: JSON file path
            
        Returns:
            Dictionary of table_name -> DataFrame
        """
        import json
        
        if self.verbose:
            print(f"🗂️ Loading JSON as relational tables...")
        
        try:
            with open(source, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            tables = self._extract_relational_tables(json_data)
            
            # Apply datetime parsing to all tables
            for table_name, df in tables.items():
                tables[table_name] = self.parse_datetimes(df)
            
            if self.verbose:
                print(f"✅ Extracted {len(tables)} tables:")
                for table_name, df in tables.items():
                    print(f"   📊 {table_name}: {len(df)} rows, {len(df.columns)} columns")
            
            return tables
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Error extracting tables: {e}")
            return {}

    def _extract_relational_tables(self, json_data: Any) -> Dict[str, 'pd.DataFrame']:
        """
        Extract relational tables from complex JSON structures
        
        Args:
            json_data: JSON data to process
            
        Returns:
            Dict of table_name -> DataFrame
        """
        import pandas as pd
        
        tables = {}
        
        if not isinstance(json_data, list):
            if isinstance(json_data, dict):
                # Look for arrays within the dict
                for key, value in json_data.items():
                    if isinstance(value, list) and value:
                        json_data = value
                        break
                else:
                    json_data = [json_data]
            else:
                return tables
        
        if not json_data:
            return tables
        
        # Main table - extract non-list fields
        main_rows = []
        nested_collections = {}
        
        for item in json_data:
            if not isinstance(item, dict):
                continue
                
            main_row = {}
            item_id = item.get('id') or item.get('refId') or len(main_rows)
            
            for key, value in item.items():
                if isinstance(value, list) and value:
                    # Store nested arrays for separate tables
                    if key not in nested_collections:
                        nested_collections[key] = []
                    
                    for nested_item in value:
                        if isinstance(nested_item, dict):
                            nested_item_copy = nested_item.copy()
                            nested_item_copy['parent_id'] = item_id
                            nested_collections[key].append(nested_item_copy)
                else:
                    # Add to main table
                    main_row[key] = value
            
            if main_row:
                main_rows.append(main_row)
        
        # Create main table
        if main_rows:
            tables['main'] = pd.DataFrame(main_rows)
        
        # Create nested tables
        for collection_name, collection_items in nested_collections.items():
            if collection_items:
                table_name = self._normalize_table_name(collection_name)
                
                # Process nested items for further nesting
                processed_items, sub_tables = self._process_nested_collection(collection_items, table_name)
                
                if processed_items:
                    tables[table_name] = pd.DataFrame(processed_items)
                
                # Add sub-tables
                tables.update(sub_tables)
        
        # Extract special structures (like dropdown options)
        special_tables = self._extract_special_structures(tables)
        tables.update(special_tables)
        
        return tables

    def _process_nested_collection(self, items: List[Dict], parent_name: str) -> Tuple[List[Dict], Dict[str, 'pd.DataFrame']]:
        """
        Process nested collection items and extract further nested structures
        
        Args:
            items: List of dictionary items
            parent_name: Name of parent table
            
        Returns:
            Tuple of (processed_items, sub_tables)
        """
        import pandas as pd
        
        processed_items = []
        sub_collections = {}
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            processed_item = {}
            item_id = item.get('id') or item.get('refId')
            
            for key, value in item.items():
                if isinstance(value, list) and value:
                    # Handle further nested arrays
                    if key not in sub_collections:
                        sub_collections[key] = []
                    
                    for sub_item in value:
                        if isinstance(sub_item, dict):
                            sub_item_copy = sub_item.copy()
                            sub_item_copy['parent_id'] = item_id
                            sub_collections[key].append(sub_item_copy)
                else:
                    processed_item[key] = value
            
            if processed_item:
                processed_items.append(processed_item)
        
        # Create sub-tables
        sub_tables = {}
        for sub_name, sub_items in sub_collections.items():
            if sub_items:
                sub_table_name = f"{parent_name}_{self._normalize_table_name(sub_name)}"
                sub_tables[sub_table_name] = pd.DataFrame(sub_items)
        
        return processed_items, sub_tables

    def _extract_special_structures(self, tables: Dict[str, 'pd.DataFrame']) -> Dict[str, 'pd.DataFrame']:
        """
        Extract special structures like dropdown options, arrays, etc.
        
        Args:
            tables: Existing tables dictionary
            
        Returns:
            Dictionary of special tables
        """
        import pandas as pd
        import ast
        
        special_tables = {}
        
        for table_name, df in tables.items():
            # Extract dropdown options
            if 'dropdownOptions' in df.columns:
                dropdown_rows = []
                
                for idx, row in df.iterrows():
                    try:
                        options = row.get('dropdownOptions')
                        if isinstance(options, str) and options.strip():
                            parsed = ast.literal_eval(options)
                            if isinstance(parsed, list):
                                for opt in parsed:
                                    if isinstance(opt, dict):
                                        dropdown_rows.append({
                                            'parent_id': row.get('id'),
                                            'option_value': opt.get('value'),
                                            'option_label': opt.get('label')
                                        })
                    except:
                        continue
                
                if dropdown_rows:
                    special_tables[f"{table_name}_dropdown_options"] = pd.DataFrame(dropdown_rows)
        
        return special_tables

    def _normalize_table_name(self, name: str) -> str:
        """
        Normalize table names for database compatibility
        
        Args:
            name: Original name
            
        Returns:
            Normalized name
        """
        if not name:
            return "unnamed"
        
        import re
        
        # Convert German umlauts and special characters
        replacements = {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
            'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'
        }
        
        for char, replacement in replacements.items():
            name = name.replace(char, replacement)
        
        # Replace spaces and special characters with underscores
        name = re.sub(r'[^\w]', '_', name.lower())
        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        
        return name

    def build_report(self, source: str, df: Optional['pd.DataFrame'] = None) -> LoadReport:
        """
        Comprehensive reporting (README requirement)
        
        Returns detailed load report as specified in README
        """
        import pandas as pd
        
        path = Path(source)
        start_time = time.time()
        
        # Load data if not provided
        if df is None:
            try:
                df = self.load(source)
                loading_time = time.time() - start_time
                success = True
                errors = []
                warnings = []
            except Exception as e:
                loading_time = time.time() - start_time
                success = False
                errors = [str(e)]
                warnings = []
                df = pd.DataFrame()  # Empty DataFrame for failed loads
        else:
            loading_time = 0
            success = True
            errors = []
            warnings = []
        
        # Detect date columns and formats
        date_columns_found = self.detect_time_columns(df)
        date_formats_detected = {}
        
        for col in date_columns_found:
            if 'datetime' in str(df[col].dtype).lower():
                date_formats_detected[col] = str(df[col].dtype)
        
        # Build column info
        column_info = {}
        for col in df.columns:
            column_info[col] = str(df[col].dtype)
        
        # Calculate quality score
        quality_score = 100
        if errors:
            quality_score -= 50
        if warnings:
            quality_score -= len(warnings) * 10
        if df.empty:
            quality_score = 0
        
        quality_score = max(0, min(100, quality_score))
        
        report = LoadReport(
            file_path=str(source),
            file_size_mb=path.stat().st_size / (1024 * 1024) if path.exists() else 0,
            detected_format=self.detect_format(source),
            detected_encoding=self.detect_encoding(source) if self.detect_format(source) == 'csv' else 'N/A',
            detected_delimiter=self._sniff_delimiter(path, self.detect_encoding(source)) if self.detect_format(source) == 'csv' else 'N/A',
            has_header=len(df.columns) > 0 and not df.columns[0].startswith('Unnamed'),
            total_rows=len(df),
            total_columns=len(df.columns),
            column_info=column_info,
            date_columns_found=date_columns_found,
            date_formats_detected=date_formats_detected,
            loading_time_seconds=loading_time,
            quality_score=quality_score,
            warnings=warnings,
            errors=errors,
            success=success
        )
        
        if self.verbose:
            print(f"📊 Report generated for {path.name}")
        
        return report
    
    def detect_time_columns(self, df: 'pd.DataFrame') -> List[str]:
        """
        Time column detection (README requirement)
        
        Returns list of columns containing datetime data
        """
        time_columns = []
        
        for col in df.columns:
            if 'datetime' in str(df[col].dtype).lower():
                time_columns.append(col)
        
        if self.verbose:
            if time_columns:
                print(f"🕒 Found {len(time_columns)} datetime columns: {time_columns}")
            else:
                print("🕒 No datetime columns found")
        
        return time_columns
    
    # =================================================================
    # DETECTION FUNCTIONS (3 methods - Manager Requirements)
    # =================================================================
    
    def detect_format(self, source: str) -> str:
        """
        1/3 Format detection 
        
        Returns: 'csv' (95%), 'excel' (80%), 'json' (70%)
        """
        path = Path(source)
        suffix = path.suffix.lower()
        
        # Manager priority mapping
        format_map = {
            '.csv': 'csv',    # 95% priority - CRITICAL
            '.tsv': 'csv',    # 95% priority - CRITICAL  
            '.txt': 'csv',    # 95% priority - CRITICAL
            '.xlsx': 'excel', # 80% priority - HIGH
            '.xls': 'excel',  # 80% priority - HIGH
            '.json': 'json'   # 70% priority - MEDIUM
        }
        
        detected = format_map.get(suffix, 'csv')  # Default to CSV (95% priority)
        
        if self.verbose:
            print(f"🔍 Format detected: {detected}")
        
        return detected
    
    def detect_encoding(self, source: str) -> str:
        """
        2/3 Encoding detection (README: CRITICAL for CSV)
        
        Manager priority: Essential for 95% critical CSV format
        """
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-8-sig', 'utf-32', 'utf-8-sig', 'utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-16-be']
        
        for encoding in encodings_to_try:
            try:
                with open(source, 'r', encoding=encoding) as f:
                    f.read(1024)  # Test read
                
                if self.verbose:
                    print(f"🔤 Encoding detected: {encoding}")
                
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Fallback
    
    def sniff_csv_params(self, source: str) -> Dict[str, Any]:
        """
        3/3 CSV parameter sniffing (README requirement)
        
        Returns detected CSV parameters for 95% critical format
        """
        encoding = self.detect_encoding(source)
        delimiter = self._sniff_delimiter(Path(source), encoding)
        
        params = {
            'delimiter': delimiter,
            'encoding': encoding,
            'has_header': True  # Simplified for demo
        }
        
        if self.verbose:
            print(f"📋 CSV parameters: delimiter='{delimiter}', encoding={encoding}")
        
        return params
    
    # =================================================================
    # PERFORMANCE & REPORTING (3 methods - Manager Requirements)
    # =================================================================
    
    def estimate_memory_usage(self, source: str) -> Dict[str, float]:
        """
        Performance method (README requirement)
        
        Memory estimation before loading
        """
        file_size = Path(source).stat().st_size / (1024 * 1024)  # MB
        estimated_memory = file_size * 2.5  # Rough estimation
        
        estimate = {
            'file_size_mb': file_size,
            'estimated_memory_mb': estimated_memory,
            'recommended_chunksize': 10000 if estimated_memory > 100 else None
        }
        
        if self.verbose:
            print(f"💾 File size: {file_size:.1f}MB, estimated memory: {estimated_memory:.1f}MB")
        
        return estimate
    
    # =================================================================
    # HELPER METHODS (Internal)
    # =================================================================
    
    def _sniff_delimiter(self, path: Path, encoding: str) -> str:
        """Internal: Sniff CSV delimiter"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                first_line = f.readline()
            
            delimiters = [',', ';', '\t', '|']
            counts = {d: first_line.count(d) for d in delimiters}
            return max(counts, key=counts.get) if max(counts.values()) > 0 else ','
        except:
            return ','
    
    def _flatten_json_to_dataframe(self, data: Any) -> 'pd.DataFrame':
        """
        Enhanced JSON flattening that handles complex nested structures
        
        Args:
            data: JSON data (dict, list, or other)
            
        Returns:
            pd.DataFrame: Flattened data
        """
        import pandas as pd
        
        if isinstance(data, list):
            # Handle list of objects
            if not data:
                return pd.DataFrame()
            
            # Check if all items are dictionaries
            if all(isinstance(item, dict) for item in data):
                # Flatten each dictionary and combine
                flattened_list = []
                for item in data:
                    flattened_item = self._flatten_dict(item)
                    flattened_list.append(flattened_item)
                return pd.DataFrame(flattened_list)
            else:
                # Mixed types or simple list
                return pd.DataFrame({'value': data})
        
        elif isinstance(data, dict):
            # Handle dictionary structure
            # Check if it looks like a records format
            if self._is_records_format(data):
                # Extract the actual data array
                data_key = self._find_data_key(data)
                if data_key and isinstance(data[data_key], list):
                    if self.verbose:
                        print(f"   🔍 Found records format with data key: '{data_key}'")
                    return self._flatten_json_to_dataframe(data[data_key])
            
            # Flatten the dictionary
            flattened = self._flatten_dict(data)
            return pd.DataFrame([flattened])
        
        else:
            # Single value
            return pd.DataFrame({'value': [data]})
    
    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '_') -> dict:
        """
        Recursively flatten a nested dictionary
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested structure
            sep: Separator for nested keys
            
        Returns:
            dict: Flattened dictionary
        """
        items = []
        
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                # Recursively flatten nested dictionaries
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Handle lists
                if v and all(isinstance(item, dict) for item in v):
                    # List of dictionaries - create multiple columns
                    for i, item in enumerate(v):
                        list_key = f"{new_key}_{i}"
                        items.extend(self._flatten_dict(item, list_key, sep=sep).items())
                elif v and all(isinstance(item, (str, int, float, bool)) for item in v):
                    # List of simple values - join as string
                    items.append((new_key, ', '.join(map(str, v))))
                else:
                    # Mixed or complex list - convert to string
                    items.append((new_key, str(v)))
            else:
                # Simple value
                items.append((new_key, v))
        
        return dict(items)
    
    def _is_records_format(self, data: dict) -> bool:
        """
        Check if dictionary looks like a records format (has metadata + data)
        
        Args:
            data: Dictionary to check
            
        Returns:
            bool: True if looks like records format
        """
        # Common patterns for records format
        data_keys = ['data', 'records', 'items', 'results', 'entries', 'rows']
        metadata_keys = ['metadata', 'info', 'summary', 'header', 'meta']
        
        has_data_key = any(key in data for key in data_keys)
        has_metadata = any(key in data for key in metadata_keys)
        
        return has_data_key or (len(data) > 1 and has_metadata)
    
    def _find_data_key(self, data: dict) -> str:
        """
        Find the key that contains the actual data array
        
        Args:
            data: Dictionary to search
            
        Returns:
            str: Key name that contains data, or None
        """
        # Priority order for data keys
        data_keys = ['data', 'records', 'items', 'results', 'entries', 'rows']
        
        # Check priority keys first
        for key in data_keys:
            if key in data and isinstance(data[key], list):
                return key
        
        # Check all keys for lists
        for key, value in data.items():
            if isinstance(value, list) and value:
                # Prefer lists of dictionaries
                if isinstance(value[0], dict):
                    return key
        
        # Check for any list
        for key, value in data.items():
            if isinstance(value, list):
                return key
        
        return None

    def _analyze_json_complexity(self, json_data: Any) -> Dict[str, Any]:
        """
        Analyze JSON structure complexity to determine if deep flattening is beneficial
        
        Args:
            json_data: JSON data to analyze
            
        Returns:
            Dict with complexity metrics and recommendations
        """
        complexity = {
            'total_items': 0,
            'max_nesting_depth': 0,
            'nested_arrays': 0,
            'nested_objects': 0,
            'total_potential_columns': 0,
            'needs_deep_flattening': False
        }
        
        def analyze_structure(data, depth=0):
            complexity['max_nesting_depth'] = max(complexity['max_nesting_depth'], depth)
            
            if isinstance(data, list):
                complexity['total_items'] += len(data)
                if data and isinstance(data[0], dict):
                    complexity['nested_arrays'] += 1
                    for item in data[:3]:  # Sample first 3 items
                        analyze_structure(item, depth + 1)
            elif isinstance(data, dict):
                complexity['nested_objects'] += 1
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        analyze_structure(value, depth + 1)
                    else:
                        complexity['total_potential_columns'] += 1
        
        # Analyze the structure
        if isinstance(json_data, list):
            analyze_structure(json_data)
        else:
            analyze_structure([json_data])
        
        # Decision logic for deep flattening
        complexity['needs_deep_flattening'] = (
            complexity['max_nesting_depth'] > 2 or
            complexity['nested_arrays'] > 0 or
            complexity['nested_objects'] > 5
        )
        
        return complexity

    def _smart_deep_flatten_json(self, json_data: Any) -> 'pd.DataFrame':
        """
        Smart deep flattening that preserves data relationships
        
        Args:
            json_data: JSON data to flatten
            
        Returns:
            pd.DataFrame: Deeply flattened data with all nested structures
        """
        import pandas as pd
        
        def deep_flatten(data, sep='_', prefix='', max_array_items=50):
            """
            Enhanced deep flattening with smart limits
            """
            result = {}
            
            if isinstance(data, dict):
                for key, value in data.items():
                    new_key = f"{prefix}{sep}{key}" if prefix else key
                    
                    if isinstance(value, dict):
                        # Recursively flatten nested dictionaries
                        result.update(deep_flatten(value, sep, new_key, max_array_items))
                    elif isinstance(value, list):
                        if value and isinstance(value[0], dict):
                            # List of dictionaries - flatten each item (with limit)
                            items_to_process = min(len(value), max_array_items)
                            for i in range(items_to_process):
                                item = value[i]
                                item_key = f"{new_key}_{i}"
                                result.update(deep_flatten(item, sep, item_key, max_array_items))
                            
                            # Add metadata about truncation
                            if len(value) > max_array_items:
                                result[f"{new_key}_total_count"] = len(value)
                                result[f"{new_key}_truncated_at"] = max_array_items
                        else:
                            # Simple list - convert to string or separate columns
                            if len(value) <= 10:  # Small lists as separate columns
                                for i, item in enumerate(value):
                                    result[f"{new_key}_{i}"] = item
                            else:  # Large lists as concatenated string
                                result[new_key] = ', '.join(str(x) for x in value) if value else ''
                    else:
                        # Simple value
                        result[new_key] = value
            else:
                result[prefix] = data
            
            return result
        
        # Handle different JSON structures
        if isinstance(json_data, list):
            flattened_records = []
            for item in json_data:
                flattened_item = deep_flatten(item)
                flattened_records.append(flattened_item)
            return pd.DataFrame(flattened_records)
        elif isinstance(json_data, dict):
            flattened = deep_flatten(json_data)
            return pd.DataFrame([flattened])
        else:
            return pd.DataFrame({'value': [json_data]})
    
    def parse_datetimes(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
        """
        5/5 DateTime parsing across all formats (README: manager priority)
        
        Automatic datetime detection and parsing for all supported formats
        """
        import pandas as pd
        
        df_result = df.copy()
        date_columns_found = []
        
        if self.verbose:
            print("🗓️ Searching for date columns...")
        
        for col in df.columns:
            if df[col].dtype == 'object':  # Text columns only
                sample = df[col].dropna().astype(str).head(10)
                
                if len(sample) == 0:
                    continue
                
                # Check each date pattern
                for pattern, date_format in self.date_patterns:
                    matches = sum(1 for val in sample if re.search(pattern, val))
                    
                    # If >50% values match date pattern
                    if matches >= len(sample) * 0.5:
                        try:
                            df_result[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
                            date_columns_found.append(col)
                            if self.verbose:
                                print(f"   ✅ Found date column: '{col}' ({date_format})")
                            break
                        except:
                            continue
        
        if not date_columns_found and self.verbose:
            print("   📅 No date columns detected")
        elif date_columns_found and self.verbose:
            print(f"   📅 Total date columns found: {len(date_columns_found)}")
        
        return df_result
