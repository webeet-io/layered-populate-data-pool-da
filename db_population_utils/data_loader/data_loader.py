# db_population_utils/data_loader.py

"""
DataLoader Module - Pure Data Loading with Quality Assessment

This module provides comprehensive data loading capabilities with intelligent format
detection and quality assessment for multiple file formats.

Key Design Philosophy:
    - **Intelligence First**: Automatic detection of formats, encodings, and structures
    - **Quality Focused**: Built-in data validation, profiling, and quality assessment (no transformation)
    - **Performance Aware**: Memory-efficient processing with multiple loading strategies
    - **Format Focused**: Unified interface for 6 core file formats
    - **Integration Ready**: Seamless integration with DataProcessor and DBConnector

Architecture Overview:
    ┌──────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
    │   Data Sources   │────│    DataLoader       │────│   Raw DataFrames     │
    │                  │    │                     │    │                      │
    │ • Files (CSV,    │    │ • Format Detection  │    │ • Data as-is         │
    │   Excel, JSON,   │    │ • Parameter Sniffing│    │ • Quality Reports    │
    │   JSON Lines,    │    │ • Validation        │    │ • Ready for          │
    │   Parquet)       │    │ • Quality Assessment│    │   DataProcessor      │
    │ • Google Sheets  │    │ • Memory Mgmt       │    │   or Analysis        │
    │ • Compressed     │    │ • Error Recovery    │    │                      │
    │   Archives       │    │                     │    │                      │
    └──────────────────┘    └─────────────────────┘    └──────────────────────┘
                                       │
                            ┌─────────────────────┐
                            │   Intelligence      │
                            │                     │
                            │ • Encoding Detection│
                            │ • CSV Sniffing      │
                            │ • Schema Inference  │
                            │ • Quality Analysis  │
                            │ • Performance Tuning│
                            └─────────────────────┘

Problem Solving Focus:
    1. **Format Chaos**: Different file formats, encodings, separators, structures
       → Automatic detection with confidence scoring
    
    2. **Data Quality Issues**: Missing values, inconsistent types, encoding errors
       → Quality assessment and reporting (processing handled by DataProcessor)
       
    3. **Memory Constraints**: Large files that don't fit in memory
       → Chunking, streaming, and memory estimation strategies
       
    4. **Integration Complexity**: Multiple file formats with different parsing requirements
       → Unified interface with format-specific optimizations
       
    5. **Production Reliability**: Files fail to load, corrupt data, schema changes
       → Error recovery, fallback strategies, and detailed reporting

    Enhanced Features vs Traditional pandas.read_*():
    ✓ **Smart Detection**: Auto-detect format, encoding, delimiter, headers
    ✓ **Quality Assessment**: Data validation, profiling, quality reporting (no transformation)
    ✓ **Memory Intelligence**: Automatic chunking and memory optimization
    ✓ **Google Sheets**: Direct loading from Google Sheets URLs with sheet selection
    ✓ **Error Recovery**: Fallback strategies and partial loading capabilities
    ✓ **Performance Tuning**: Multiple loading strategies for different scenarios
    ✓ **Rich Reporting**: Comprehensive load reports with metrics and recommendations

Target Use Cases:
    1. **Data Ingestion**: Load raw data from various sources for processing
    2. **ETL Pipelines**: Extract data from files as first step in transformation workflows
    3. **Data Analysis**: Load files for exploratory analysis with quality checks
    4. **Data Validation**: Verify file data quality before database insertion
    5. **Data Migration**: Move data between different file formats and systems
    6. **Batch Processing**: Handle large files with memory-efficient strategies

    Integration with DataProcessor & DBConnector:
    ```python
    # Complete data pipeline
    loader = DataLoader(validation_level=ValidationLevel.COMPREHENSIVE)
    processor = DataProcessor()  # Separate class for transformations
    connector = DBConnector(config_file="db_config.yaml")
    
    # Load, process, and insert
    df_raw = loader.load("raw_data.csv")
    report = loader.build_report()
    
    if report.data_quality.quality_score > 80:
        df_clean = processor.clean_data(df_raw)  # Processing in separate class
        connector.to_sql(df_clean, "clean_data", target="ingestion")
    ```

Load Strategy Examples:
    • **PERFORMANCE**: Fast loading for known-good data
    • **MEMORY_EFFICIENT**: Chunked processing for large files
    • **ROBUST**: Maximum error recovery and validation
    • **STREAMING**: Continuous processing of data streams

    Format Support Matrix:
    Format     │ Detection │ Streaming │ Compression │ Schema │ Validation │ Usage
    ───────────┼───────────┼───────────┼─────────────┼────────┼────────────┼───────
    CSV/TSV    │    ✓      │     ✓     │      ✓      │   ✓    │     ✓      │ 95%
    Excel      │    ✓      │     ✗     │      ✓      │   ✓    │     ✓      │ 80%
    JSON       │    ✓      │     ✓     │      ✓      │   ✓    │     ✓      │ 70%
    JSON Lines │    ✓      │     ✓     │      ✓      │   ✓    │     ✓      │ 20%
    Parquet    │    ✓      │     ✓     │      ✓      │   ✓    │     ✓      │ 35%
    G. Sheets  │    ✓      │     ✗     │      N/A    │   ✓    │     ✓      │ 40%

Example Workflows:
    # Quick and simple
    df = DataLoader().load("data.csv")
    
    # Production with validation
    loader = DataLoader(
        load_strategy=LoadStrategy.ROBUST,
        validation_level=ValidationLevel.COMPREHENSIVE
    )
    df = loader.load("production_data.xlsx")
    
    # Memory-efficient large file processing
    for chunk in loader.load_streaming("huge_file.csv", chunk_size=10000):
        process_chunk(chunk)
    
    # Multi-source batch loading (6 supported formats)
    dfs = loader.load_batch([
        "source1.csv", 
        "data/source2.json",
        "data.parquet",
        "https://docs.google.com/spreadsheets/d/abc123/edit"
    ])
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union, Literal, Callable
from contextlib import contextmanager
from pathlib import Path
from enum import Enum
import logging

# Type-only imports to keep design stub lightweight
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd
    from io import IOBase

# Enhanced type definitions
PathLike = Union[str, Path]
SourceLike = Union[PathLike, "IOBase", str]  # file path/URL or open file-like object
Kind = Literal[
    "auto", "csv", "tsv", "excel", "json", "jsonl", "parquet", "google_sheets"
]
PreprocessingStrategy = Literal["auto", "skip", "clean", "normalize", "validate"]
CompressionType = Literal["infer", "gzip", "bz2", "zip", "xz", None]


# -----------------------
# Enhanced Enums
# -----------------------
class LoadStrategy(Enum):
    """Loading strategies for different scenarios."""
    MEMORY_EFFICIENT = "memory_efficient"
    PERFORMANCE = "performance"
    ROBUST = "robust"
    STREAMING = "streaming"


class ValidationLevel(Enum):
    """Data validation levels."""
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    COMPREHENSIVE = "comprehensive"


# -----------------------
# Enhanced Support dataclasses
# -----------------------
@dataclass
class CsvParams:
    """
    Enhanced parameters for CSV/TSV loading with advanced detection results.
    """
    delimiter: str = ","
    decimal: str = "."
    header: Optional[int] = 0
    encoding: Optional[str] = None
    # Enhanced parameters
    quote_char: str = '"'
    escape_char: Optional[str] = None
    null_values: List[str] = field(default_factory=lambda: ['', 'NULL', 'null', 'NA', 'na'])
    skip_rows: int = 0
    comment_char: Optional[str] = None
    thousands_sep: Optional[str] = None
    # Detection confidence scores
    delimiter_confidence: float = 0.0
    encoding_confidence: float = 0.0
    has_multiline_records: bool = False


@dataclass
class ExcelParams:
    """Parameters for Excel file loading."""
    sheet: Union[str, int, Literal["auto"], None] = "auto"
    engine: Optional[str] = None
    decimal: Optional[str] = None
    # Enhanced parameters
    header: Optional[Union[int, List[int]]] = 0
    index_col: Optional[Union[int, str, List]] = None
    usecols: Optional[Union[str, List]] = None
    skiprows: Optional[Union[int, List[int], Callable]] = None
    nrows: Optional[int] = None
    # Detection results
    available_sheets: List[str] = field(default_factory=list)
    recommended_sheet: Optional[str] = None
    sheet_shapes: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    has_merged_cells: bool = False


@dataclass
class JsonParams:
    """Parameters for JSON file loading."""
    record_path: Optional[Union[str, List[str]]] = None
    meta: Optional[List[str]] = None
    json_path: Optional[str] = None
    # Enhanced parameters
    lines: bool = False  # JSON Lines format
    orient: Optional[str] = None
    max_nesting_level: int = 10
    # Detection results
    structure_type: str = "unknown"  # "flat", "nested", "array_of_objects", etc.
    estimated_records: Optional[int] = None
    field_types: Dict[str, str] = field(default_factory=dict)


@dataclass
class PreprocessingStep:
    """Configuration for preprocessing steps."""
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Callable] = None
    error_strategy: str = "raise"  # "raise", "skip", "warn"


@dataclass
class LoadOptions:
    """
    Enhanced high-level overrides to control loading behavior across formats.
    """
    # Format detection
    kind: Kind = "auto"
    encoding: Optional[str] = None
    compression: CompressionType = "infer"
    
    # Performance options
    chunksize: Optional[int] = None
    nrows: Optional[int] = None
    skiprows: Optional[Union[int, List[int], Callable]] = None
    low_memory: bool = True
    dtype_overrides: Optional[Dict[str, Any]] = None
    
    # CSV/TSV specific
    delimiter: Optional[str] = None
    decimal: Optional[str] = None
    header: Optional[Union[int, List[int]]] = None
    quote_char: Optional[str] = None
    null_values: Optional[List[str]] = None
    
    # Excel specific
    sheet: Union[str, int, Literal["auto"], None] = "auto"
    engine: Optional[str] = None
    
    # JSON specific
    flatten_json: bool = True
    record_path: Optional[Union[str, List[str]]] = None
    meta: Optional[List[str]] = None
    json_path: Optional[str] = None
    max_nesting_level: int = 10
    
    # Advanced format options (for specific formats that support them)
    fixed_width_colspecs: Optional[List[Tuple[int, int]]] = None  # Only for fixed-width files if added later
    
    # Datetime handling
    date_columns: Optional[List[str]] = None
    detect_time_columns: bool = True
    tz_source: Optional[str] = None
    tz_target: Optional[str] = "UTC"
    dayfirst: bool = False
    infer_datetime_format: bool = True
    custom_date_parser: Optional[Callable] = None
    
    # Data quality and validation (assessment only, no transformation)
    validation_level: ValidationLevel = ValidationLevel.BASIC
    schema: Optional[Dict[str, Any]] = None
    drop_empty_rows: bool = True
    drop_empty_columns: bool = False
    
    # Error handling
    on_bad_lines: str = "error"  # "error", "warn", "skip"
    error_tolerance: float = 0.0  # percentage of errors to tolerate
    
    # Memory and performance
    load_strategy: LoadStrategy = LoadStrategy.PERFORMANCE
    parallel_processing: bool = False
    max_workers: Optional[int] = None
    cache_detection: bool = True


@dataclass
class ValidationReport:
    """Report from data validation operations."""
    is_valid: bool
    validation_errors: List[str] = field(default_factory=list)
    field_validation: Dict[str, bool] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    validation_time: float = 0.0


@dataclass
class MemoryEstimate:
    """Memory usage estimation."""
    estimated_memory_mb: float
    recommended_chunksize: Optional[int] = None
    can_load_in_memory: bool = True
    memory_per_row_bytes: float = 0.0


@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment."""
    missing_data_ratio: float = 0.0
    duplicate_rows: int = 0
    unique_values_per_column: Dict[str, int] = field(default_factory=dict)
    data_types_detected: Dict[str, str] = field(default_factory=dict)
    outlier_count: Dict[str, int] = field(default_factory=dict)
    quality_score: float = 0.0  # 0-100
    recommendations: List[str] = field(default_factory=list)


