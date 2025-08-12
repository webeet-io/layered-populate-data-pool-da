# DataLoader Class Design

## Overview
`DataLoader` (core, reusable)

**Responsibility**: Robust, schema-agnostic loading of tabular data from diverse sources (files, URLs, databases, cloud storage) with intelligent detection, validation, and preprocessing capabilities.

## Core Methods (Original Design)

### Initialization
* `__init__(verbose: bool = True)` - Initialize loader with logging preferences

### Main Loading Interface
* `load(source, kind='auto', options: LoadOptions|dict|None=None) -> pd.DataFrame` - Universal data loading interface with auto-detection

### Format Detection & Analysis
* `detect_encoding(source, sample_size=20000) -> str` - Detect file encoding with confidence scoring
* `sniff_csv_params(source, sample_size=20000) -> CsvParams` - Auto-detect CSV parameters
* `detect_time_columns(df, hints=None, min_parse_rate=0.8) -> list[str]` - Identify datetime columns

### Format-Specific Loading
* `load_csv(source, params: CsvParams|dict|None=None, dtype_overrides=None, date_columns=None, chunksize=None) -> pd.DataFrame | Iterator[pd.DataFrame]` - Load CSV/TSV files
* `load_excel(source, sheet='auto', engine=None, decimal=',') -> pd.DataFrame` - Load Excel files with sheet auto-selection
* `load_json(source, record_path=None, meta=None, flatten=True, json_path=None) -> pd.DataFrame` - Load and normalize JSON data

### Data Processing
* `flatten_json(obj, record_path=None, meta=None) -> pd.DataFrame` - Flatten nested JSON structures
* `parse_datetimes(df, cols, tz_source=None, tz_target='UTC', dayfirst=False, infer=True) -> pd.DataFrame` - Parse and normalize datetime columns

### Reporting
* `build_report() -> LoadReport` - Generate comprehensive loading report

## Enhanced Methods (Extensions)

### Advanced Source Support
* `load_from_url(url: str, headers: dict = None, auth: tuple = None, **kwargs) -> pd.DataFrame` - Load from HTTP/HTTPS URLs with authentication
* `load_from_s3(bucket: str, key: str, aws_config: dict = None, **kwargs) -> pd.DataFrame` - Load from AWS S3
* `load_from_gcs(bucket: str, blob: str, credentials: dict = None, **kwargs) -> pd.DataFrame` - Load from Google Cloud Storage
* `load_from_azure(container: str, blob: str, connection_string: str = None, **kwargs) -> pd.DataFrame` - Load from Azure Blob Storage
* `load_from_ftp(host: str, path: str, credentials: dict = None, **kwargs) -> pd.DataFrame` - Load from FTP/SFTP servers
* `load_from_database(query: str, connection, **kwargs) -> pd.DataFrame` - Load from database query results

### Enhanced Format Support
* `load_parquet(source, columns: list = None, filters: list = None, **kwargs) -> pd.DataFrame` - Load Parquet files with column selection
* `load_avro(source, **kwargs) -> pd.DataFrame` - Load Apache Avro files
* `load_orc(source, columns: list = None, **kwargs) -> pd.DataFrame` - Load ORC files
* `load_xml(source, xpath: str = None, namespaces: dict = None, **kwargs) -> pd.DataFrame` - Load and parse XML files
* `load_yaml(source, **kwargs) -> pd.DataFrame` - Load YAML files
* `load_fixed_width(source, colspecs: list, names: list = None, **kwargs) -> pd.DataFrame` - Load fixed-width files
* `load_hdf5(source, key: str, **kwargs) -> pd.DataFrame` - Load HDF5 files

### Advanced CSV/Text Processing
* `detect_delimiter_advanced(source, sample_size: int = 50000) -> DelimiterInfo` - Advanced delimiter detection with confidence scores
* `detect_quote_char(source, delimiter: str, sample_size: int = 20000) -> str` - Detect quote character
* `detect_null_patterns(source, sample_size: int = 20000) -> list[str]` - Identify null value patterns
* `clean_headers(df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame` - Clean and normalize column headers
* `detect_multiline_records(source, sample_size: int = 10000) -> bool` - Detect multi-line CSV records

### Data Quality & Validation
* `validate_schema(df: pd.DataFrame, schema: dict, strict: bool = False) -> ValidationReport` - Validate DataFrame against schema
* `detect_data_types(df: pd.DataFrame, sample_ratio: float = 0.1) -> dict` - Intelligent data type detection
* `identify_duplicates(df: pd.DataFrame, subset: list = None) -> DuplicateReport` - Identify and analyze duplicate records
* `detect_outliers(df: pd.DataFrame, columns: list = None, method: str = 'iqr') -> OutlierReport` - Statistical outlier detection
* `analyze_missing_data(df: pd.DataFrame) -> MissingDataReport` - Comprehensive missing data analysis
* `validate_data_integrity(df: pd.DataFrame, rules: list) -> IntegrityReport` - Custom data integrity validation

