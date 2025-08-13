# db_population_utils/data_loader/__init__.py

"""
DataLoader Module - Essential Data Loading Utilities (Manager Requirements)

This module provides essential data loading capabilities with intelligent 
format detection and quality assessment for core file formats based on manager priorities.

Main Components:
- DataLoader: Core data loading class focused on 3 formats (CSV 95%, Excel 80%, JSON 70%)
- Configuration classes for fine-grained control (CsvParams, ExcelParams, JsonParams)  
- Report classes for comprehensive quality analysis and loading metrics
- Custom exceptions for robust error handling

Manager Requirements Philosophy:
DataLoader implements exactly 10 core methods focusing on:
- Loading Functions (5): load(), load_csv(), load_excel(), load_json(), parse_datetimes()
- Detection Functions (3): detect_format(), detect_encoding(), sniff_csv_params()
- Performance (1): estimate_memory_usage()
- Reporting & Error Handling (2): build_report(), detect_time_columns()

Plus 3 comprehensive single-call operations for common workflows.

Supported Formats (Manager Priority Only):
- CSV/TSV: 95% usage (CRITICAL) - Full parameter detection and encoding handling
- Excel: 80% usage (HIGH) - Sheet detection and selection
- JSON: 70% usage (MEDIUM) - Structure flattening

Excluded Formats (Not in Manager Requirements):
❌ Parquet - Not mentioned in manager priority list
❌ JSON Lines - Not mentioned in manager priority list  
❌ Google Sheets - Not mentioned in manager priority list
❌ URLs - Not mentioned in manager requirements
❌ Compressed archives - Not mentioned in manager requirements

Usage Examples:
    # Basic usage - load file as-is (Manager approved workflow)
    from db_population_utils.data_loader import DataLoader
    loader = DataLoader(verbose=True)
    df = loader.load("data.csv")  # Raw data, no transformations
    
    # Critical datetime parsing (Manager priority)
    df_with_dates = loader.parse_datetimes(df)
    
    # Comprehensive loading with full reporting
    df, report = loader.load_with_comprehensive_report("data.xlsx")
    print(f"Quality Score: {report.data_quality.quality_score}/100")
    
    # CSV with smart detection (95% usage priority)
    df, details = loader.load_csv_with_smart_detection("messy_data.csv")
"""

# Essential data loading components (Manager Requirements Only)
from .data_loader import (
    # Core class (Manager Requirements)
    DataLoader,
    
    # Configuration classes (3 formats only)
    CsvParams,
    ExcelParams,
    JsonParams,
    LoadOptions,
    
    # Report classes
    LoadReport,
    DataQualityReport,
    MemoryEstimate,
    
    # Type definitions and enums (Manager Requirements)
    Kind,  # Only: "auto", "csv", "tsv", "excel", "json"
    LoadStrategy,
    SourceLike,
    PathLike,
    CompressionType,
    
    # Custom exceptions
    DataLoaderError,
    DetectionError,
    UnsupportedFormatError,
    LoadingMemoryError,
)

# Module metadata
__version__ = "0.3.0"
__author__ = "Data Engineering Team"
__description__ = "Essential data loading utilities - Manager Requirements Implementation"

# Public API - Manager Requirements Only
__all__ = [
    # Core class
    "DataLoader",
    
    # Configuration classes (3 formats only)
    "CsvParams",
    "ExcelParams", 
    "JsonParams",
    "LoadOptions",
    
    # Report classes
    "LoadReport",
    "DataQualityReport",
    "MemoryEstimate",
    
    # Type definitions (Manager Requirements)
    "Kind",
    "LoadStrategy", 
    "SourceLike",
    "PathLike",
    "CompressionType",
    
    # Exceptions
    "DataLoaderError",
    "DetectionError",
    "UnsupportedFormatError",
    "LoadingMemoryError",
    
    # Module info
    "__version__",
    
    # Convenience functions (Manager workflow focused)
    "create_essential_loader",
    "quick_csv_load",
    "load_with_datetime_parsing",
]

