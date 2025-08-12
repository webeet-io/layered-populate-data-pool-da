# DataLoader Class Design - Focused & Practical

## Overview
`DataLoader` (core, reusable)

**Responsibility**: Robust, schema-agnostic loading of tabular data from files with intelligent detection, validation, and preprocessing capabilities.

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

### Core Format Support (6 Formats)
* `load_csv(source, params: CsvParams|dict|None=None, dtype_overrides=None, date_columns=None, chunksize=None) -> pd.DataFrame | Iterator[pd.DataFrame]` - Enhanced CSV/TSV loader with advanced parameter detection
* `load_excel(source, sheet='auto', engine=None, decimal=',') -> pd.DataFrame` - Excel loader with intelligent sheet selection
* `load_json(source, record_path=None, meta=None, flatten=True, json_path=None) -> pd.DataFrame` - JSON loader with advanced flattening
* `load_jsonl(source, chunksize: int = None, **kwargs) -> pd.DataFrame | Iterator[pd.DataFrame]` - JSON Lines format with streaming support
* `load_parquet(source, columns: list = None, filters: list = None, **kwargs) -> pd.DataFrame` - Parquet files with column selection and filtering
* `load_google_sheets(url: str, sheet_id: str = None, format: str = 'csv', **kwargs) -> pd.DataFrame` - Direct Google Sheets loading

### Advanced CSV/Text Processing
* `detect_delimiter_advanced(source, sample_size: int = 50000) -> DelimiterInfo` - Advanced delimiter detection with confidence scores
* `detect_quote_char(source, delimiter: str, sample_size: int = 20000) -> str` - Detect quote character
* `detect_null_patterns(source, sample_size: int = 20000) -> list[str]` - Identify null value patterns
* `detect_multiline_records(source, sample_size: int = 10000) -> bool` - Detect multi-line CSV records

### Data Quality & Validation
* `validate_schema(df: pd.DataFrame, schema: dict, strict: bool = False) -> ValidationReport` - Validate DataFrame against schema
* `detect_data_types(df: pd.DataFrame, sample_ratio: float = 0.1) -> dict` - Intelligent data type detection

### Memory & Performance Optimization
* `estimate_memory_usage(source, sample_ratio: float = 0.01) -> MemoryEstimate` - Estimate memory requirements
* `load_in_chunks(source, chunksize: int = 10000, **kwargs) -> Iterator[pd.DataFrame]` - Memory-efficient chunked loading
* `parallel_load(sources: list, max_workers: int = None, **kwargs) -> list[pd.DataFrame]` - Parallel loading of multiple sources
* `stream_load(source, batch_size: int = 1000, **kwargs) -> Iterator[pd.DataFrame]` - Streaming data loader

### Advanced Excel Processing
* `list_excel_sheets(source) -> list[str]` - List all sheets in Excel file
* `detect_excel_structure(source, sheet: str = None) -> ExcelStructure` - Analyze Excel file structure
* `load_excel_range(source, sheet: str, cell_range: str, **kwargs) -> pd.DataFrame` - Load specific cell range
* `merge_excel_sheets(source, sheets: list = None, merge_strategy: str = 'concat') -> pd.DataFrame` - Combine multiple sheets

### JSON Processing Enhancements
* `detect_json_structure(source, sample_size: int = 1000) -> JsonStructure` - Analyze JSON structure
* `extract_json_schema(source) -> dict` - Extract JSON schema
* `normalize_nested_json(obj, max_level: int = 10) -> pd.DataFrame` - Advanced nested JSON normalization

### Time Series & DateTime Processing
* `detect_time_patterns(df: pd.DataFrame, columns: list = None) -> TimePatternReport` - Identify time series patterns
* `standardize_timezones(df: pd.DataFrame, tz_columns: list, target_tz: str = 'UTC') -> pd.DataFrame` - Standardize timezone handling
* `parse_custom_datetime(df: pd.DataFrame, column: str, format_pattern: str) -> pd.DataFrame` - Parse custom datetime formats
* `detect_time_frequency(df: pd.DataFrame, datetime_col: str) -> FrequencyInfo` - Detect time series frequency

### Configuration & Caching
* `save_load_config(path: str, config: LoadOptions) -> None` - Save loading configuration
* `load_config_from_file(path: str) -> LoadOptions` - Load configuration from file
* `cache_detection_results(enabled: bool = True, cache_dir: str = None) -> None` - Cache detection results for performance
* `clear_cache() -> None` - Clear detection cache
* `get_cached_params(source) -> dict` - Get cached detection parameters

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
    kind: str = 'auto'  # csv, excel, json, jsonl, parquet, google_sheets
    delimiter: str = None
    encoding: str = None
    sheet: str = 'auto'
    compression: str = 'infer'  # gzip, bz2, zip, xz
    
    # Data processing options
    date_columns: list[str] = None
    tz_source: str = None
    tz_target: str = 'UTC'
    dtype_overrides: dict = None
    
    # Performance options
    chunksize: int = None
    nrows: int = None
    skiprows: int = None
    load_strategy: str = 'performance'  # performance, memory_efficient, robust, streaming
    
    # Quality options
    validation_level: str = 'basic'  # none, basic, strict, comprehensive
    detect_types: bool = True
    drop_empty_rows: bool = True