### Memory & Performance Optimization
* `estimate_memory_usage(source, sample_ratio: float = 0.01) -> MemoryEstimate` - Estimate memory requirements
* `load_in_chunks(source, chunksize: int = 10000, **kwargs) -> Iterator[pd.DataFrame]` - Memory-efficient chunked loading
* `optimize_dtypes(df: pd.DataFrame, aggressive: bool = False) -> pd.DataFrame` - Optimize DataFrame memory usage
* `parallel_load(sources: list, max_workers: int = None, **kwargs) -> list[pd.DataFrame]` - Parallel loading of multiple sources
* `stream_load(source, batch_size: int = 1000, **kwargs) -> Iterator[pd.DataFrame]` - Streaming data loader

### Advanced Excel Processing
* `list_excel_sheets(source) -> list[str]` - List all sheets in Excel file
* `detect_excel_structure(source, sheet: str = None) -> ExcelStructure` - Analyze Excel file structure
* `load_excel_range(source, sheet: str, cell_range: str, **kwargs) -> pd.DataFrame` - Load specific cell range
* `merge_excel_sheets(source, sheets: list = None, merge_strategy: str = 'concat') -> pd.DataFrame` - Combine multiple sheets

### JSON Processing Enhancements
* `detect_json_structure(source, sample_size: int = 1000) -> JsonStructure` - Analyze JSON structure
* `load_jsonl(source, **kwargs) -> pd.DataFrame` - Load JSON Lines files
* `extract_json_schema(source) -> dict` - Extract JSON schema
* `normalize_nested_json(obj, max_level: int = 10) -> pd.DataFrame` - Advanced nested JSON normalization

### Time Series & DateTime Processing
* `detect_time_patterns(df: pd.DataFrame, columns: list = None) -> TimePatternReport` - Identify time series patterns
* `standardize_timezones(df: pd.DataFrame, tz_columns: list, target_tz: str = 'UTC') -> pd.DataFrame` - Standardize timezone handling
* `parse_custom_datetime(df: pd.DataFrame, column: str, format_pattern: str) -> pd.DataFrame` - Parse custom datetime formats
* `detect_time_frequency(df: pd.DataFrame, datetime_col: str) -> FrequencyInfo` - Detect time series frequency
* `fill_time_gaps(df: pd.DataFrame, datetime_col: str, freq: str = None, method: str = 'interpolate') -> pd.DataFrame` - Fill gaps in time series

### Configuration & Caching
* `save_load_config(path: str, config: LoadOptions) -> None` - Save loading configuration
* `load_config_from_file(path: str) -> LoadOptions` - Load configuration from file
* `cache_detection_results(enabled: bool = True, cache_dir: str = None) -> None` - Cache detection results for performance
* `clear_cache() -> None` - Clear detection cache
* `get_cached_params(source) -> dict` - Get cached detection parameters

### Preprocessing & Transformation
* `apply_preprocessing(df: pd.DataFrame, steps: list[PreprocessingStep]) -> pd.DataFrame` - Apply preprocessing pipeline
* `normalize_text_columns(df: pd.DataFrame, columns: list = None, strategy: str = 'auto') -> pd.DataFrame` - Normalize text data
* `encode_categorical(df: pd.DataFrame, columns: list = None, method: str = 'auto') -> pd.DataFrame` - Encode categorical variables
* `scale_numeric_columns(df: pd.DataFrame, columns: list = None, method: str = 'standard') -> pd.DataFrame` - Scale numeric data

### Error Handling & Recovery
* `load_with_fallback(source, fallback_options: list[LoadOptions]) -> LoadResult` - Load with fallback strategies
* `recover_corrupted_data(source, recovery_strategy: str = 'skip_bad_lines') -> pd.DataFrame` - Recover from corrupted files
* `partial_load_on_error(source, error_threshold: float = 0.1, **kwargs) -> PartialLoadResult` - Partial loading with error tolerance
* `validate_before_load(source, quick_check: bool = True) -> ValidationResult` - Pre-load validation

### Metadata & Profiling
* `profile_dataset(df: pd.DataFrame, include_correlations: bool = False) -> DataProfile` - Comprehensive data profiling
* `extract_metadata(source) -> FileMetadata` - Extract file metadata
* `generate_data_dictionary(df: pd.DataFrame, include_stats: bool = True) -> dict` - Generate data dictionary
* `compare_datasets(df1: pd.DataFrame, df2: pd.DataFrame) -> ComparisonReport` - Compare two datasets