# Manager Requirements Convenience Functions
def create_essential_loader(
    load_strategy: LoadStrategy = LoadStrategy.PERFORMANCE,
    max_memory_gb: float = 4.0,
    verbose: bool = True,
    **kwargs
) -> DataLoader:
    """
    Create DataLoader with manager-approved defaults for essential formats.
    
    Focuses on the 3 core formats: CSV (95%), Excel (80%), JSON (70%)
    
    Args:
        load_strategy: Default loading strategy
        max_memory_gb: Maximum memory usage
        verbose: Enable detailed logging
        **kwargs: Additional DataLoader arguments
        
    Returns:
        Configured DataLoader instance optimized for manager requirements
        
    Example:
        # Standard setup for manager requirements
        loader = create_essential_loader(
            load_strategy=LoadStrategy.ROBUST,
            max_memory_gb=8.0
        )
        
        # Use with priority formats
        df_csv = loader.load_csv("critical_data.csv")  # 95% priority
        df_excel = loader.load_excel("reports.xlsx")   # 80% priority
        df_json = loader.load_json("api_data.json")    # 70% priority
    """
    return DataLoader(
        verbose=verbose,
        max_memory_usage_gb=max_memory_gb,
        load_strategy=load_strategy,
        **kwargs
    )


def quick_csv_load(
    source: SourceLike,
    auto_detect_encoding: bool = True,
    auto_detect_params: bool = True,
    parse_dates: bool = True,
    **options
) -> tuple["pd.DataFrame", dict]:
    """
    Quick CSV loading utility optimized for 95% usage priority format.
    
    Manager Priority: CSV is CRITICAL format requiring special attention to encoding
    and parameter detection.
    
    Args:
        source: CSV file path or file-like object
        auto_detect_encoding: Use critical encoding detection
        auto_detect_params: Use CSV parameter sniffing
        parse_dates: Automatically detect and parse datetime columns
        **options: Additional options for CSV loading
        
    Returns:
        Tuple of (DataFrame, detection_summary)
        
    Example:
        # Manager workflow for CSV (95% usage)
        df, summary = quick_csv_load("important_data.csv")
        
        print(f"📄 Encoding: {summary['encoding']}")
        print(f"📝 Delimiter: '{summary['delimiter']}'")
        print(f"🕒 Date columns: {summary['date_columns']}")
        print(f"📊 Quality: {summary['quality_score']}/100")
    """
    # Create loader optimized for CSV
    loader = create_essential_loader(verbose=False)
    
    try:
        # Step 1: Critical encoding detection (manager priority)
        encoding, enc_confidence = loader.detect_encoding(source) if auto_detect_encoding else (None, 0.0)
        
        # Step 2: CSV parameter sniffing
        csv_params = loader.sniff_csv_params(source) if auto_detect_params else None
        
        # Step 3: Load CSV with detected parameters
        load_options = {
            'encoding': encoding,
            'params': csv_params,
            **options
        }
        df = loader.load_csv(source, **{k: v for k, v in load_options.items() if v is not None})
        
        # Step 4: Parse datetime columns (manager priority)
        date_columns = []
        if parse_dates and not df.empty:
            date_columns = loader.detect_time_columns(df)
            if date_columns:
                df = loader.parse_datetimes(df, date_columns)
        
        # Step 5: Quick quality assessment
        quality_report = loader._analyze_data_quality(df) if hasattr(loader, '_analyze_data_quality') else None
        
        # Summary for manager workflow
        summary = {
            'encoding': encoding,
            'encoding_confidence': enc_confidence,
            'delimiter': csv_params.delimiter if csv_params else 'unknown',
            'delimiter_confidence': csv_params.delimiter_confidence if csv_params else 0.0,
            'date_columns': date_columns,
            'rows_loaded': len(df),
            'columns_loaded': len(df.columns),
            'quality_score': quality_report.quality_score if quality_report else 0,
            'status': 'success'
        }
        
        return df, summary
        
    except Exception as e:
        # Error summary
        error_summary = {
            'status': 'failed',
            'error': str(e),
            'encoding': 'detection_failed',
            'delimiter': 'detection_failed',
            'date_columns': [],
            'rows_loaded': 0,
            'columns_loaded': 0,
            'quality_score': 0
        }
        raise DataLoaderError(f"Quick CSV load failed: {str(e)}") from e


