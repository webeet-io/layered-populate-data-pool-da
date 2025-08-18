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
    
    def load_json(self, source: str, flatten_mode: str = 'smart', **kwargs) -> 'pd.DataFrame':
        """
        4/5 JSON loading with smart detection (README: 70% priority - MEDIUM)
        
        Implements JsonLoader functionality with:
        - Structure flattening (README requirement)
        - Auto-delegation from unified interface
        - Enhanced nested structure handling
        - Relational table extraction
        
        Args:
            source: JSON file path
            flatten_mode: 'smart' (auto), 'simple' (basic), 'relational' (multi-table)
            **kwargs: Additional parameters
            
        Returns:
            pd.DataFrame: Loaded JSON data
        """
        import pandas as pd
        import json
        
        if self.verbose:
            print(f"🗂️ Loading JSON file...")
        
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
            
            # Enhanced JSON flattening logic
            df = self._flatten_json_to_dataframe(json_data, flatten_mode=flatten_mode)
            
            # Auto-detect and parse datetimes
            df = self.parse_datetimes(df)
            
            if self.verbose:
                print(f"✅ JSON loaded: {len(df)} rows, {len(df.columns)} columns")
                print(f"   📊 Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Error loading JSON: {e}")
            # Fallback to pandas default JSON loading
            df = pd.read_json(source, **kwargs)
            df = self.parse_datetimes(df)
            return df

    def load_json_as_tables(self, source: str) -> Dict[str, 'pd.DataFrame']:
        """
        Load JSON and return all extracted relational tables
        
        Args:
            source: JSON file path
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of table_name -> DataFrame
        """
        import pandas as pd
        import json
        
        if self.verbose:
            print(f"🗂️ Loading JSON as tables...")
        
        try:
            # Load raw JSON data first
            with open(source, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Extract relational tables
            tables = self._extract_relational_tables(json_data)
            
            if self.verbose:
                print(f"   📊 Tables extracted: {list(tables.keys())}")
            
            return tables
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Error loading JSON as tables: {e}")
            raise ValueError(f"Error loading JSON as tables: {e}")

    def _flatten_json_to_dataframe(self, data: Any, flatten_mode: str = 'smart') -> 'pd.DataFrame':
        """
        Enhanced JSON flattening that handles complex nested structures
        
        Args:
            data: JSON data (dict, list, or other)
            flatten_mode: 'smart' (auto), 'simple' (basic), 'relational' (multi-table)
            
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
                    return self._flatten_json_to_dataframe(data[data_key], flatten_mode=flatten_mode)
            
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


# Example usage
if __name__ == "__main__":
    # Quick test
    loader = SmartAutoDataLoader(verbose=True)
    
    print("\n🎯 SmartAutoDataLoader ready!")
    print("Usage: loader.load('your_file.csv')")
    print("Features: Auto-detection, datetime parsing, comprehensive reporting")
    print("Supports: CSV (95%), Excel (80%), JSON (70%)")