```

### Enhanced Report Classes
```python
@dataclass
class LoadReport:
    source: str
    kind: str  # Detected format
    load_strategy: str
    
    # Detection results
    encoding: str = None
    compression_detected: str = None
    csv_params: CsvParams = None
    excel_params: ExcelParams = None
    json_params: JsonParams = None
    
    # Data characteristics
    shape: tuple[int, int] = None
    columns_detected: list[str] = None
    date_columns_found: list[str] = None
    data_types: dict = None
    
    # Quality metrics
    data_quality: DataQualityReport = None
    validation_result: ValidationReport = None
    missing_data_summary: dict = None
    duplicate_count: int = None
    outlier_summary: dict = None
    
    # Performance metrics
    load_time_seconds: float = None
    memory_usage_mb: float = None
    rows_processed: int = None
    processing_speed_rows_per_sec: float = None
    
    # Issues and notes
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    
    # Source metadata
    file_size_bytes: int = None
    file_modified_time: str = None
    source_accessible: bool = True
```

### Specialized Report Classes
```python
@dataclass
class ValidationReport:
    is_valid: bool
    validation_errors: list[str]
    field_validation: dict[str, bool]
    suggestions: list[str]
    validation_time: float = 0.0

@dataclass
class MemoryEstimate:
    estimated_memory_mb: float
    recommended_chunksize: int
    can_load_in_memory: bool
    memory_per_row_bytes: float = 0.0
    
@dataclass
class DataQualityReport:
    missing_data_ratio: float = 0.0
    duplicate_rows: int = 0
    unique_values_per_column: dict[str, int] = field(default_factory=dict)
    data_types_detected: dict[str, str] = field(default_factory=dict)
    outlier_count: dict[str, int] = field(default_factory=dict)
    quality_score: float = 0.0  # 0-100
    recommendations: list[str] = field(default_factory=list)
    
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
    structure_type: str = "unknown"  # flat, nested, array_of_objects
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
    load_strategy: str = 'performance',
    validation_level: str = 'basic'
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
        load_strategy: Default loading strategy (performance, memory_efficient, robust, streaming)
        validation_level: Default validation level (none, basic, strict, comprehensive)
    """
```

## Supported Formats & Usage Statistics

### Format Support Matrix
| Format | Detection | Streaming | Compression | Schema | Validation | Usage |
|--------|-----------|-----------|-------------|--------|------------|-------|
| CSV/TSV | ✓ | ✓ | ✓ | ✓ | ✓ | 95% |
| Excel | ✓ | ✗ | ✓ | ✓ | ✓ | 80% |
| JSON | ✓ | ✓ | ✓ | ✓ | ✓ | 70% |
| JSON Lines | ✓ | ✓ | ✓ | ✓ | ✓ | 20% |
| Parquet | ✓ | ✓ | ✓ | ✓ | ✓ | 35% |
| Google Sheets | ✓ | ✗ | N/A | ✓ | ✓ | 40% |

### Loading Strategies
- **PERFORMANCE**: Fast loading for known-good data, default choice
- **MEMORY_EFFICIENT**: Chunked processing for large files, automatic memory management
- **ROBUST**: Maximum error recovery and validation, comprehensive quality checks
- **STREAMING**: Continuous processing of data streams, minimal memory footprint

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
    validation_level='comprehensive',
    detect_types=True
)
df = loader.load("complex_data.xlsx", options=options)
```

### Format-Specific Loading
```python
# CSV with advanced detection
df = loader.load_csv("data.csv")  # Auto-detects delimiter, encoding, etc.

# Excel with sheet selection
df = loader.load_excel("report.xlsx", sheet="Summary")

# JSON with flattening
df = loader.load_json("nested.json", record_path=['data', 'records'])

# JSON Lines streaming
for chunk in loader.load_jsonl("logs.jsonl", chunksize=1000):
    process_chunk(chunk)

# Parquet with column selection
df = loader.load_parquet("data.parquet", columns=['id', 'name', 'value'])

# Google Sheets direct loading
df = loader.load_google_sheets(
    "https://docs.google.com/spreadsheets/d/abc123/edit",
    sheet_id="123456789"
)
```

### Advanced Features
```python
# Memory-efficient processing
for chunk in loader.load_in_chunks("large_file.csv", chunksize=10000):
    process_chunk(chunk)

# Parallel batch loading
dfs = loader.parallel_load([
    "file1.csv", "file2.json", "file3.parquet"
], max_workers=4)

# Data quality analysis
profile = loader.profile_dataset(df, include_correlations=True)
validation = loader.validate_schema(df, schema_dict)

# Get comprehensive report
report = loader.build_report()
print(f"Quality Score: {report.data_quality.quality_score}/100")
print(f"Load Time: {report.load_time_seconds:.2f}s")
print(f"Memory Usage: {report.memory_usage_mb:.1f}MB")
```

### Error Handling & Recovery
```python
# Load with fallback strategies
df, report = loader.load_with_fallback(
    "problematic_file.csv",
    fallback_options=[
        LoadOptions(encoding='utf-8', delimiter=','),
        LoadOptions(encoding='latin-1', delimiter=';'),
        LoadOptions(encoding='utf-8', on_bad_lines='skip')
    ]
)

# Partial loading with error tolerance
df, errors = loader.recover_corrupted_data(
    "corrupted.csv", 
    recovery_strategy='skip_bad_lines'
)
```

## Integration Points

This focused `DataLoader` class provides:
- **Pure data loading** focused on getting data into pandas DataFrames as-is
- **Intelligent detection** with confidence scoring and fallback strategies  
- **Quality assessment** and validation capabilities for data profiling
- **Performance optimization** for large datasets with multiple loading strategies
- **Google Sheets integration** for collaborative workflows
- **Comprehensive reporting** for load monitoring and data quality insights
- **Seamless integration** with DataProcessor (for transformations) and DBConnector (for database operations)