def load_with_datetime_parsing(
    source: SourceLike,
    datetime_columns: Optional[List[str]] = None,
    auto_detect_datetime: bool = True,
    **load_options
) -> tuple["pd.DataFrame", dict]:
    """
    Load data with emphasis on datetime parsing (Manager priority).
    
    Manager Note: "parse_datetimes() - can cause lots of troubles and can be pretty common"
    
    Args:
        source: File path or file-like object
        datetime_columns: Specific columns to parse as datetime
        auto_detect_datetime: Automatically detect datetime columns
        **load_options: Options for loading
        
    Returns:
        Tuple of (DataFrame with parsed dates, datetime_parsing_report)
        
    Example:
        # Manager workflow for datetime handling
        df, dt_report = load_with_datetime_parsing("time_series.csv")
        
        print(f"🕒 Detected columns: {dt_report['detected_columns']}")
        print(f"✅ Successfully parsed: {dt_report['successful_columns']}")
        print(f"❌ Failed to parse: {dt_report['failed_columns']}")
        print(f"📊 Success rate: {dt_report['overall_success_rate']:.1f}%")
    """
    # Create loader
    loader = create_essential_loader()
    
    try:
        # Step 1: Load data (auto-detect format)
        df = loader.load(source, **load_options)
        
        if df.empty:
            return df, {'status': 'empty_dataframe', 'detected_columns': [], 'successful_columns': [], 'failed_columns': []}
        
        # Step 2: Detect datetime columns (if auto-detect enabled)
        detected_columns = []
        if auto_detect_datetime:
            detected_columns = loader.detect_time_columns(df)
        
        # Step 3: Combine specified and detected columns
        columns_to_parse = []
        if datetime_columns:
            columns_to_parse.extend(datetime_columns)
        if detected_columns:
            columns_to_parse.extend([col for col in detected_columns if col not in columns_to_parse])
        
        # Step 4: Parse datetime columns
        successful_columns = []
        failed_columns = []
        
        if columns_to_parse:
            try:
                df_parsed = loader.parse_datetimes(df, columns_to_parse)
                
                # Check which columns were successfully parsed
                for col in columns_to_parse:
                    if col in df_parsed.columns:
                        if df_parsed[col].dtype.name.startswith('datetime'):
                            successful_columns.append(col)
                        else:
                            failed_columns.append(col)
                    else:
                        failed_columns.append(col)
                
                df = df_parsed
                
            except Exception as e:
                # Partial parsing - try individual columns
                for col in columns_to_parse:
                    try:
                        df = loader.parse_datetimes(df, [col])
                        successful_columns.append(col)
                    except:
                        failed_columns.append(col)
        
        # Step 5: Generate datetime parsing report
        total_columns = len(columns_to_parse) if columns_to_parse else 0
        success_rate = (len(successful_columns) / total_columns * 100) if total_columns > 0 else 0
        
        datetime_report = {
            'status': 'success',
            'detected_columns': detected_columns,
            'specified_columns': datetime_columns or [],
            'columns_attempted': columns_to_parse,
            'successful_columns': successful_columns,
            'failed_columns': failed_columns,
            'overall_success_rate': success_rate,
            'total_datetime_columns': len(successful_columns)
        }
        
        return df, datetime_report
        
    except Exception as e:
        error_report = {
            'status': 'failed',
            'error': str(e),
            'detected_columns': [],
            'successful_columns': [],
            'failed_columns': datetime_columns or [],
            'overall_success_rate': 0.0
        }
        raise DataLoaderError(f"Datetime parsing load failed: {str(e)}") from e


# Optional: Add logging configuration
import logging
import sys
import warnings
from typing import List, Optional

# Set up module logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Check for required dependencies (Manager Requirements)
_ESSENTIAL_DEPENDENCIES = {
    'pandas': "pip install pandas>=1.3.0", 
    'numpy': "pip install numpy>=1.20.0"
}