## Enhanced Support Types (Dataclasses)

### Core Configuration Classes
```python
@dataclass
class CsvParams:
    delimiter: str = ','
    decimal: str = '.'
    header: Union[int, list, None] = 'infer'
    encoding: str = 'utf-8'
    quote_char: str = '"'
    escape_char: str = None
    null_values: list[str] = field(default_factory=list)
    skip_rows: int = 0
    comment_char: str = None
```

```python
@dataclass
class LoadOptions:
    # Format options
    delimiter: str = None
    encoding: str = None
    sheet: str = 'auto'
    
    # Data processing options
    date_columns: list[str] = None
    tz_source: str = None
    tz_target: str = 'UTC'
    dtype_overrides: dict = None
    
    # Performance options
    chunksize: int = None
    nrows: int = None
    skiprows: int = None
    
    # Quality options
    validate_schema: bool = False
    clean_headers: bool = True
    detect_types: bool = True
    
    # Preprocessing options
    preprocessing_steps: list = None
    normalize_text: bool = False
    handle_missing: str = 'auto'
```

### Enhanced Report Classes
```python
@dataclass
class LoadReport:
    source: str
    format_detected: str
    encoding_used: str
    delimiter_used: str = None
    sheet_selected: str = None
    
    # Data characteristics
    shape: tuple[int, int] = None
    columns_detected: list[str] = None
    date_columns_found: list[str] = None
    data_types: dict = None
    
    # Quality metrics
    missing_data_summary: dict = None
    duplicate_count: int = None
    outlier_summary: dict = None
    
    # Performance metrics
    load_time_seconds: float = None
    memory_usage_mb: float = None
    rows_processed: int = None
    
    # Warnings and errors
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

### Specialized Report Classes
```python
@dataclass
class ValidationReport:
    schema_valid: bool
    validation_errors: list[str]
    field_validation: dict[str, bool]
    suggestions: list[str]

@dataclass
class MemoryEstimate:
    estimated_memory_mb: float
    recommended_chunksize: int
    can_load_in_memory: bool
    
@dataclass
class ExcelStructure:
    sheets: list[str]
    recommended_sheet: str
    sheet_shapes: dict[str, tuple]
    has_merged_cells: bool
    
@dataclass
class JsonStructure:
    max_nesting_level: int
    record_count_estimate: int
    field_types: dict
    recommended_record_path: str
```

## Enhanced Initialization

```python
def __init__(
    self,
    verbose: bool = True,
    cache_enabled: bool = True,
    cache_dir: str = None,
    max_memory_usage_gb: float = 4.0,
    default_encoding: str = 'utf-8',
    chunk_size_auto: bool = True,
    parallel_processing: bool = True,
    max_workers: int = None,
    logger: logging.Logger = None,
    preprocessing_pipeline: list = None
):
    """
    Initialize DataLoader with enhanced configuration options.
    
    Args:
        verbose: Enable detailed logging
        cache_enabled: Enable detection result caching
        cache_dir: Directory for cache files
        max_memory_usage_gb: Maximum memory usage limit
        default_encoding: Default encoding for text files
        chunk_size_auto: Automatically determine optimal chunk size
        parallel_processing: Enable parallel processing
        max_workers: Maximum worker threads for parallel processing
        logger: Custom logger instance
        preprocessing_pipeline: Default preprocessing steps
    """
```

## Usage Examples

### Basic Usage
```python
# Initialize with enhanced options
loader = DataLoader(
    verbose=True,
    cache_enabled=True,
    max_memory_usage_gb=8.0
)

# Universal loading with auto-detection
df = loader.load("data.csv")

# Advanced loading with options
options = LoadOptions(
    validate_schema=True,
    clean_headers=True,
    preprocessing_steps=[
        PreprocessingStep('normalize_text'),
        PreprocessingStep('handle_missing', strategy='interpolate')
    ]
)
df = loader.load("complex_data.xlsx", options=options)
```

### Advanced Features
```python
# Load from cloud storage
df = loader.load_from_s3("my-bucket", "data/file.parquet")

# Memory-efficient processing
for chunk in loader.load_in_chunks("large_file.csv", chunksize=10000):
    process_chunk(chunk)

# Data quality analysis
profile = loader.profile_dataset(df, include_correlations=True)
validation = loader.validate_schema(df, schema_dict)

# Get comprehensive report
report = loader.build_report()
```

## Integration Points

This enhanced `DataLoader` class provides:
- **Comprehensive format support** for modern data engineering needs
- **Advanced data quality** and validation capabilities
- **Performance optimization** for large datasets
- **Cloud storage integration** for modern data pipelines
- **Extensible preprocessing** pipeline architecture
- **Production-ready monitoring** and reporting