@dataclass
class LoadReport:
    """
    Enhanced comprehensive summary of what the loader decided/did.
    """
    # Basic info
    source: str
    kind: Kind
    load_strategy: LoadStrategy
    
    # Detection results
    encoding: Optional[str] = None
    compression_detected: Optional[str] = None
    csv_params: Optional[CsvParams] = None
    excel_params: Optional[ExcelParams] = None
    json_params: Optional[JsonParams] = None
    
    # Data characteristics  
    shape: Optional[Tuple[int, int]] = None
    columns_detected: List[str] = field(default_factory=list)
    data_types: Dict[str, str] = field(default_factory=dict)
    
    # Datetime processing
    detected_time_cols: List[str] = field(default_factory=list)
    tz_applied: Optional[str] = None
    datetime_parsing_success_rate: Dict[str, float] = field(default_factory=dict)
    
    # Quality assessment
    data_quality: Optional[DataQualityReport] = None
    validation_result: Optional[ValidationReport] = None
    
    # Performance metrics
    load_time_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    rows_processed: int = 0
    processing_speed_rows_per_sec: float = 0.0
    
    # Issues and notes
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    
    # Source metadata
    file_size_bytes: Optional[int] = None
    file_modified_time: Optional[str] = None
    source_accessible: bool = True