_FORMAT_SPECIFIC_DEPENDENCIES = {
    # CSV (95% priority - CRITICAL)
    'chardet': "pip install chardet  # CRITICAL: For encoding detection in CSV files",
    
    # Excel (80% priority - HIGH)  
    'openpyxl': "pip install openpyxl  # HIGH: For Excel (.xlsx) support",
    'xlrd': "pip install xlrd  # For legacy Excel (.xls) support", 
    
    # JSON (70% priority - MEDIUM)
    # JSON is handled by built-in json module, no extra dependencies needed
}

# Check essential dependencies
for dep, install_cmd in _ESSENTIAL_DEPENDENCIES.items():
    try:
        __import__(dep)
    except ImportError:
        warnings.warn(
            f"CRITICAL: Required dependency '{dep}' not found. Install with: {install_cmd}",
            ImportWarning,
            stacklevel=2
        )

def check_format_support() -> dict:
    """
    Check which of the 3 manager-required formats are fully supported.
    
    Returns:
        Dictionary with format support status
        
    Example:
        support = check_format_support()
        print(f"CSV support: {support['csv']['status']}")
        print(f"Excel support: {support['excel']['status']}")
        print(f"JSON support: {support['json']['status']}")
    """
    support_status = {
        'csv': {
            'status': 'full',  # pandas built-in support
            'priority': '95% (CRITICAL)',
            'encoding_detection': _check_dependency('chardet'),
            'missing_deps': []
        },
        'excel': {
            'status': 'partial',
            'priority': '80% (HIGH)', 
            'xlsx_support': _check_dependency('openpyxl'),
            'xls_support': _check_dependency('xlrd'),
            'missing_deps': []
        },
        'json': {
            'status': 'full',  # Built-in json module
            'priority': '70% (MEDIUM)',
            'missing_deps': []
        }
    }
    
    # Check Excel dependencies
    if not support_status['excel']['xlsx_support']:
        support_status['excel']['missing_deps'].append('openpyxl')
    if not support_status['excel']['xls_support']:
        support_status['excel']['missing_deps'].append('xlrd')
    
    if support_status['excel']['missing_deps']:
        support_status['excel']['status'] = 'limited'
    else:
        support_status['excel']['status'] = 'full'
    
    # Check CSV encoding detection
    if not support_status['csv']['encoding_detection']:
        support_status['csv']['missing_deps'].append('chardet')
        support_status['csv']['status'] = 'limited'  # Still works but without encoding detection
    
    return support_status

def _check_dependency(dep_name: str) -> bool:
    """Check if dependency is available."""
    try:
        __import__(dep_name)
        return True
    except ImportError:
        return False

# Export dependency checker
__all__.extend(["check_format_support"])

# Manager Requirements Summary
"""
DataLoader - Manager Requirements Implementation

Core Methods (10 total):
✓ Loading Functions (5): load(), load_csv(), load_excel(), load_json(), parse_datetimes()
✓ Detection Functions (3): detect_format(), detect_encoding(), sniff_csv_params()  
✓ Performance (1): estimate_memory_usage()
✓ Reporting & Error Handling (2): build_report(), detect_time_columns()

Format Priorities (Manager Specified):
✓ CSV/TSV: 95% usage (CRITICAL) - Full parameter and encoding detection
✓ Excel: 80% usage (HIGH) - Sheet detection and selection
✓ JSON: 70% usage (MEDIUM) - Structure flattening

Critical Features (Manager Emphasized):
✓ detect_encoding(): "encoding might cause nasty problems, so we definitely should have it"
✓ parse_datetimes(): "can cause lots of troubles and can be pretty common"

Integration with DataProcessor & DBConnector:
DataLoader → DataProcessor → DBConnector ← DBPopulator

Manager Workflow:
    loader = DataLoader()
    df_raw, report = loader.load_with_comprehensive_report("data.csv")
    
    if report.data_quality.quality_score > 80:
        processor = DataProcessor()
        df_clean = processor.clean_data(df_raw)
        
        connector = DBConnector()
        success, db_report = connector.insert_dataframe_with_report(df_clean, "table")

Excluded (Not in Manager Requirements):
❌ Parquet, JSON Lines, Google Sheets, URLs, Compressed archives
"""