@dataclass
class StreamingResult:
    """Result from streaming operations."""
    chunk_iterator: Iterator["pd.DataFrame"]
    total_chunks_estimate: Optional[int] = None
    chunk_size: int = 1000
    metadata: Optional[LoadReport] = None


# -----------------------
# Custom Exceptions
# -----------------------
class DataLoaderError(Exception):
    """Base exception for DataLoader operations."""


class DetectionError(DataLoaderError):
    """Raised when automatic detection fails."""


class ValidationError(DataLoaderError):
    """Raised when data validation fails."""


class UnsupportedFormatError(DataLoaderError):
    """Raised when file format is not supported."""


class MemoryError(DataLoaderError):
    """Raised when estimated memory usage exceeds limits."""


# -----------------------
# Enhanced Design stub: DataLoader
# -----------------------
class DataLoader:
    """
    DataLoader — Pure data loading with intelligent detection and quality assessment.

    Purpose:
      Robustly load tabular data from 6 file formats with:
        - Advanced format detection and parameter sniffing
        - Comprehensive data quality analysis and assessment (no transformation)
        - Memory-efficient processing with multiple loading strategies
        - Google Sheets integration for collaborative workflows
        - Comprehensive monitoring and reporting
        - Error recovery and fallback strategies

    Features:
      - Support for 6 key file formats (CSV, Excel, JSON, JSON Lines, Parquet, Google Sheets)
      - Intelligent format detection and parameter sniffing
      - Advanced datetime handling with timezone support
      - Data quality assessment and validation (no transformation)
      - Memory optimization and streaming capabilities
      - Comprehensive reporting and monitoring
    """

    def __init__(
        self,
        verbose: bool = True,
        # Enhanced initialization parameters
        cache_enabled: bool = True,
        cache_dir: Optional[PathLike] = None,
        max_memory_usage_gb: float = 4.0,
        default_encoding: str = 'utf-8',
        chunk_size_auto: bool = True,
        parallel_processing: bool = True,
        max_workers: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        load_strategy: LoadStrategy = LoadStrategy.PERFORMANCE,
        validation_level: ValidationLevel = ValidationLevel.BASIC,
    ):
        """
        Initialize enhanced DataLoader with comprehensive configuration.
        
        Args:
            verbose: Enable detailed logging during operations
            cache_enabled: Enable caching of detection results
            cache_dir: Directory for cache files
            max_memory_usage_gb: Maximum memory usage limit
            default_encoding: Default text encoding
            chunk_size_auto: Automatically determine optimal chunk size
            parallel_processing: Enable parallel processing
            max_workers: Maximum worker threads
            logger: Custom logger instance
            load_strategy: Default loading strategy
            validation_level: Default validation level
        """
        raise NotImplementedError

    # -----------------------
    # High-level entry points
    # -----------------------
    def load(
        self,
        source: SourceLike,
        *,
        kind: Kind = "auto",
        options: Optional[LoadOptions] = None,
    ) -> "pd.DataFrame":
        """
        Enhanced high-level loader with comprehensive format support and intelligence.
        
        Args:
            source: File path, URL, or file-like object
            kind: Format type or 'auto' for detection
            options: Loading configuration options
            
                    Returns:
            Raw DataFrame loaded as-is (no transformations applied)
            
        Raises:
            DataLoaderError: On loading failures
            UnsupportedFormatError: For unsupported formats
            ValidationError: On validation failures
        """
        raise NotImplementedError

    def load_batch(
        self,
        sources: List[SourceLike],
        *,
        kind: Kind = "auto",
        options: Optional[LoadOptions] = None,
        parallel: bool = True,
    ) -> List["pd.DataFrame"]:
        """Load multiple sources in batch, optionally in parallel."""
        raise NotImplementedError

    def load_streaming(
        self,
        source: SourceLike,
        *,
        kind: Kind = "auto",
        chunk_size: int = 10000,
        options: Optional[LoadOptions] = None,
    ) -> StreamingResult:
        """Load data as streaming chunks for memory-efficient processing."""
        raise NotImplementedError

    @contextmanager
    def load_context(
        self,
        source: SourceLike,
        *,
        kind: Kind = "auto",
        options: Optional[LoadOptions] = None,
    ):
        """Context manager for resource-managed loading."""
        raise NotImplementedError

    # -----------------------
    # Enhanced Detection utilities
    # -----------------------
    def detect_format(self, source: SourceLike) -> Tuple[Kind, float]:
        """Detect file format with confidence score."""
        raise NotImplementedError

    def detect_encoding(
        self, 
        source: SourceLike, 
        *, 
        sample_size: int = 20000,
        confidence_threshold: float = 0.8
    ) -> Tuple[str, float]:
        """Enhanced encoding detection with confidence score."""
        raise NotImplementedError

    def sniff_csv_params(
        self, 
        source: SourceLike, 
        *, 
        sample_size: int = 20000,
        advanced_detection: bool = True
    ) -> CsvParams:
        """Enhanced CSV parameter detection with advanced sniffing."""
        raise NotImplementedError

    def detect_compression(self, source: SourceLike) -> Optional[str]:
        """Detect compression format (gzip, bz2, zip, etc.)."""
        raise NotImplementedError

    def analyze_structure(self, source: SourceLike, kind: Kind = "auto") -> Dict[str, Any]:
        """Analyze file structure and provide recommendations."""
        raise NotImplementedError

    def detect_time_columns(
        self,
        df: "pd.DataFrame",
        *,
        hints: Optional[List[str]] = None,
        min_parse_rate: float = 0.8,
        sample_size: Optional[int] = None,
    ) -> List[str]:
        """Enhanced datetime column detection with sampling."""
        raise NotImplementedError

    def estimate_memory_usage(
        self, 
        source: SourceLike, 
        *, 
        sample_ratio: float = 0.01
    ) -> MemoryEstimate:
        """Estimate memory requirements for loading."""
        raise NotImplementedError

    # -----------------------
    # Format-specific loaders (6 core formats)
    # -----------------------
    def load_csv(
        self,
        source: SourceLike,
        *,
        params: Optional[CsvParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
        date_columns: Optional[List[str]] = None,
        chunksize: Optional[int] = None,
        encoding: Optional[str] = None,
        compression: CompressionType = "infer",
    ) -> Union["pd.DataFrame", Iterator["pd.DataFrame"]]:
        """Enhanced CSV/TSV loader with advanced parameter detection."""
        raise NotImplementedError

    def load_excel(
        self,
        source: SourceLike,
        *,
        params: Optional[ExcelParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        """Enhanced Excel loader with intelligent sheet selection."""
        raise NotImplementedError

    def load_json(
        self,
        source: SourceLike,
        *,
        params: Optional[JsonParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        """Enhanced JSON loader with advanced flattening and path extraction."""
        raise NotImplementedError

    def load_jsonl(
        self,
        source: SourceLike,
        *,
        chunksize: Optional[int] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> Union["pd.DataFrame", Iterator["pd.DataFrame"]]:
        """Load JSON Lines format files with streaming support."""
        raise NotImplementedError

    def load_parquet(
        self,
        source: SourceLike,
        *,
        columns: Optional[List[str]] = None,
        filters: Optional[List] = None,
        engine: str = "auto",
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        """Load Parquet files with column selection and filtering."""
        raise NotImplementedError

    def load_google_sheets(
        self,
        url: str,
        *,
        sheet_id: Optional[Union[str, int]] = None,
        format: Literal["csv", "xlsx"] = "csv",
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        """
        Load data from Google Sheets URL.
        
        Args:
            url: Google Sheets URL (edit or view link)
            sheet_id: Specific sheet ID/name (gid parameter)
            format: Export format - 'csv' or 'xlsx'
            dtype_overrides: Custom data types for columns
            
        Returns:
            Loaded DataFrame
            
        Example:
            # Full spreadsheet URL
            df = loader.load_google_sheets(
                "https://docs.google.com/spreadsheets/d/abc123/edit"
            )
            
            # Specific sheet by gid
            df = loader.load_google_sheets(
                "https://docs.google.com/spreadsheets/d/abc123/edit",
                sheet_id="123456789"
            )
            
            # Export as Excel format
            df = loader.load_google_sheets(url, format="xlsx")
        """
        raise NotImplementedError

    # -----------------------
    # URL & Database Integration
    # -----------------------
    def load_from_url(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        kind: Kind = "auto",
        options: Optional[LoadOptions] = None,
    ) -> "pd.DataFrame":
        """Load data from HTTP/HTTPS URL with authentication."""
        raise NotImplementedError

    def load_from_database(
        self,
        query: str,
        connection,
        *,
        chunksize: Optional[int] = None,
        options: Optional[LoadOptions] = None,
    ) -> Union["pd.DataFrame", Iterator["pd.DataFrame"]]:
        """Load data from database query."""
        raise NotImplementedError

    # -----------------------
    # Data Quality & Validation (Assessment Only - No Transformation)
    # -----------------------
    def validate_data(
        self,
        df: "pd.DataFrame",
        *,
        schema: Optional[Dict[str, Any]] = None,
        validation_level: ValidationLevel = ValidationLevel.BASIC,
    ) -> ValidationReport:
        """Comprehensive data validation against schema and quality checks."""
        raise NotImplementedError

    def analyze_data_quality(
        self, 
        df: "pd.DataFrame",
        *,
        include_profiling: bool = True,
    ) -> DataQualityReport:
        """Analyze data quality and provide recommendations."""
        raise NotImplementedError

    def profile_dataset(
        self,
        df: "pd.DataFrame",
        *,
        include_correlations: bool = False,
        sample_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate comprehensive dataset profile."""
        raise NotImplementedError

    # -----------------------
    # Enhanced Datetime utilities
    # -----------------------
    def parse_datetimes(
        self,
        df: "pd.DataFrame",
        cols: List[str],
        *,
        tz_source: Optional[str] = None,
        tz_target: Optional[str] = "UTC",
        dayfirst: bool = False,
        infer: bool = True,
        custom_parser: Optional[Callable] = None,
    ) -> "pd.DataFrame":
        """Enhanced datetime parsing with timezone support and custom parsers."""
        raise NotImplementedError

    def standardize_timezones(
        self,
        df: "pd.DataFrame",
        *,
        tz_columns: List[str],
        target_tz: str = "UTC",
    ) -> "pd.DataFrame":
        """Standardize timezone handling across datetime columns."""
        raise NotImplementedError

    def detect_time_patterns(
        self,
        df: "pd.DataFrame",
        *,
        datetime_col: str,
    ) -> Dict[str, Any]:
        """Detect patterns in time series data."""
        raise NotImplementedError

    # -----------------------
    # Utility Methods
    # -----------------------
    def flatten_json(
        self,
        obj: Any,
        *,
        record_path: Optional[Union[str, List[str]]] = None,
        meta: Optional[List[str]] = None,
        max_level: int = 10,
    ) -> "pd.DataFrame":
        """Enhanced JSON flattening with level control."""
        raise NotImplementedError

    def sample_data(
        self,
        source: SourceLike,
        *,
        n_rows: int = 1000,
        kind: Kind = "auto",
    ) -> "pd.DataFrame":
        """Load a sample of data for analysis."""
        raise NotImplementedError

    def get_source_info(self, source: SourceLike) -> Dict[str, Any]:
        """Get metadata about the data source."""
        raise NotImplementedError

    # -----------------------
    # Configuration & Caching
    # -----------------------
    def save_config(self, path: PathLike, options: LoadOptions) -> None:
        """Save loading configuration to file."""
        raise NotImplementedError

    def load_config(self, path: PathLike) -> LoadOptions:
        """Load configuration from file."""
        raise NotImplementedError

    def clear_cache(self) -> None:
        """Clear detection cache (not processing cache - DataLoader doesn't process)."""
        raise NotImplementedError

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache usage statistics."""
        raise NotImplementedError

    # -----------------------
    # Enhanced Reporting
    # -----------------------
    def build_report(self) -> LoadReport:
        """Build comprehensive loading and quality assessment report."""
        raise NotImplementedError

    def export_report(
        self, 
        report: LoadReport, 
        path: PathLike, 
        format: str = "json"
    ) -> None:
        """Export report to file (JSON, YAML, HTML)."""
        raise NotImplementedError

    def compare_datasets(
        self,
        df1: "pd.DataFrame",
        df2: "pd.DataFrame",
        *,
        include_values: bool = False,
    ) -> Dict[str, Any]:
        """Compare two datasets and generate comparison report."""
        raise NotImplementedError

    # -----------------------
    # Error Handling & Recovery
    # -----------------------
    def load_with_fallback(
        self,
        source: SourceLike,
        *,
        fallback_options: List[LoadOptions],
    ) -> Tuple["pd.DataFrame", LoadReport]:
        """Load with fallback strategies on failure."""
        raise NotImplementedError

    def recover_from_errors(
        self,
        source: SourceLike,
        *,
        error_strategy: str = "skip_bad_lines",
        max_errors: Optional[int] = None,
    ) -> Tuple["pd.DataFrame", List[str]]:
        """Attempt to recover data from corrupted files."""
        raise NotImplementedError

    # -----------------------
    # Private/Internal Methods
    # -----------------------
    def _detect_file_format(self, source: SourceLike) -> Kind:
        """
        Internal format detection logic for 6 supported formats.
        
        Detection priority:
        1. Google Sheets URLs (by URL pattern)
        2. File extension (.csv, .xlsx, .json, .jsonl, .parquet)
        3. Content sniffing (for ambiguous cases)
        4. Magic bytes detection
        """
        raise NotImplementedError

    def _validate_source(self, source: SourceLike) -> bool:
        """Internal source validation."""
        raise NotImplementedError

    def _optimize_loading_strategy(
        self, 
        source: SourceLike, 
        options: LoadOptions
    ) -> LoadOptions:
        """Internal optimization of loading parameters."""
        raise NotImplementedError

    def _update_report(self, **kwargs) -> None:
        """Internal method to update loading report."""
        raise NotImplementedError

    def _detect_google_sheets_url(self, source: SourceLike) -> bool:
        """Internal method to detect if source is a Google Sheets URL."""
        raise NotImplementedError

    def _handle_loading_error(
        self, 
        error: Exception, 
        source: SourceLike, 
        context: str
    ) -> None:
        """Internal error handling and logging."""
        raise NotImplementedError

    def _update_report(self, **kwargs) -> None:
        """Internal method to update loading report."""
        raise NotImplementedError