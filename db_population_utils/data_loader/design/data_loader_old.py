# db_population_utils/data_loader.py

"""
DataLoader Module - Optimized Main Data Loading Interface

This module provides the main DataLoader class that orchestrates all specialized
loaders and provides a unified interface for loading data from multiple formats.

Key Design Philosophy:
    - **Delegation**: Main class delegates to specialized loaders
    - **Unified Interface**: Single point of entry for all formats
    - **Intelligence**: Automatic format detection and optimization
    - **Comprehensive**: Complete operations with full reporting
    - **Manager Requirements**: Exactly 10 methods + 3 comprehensive operations

Architecture Overview:
    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
    │   Data Sources   │───▶│    DataLoader    │───▶│   Processed Data    │
    │                  │    │                  │    │                     │
    │ • CSV Files      │    │ • Format Router  │    │ • Clean DataFrames  │
    │ • Excel Files    │    │ • Specialized    │    │ • Quality Reports   │
    │ • JSON Files     │    │   Delegators     │    │ • Performance       │
    │                  │    │ • Comprehensive  │    │   Metrics           │
    └──────────────────┘    │   Operations     │    └─────────────────────┘
                            └──────────────────┘
                                     │
                            ┌──────────────────┐
                            │   Specialized    │
                            │     Loaders      │
                            │                  │
                            │ • CsvLoader      │
                            │ • ExcelLoader    │
                            │ • JsonLoader     │
                            └──────────────────┘

Manager Requirements Implementation:
    ✓ Loading Functions (5): load(), load_csv(), load_excel(), load_json(), parse_datetimes()
    ✓ Detection Functions (3): detect_format(), detect_encoding(), sniff_csv_params()
    ✓ Performance (1): estimate_memory_usage()
    ✓ Reporting & Error Handling (2): build_report(), detect_time_columns()
    ✓ Comprehensive Operations (3): Enhanced single-call workflows
    ✓ Total: 10 core methods + 3 comprehensive operations
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, Literal
from pathlib import Path
import logging
import time
import os

# Type-only imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd

# Import specialized loaders
from .csv_loader import CsvLoader, CsvParams, CsvLoadReport
from .excel_loader import ExcelLoader, ExcelParams, ExcelLoadReport
from .json_loader import JsonLoader, JsonParams, JsonLoadReport
from .base_loader import (
    BaseLoader, LoadStrategy, MemoryEstimate, DataQualityReport,
    DataLoaderError, DetectionError, UnsupportedFormatError, LoadingMemoryError
)

# Type definitions
PathLike = Union[str, Path]
Kind = Literal["auto", "csv", "tsv", "excel", "json"]
CompressionType = Literal["infer", "gzip", "bz2", "zip", None]


@dataclass
class LoadOptions:
    """High-level loading configuration options."""
    # Format detection
    kind: Kind = "auto"
    encoding: Optional[str] = None
    compression: CompressionType = "infer"
    
    # Performance options
    chunksize: Optional[int] = None
    nrows: Optional[int] = None
    low_memory: bool = True
    dtype_overrides: Optional[Dict[str, Any]] = None
    
    # CSV/TSV specific
    delimiter: Optional[str] = None
    decimal: Optional[str] = None
    header: Optional[Union[int, List[int]]] = None
    
    # Excel specific
    sheet: Union[str, int, Literal["auto"], None] = "auto"
    
    # JSON specific
    flatten_json: bool = True
    record_path: Optional[Union[str, List[str]]] = None
    
    # Datetime handling
    date_columns: Optional[List[str]] = None
    detect_time_columns: bool = False  # Disabled by default until fully implemented
    infer_datetime_format: bool = True
    
    # Error handling
    on_bad_lines: str = "error"
    error_tolerance: float = 0.0
    
    # Performance strategy
    load_strategy: LoadStrategy = LoadStrategy.PERFORMANCE


@dataclass
class LoadReport:
    """Comprehensive loading report from main DataLoader."""
    # Basic info
    source: str
    kind: Kind
    load_strategy: LoadStrategy
    
    # Detection results
    encoding: Optional[str] = None
    compression_detected: Optional[str] = None
    format_confidence: float = 0.0
    
    # Format-specific parameters
    csv_params: Optional[CsvParams] = None
    excel_params: Optional[ExcelParams] = None
    json_params: Optional[JsonParams] = None
    
    # Data characteristics  
    shape: Optional[Tuple[int, int]] = None
    columns_detected: List[str] = field(default_factory=list)
    data_types: Dict[str, str] = field(default_factory=dict)
    
    # Datetime processing
    detected_time_cols: List[str] = field(default_factory=list)
    datetime_parsing_success_rate: Dict[str, float] = field(default_factory=dict)
    
    # Quality assessment
    data_quality: Optional[DataQualityReport] = None
    
    # Performance metrics
    load_time_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    rows_processed: int = 0
    processing_speed_rows_per_sec: float = 0.0
    
    # Issues and recommendations
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    
    # Source metadata
    file_size_bytes: Optional[int] = None
    source_accessible: bool = True


class DataLoader:
    """
    Main DataLoader - Unified interface for intelligent data loading.

    This class provides the main interface for loading data from CSV, Excel, and JSON
    files with automatic format detection, parameter optimization, and comprehensive
    reporting. It delegates to specialized loaders while maintaining a simple API.

    Manager Requirements Implementation (10 Core Methods):
      ✓ Loading Functions (5): load(), load_csv(), load_excel(), load_json(), parse_datetimes()
      ✓ Detection Functions (3): detect_format(), detect_encoding(), sniff_csv_params()
      ✓ Performance (1): estimate_memory_usage()
      ✓ Reporting & Error Handling (2): build_report(), detect_time_columns()

    Supported Formats:
      - CSV/TSV: 95% usage (CRITICAL) - Advanced parameter detection
      - Excel: 80% usage (HIGH) - Intelligent sheet selection  
      - JSON: 70% usage (MEDIUM) - Structure flattening
    """

    def __init__(
        self,
        verbose: bool = True,
        max_memory_usage_gb: float = 4.0,
        default_encoding: str = 'utf-8',
        logger: Optional[logging.Logger] = None,
        load_strategy: LoadStrategy = LoadStrategy.PERFORMANCE,
    ):
        """
        Initialize DataLoader with specialized loaders.
        
        Args:
            verbose: Enable detailed logging during operations
            max_memory_usage_gb: Maximum memory usage limit
            default_encoding: Default text encoding
            logger: Custom logger instance
            load_strategy: Default loading strategy
        """
        self.verbose = verbose
        self.max_memory_usage_gb = max_memory_usage_gb
        self.default_encoding = default_encoding
        self.logger = logger or logging.getLogger(__name__)
        self.load_strategy = load_strategy
        
        # Initialize specialized loaders
        self.csv_loader = CsvLoader(verbose, max_memory_usage_gb, default_encoding, logger)
        self.excel_loader = ExcelLoader(verbose, max_memory_usage_gb, logger)
        self.json_loader = JsonLoader(verbose, max_memory_usage_gb, logger, default_encoding)
        
        # Internal state for reporting
        self._current_report: Optional[LoadReport] = None
        self._start_time: Optional[float] = None
        
        if self.verbose:
            self.logger.info("DataLoader initialized with specialized loaders")

    # -----------------------
    # LOADING FUNCTIONS (5 methods - Manager Requirements)
    # -----------------------
    
    def load(
        self,
        source: PathLike,
        *,
        # Format detection
        kind: Kind = "auto",
        encoding: Optional[str] = None,
        
        # Common options with safe defaults
        detect_time_columns: bool = False,  # Safe default - disabled
        delimiter: Optional[str] = None,    # Auto-detect for CSV
        sheet: Union[str, int, None] = 0,   # First sheet for Excel
        
        # Advanced options (backward compatibility)
        options: Optional[LoadOptions] = None,
    ) -> "pd.DataFrame":
        """
        🎯 Simplified main loading method - works out of the box!
        
        Args:
            source: File path to load
            kind: Format type ('auto', 'csv', 'excel', 'json') 
            encoding: File encoding (auto-detected if None)
            detect_time_columns: Enable datetime detection (disabled by default)
            delimiter: CSV delimiter (auto-detected if None)
            sheet: Excel sheet to load (0 = first sheet)
            options: Advanced LoadOptions (optional, for complex cases)
            
        Returns:
            DataFrame loaded with sensible defaults
            
        Examples:
            # Simple usage - just works!
            df = loader.load("data.csv")
            
            # With basic options
            df = loader.load("data.csv", encoding="utf-8", delimiter=";")
            
            # Excel with specific sheet
            df = loader.load("report.xlsx", sheet="Summary")
        """
        
        Args:
            source: Local file path
            kind: Format type ('auto', 'csv', 'excel', 'json')
            options: Loading configuration options
            
        Returns:
            Raw DataFrame loaded as-is (no transformations applied)
            
        Raises:
            DataLoaderError: On loading failures
            UnsupportedFormatError: For unsupported formats
        """
        source_str = str(source)
        
        # Create LoadOptions from simple parameters (if not provided)
        if options is None:
            options = LoadOptions(
                kind=kind,
                encoding=encoding,
                detect_time_columns=detect_time_columns,
                delimiter=delimiter,
                sheet=sheet,
            )
        
        # Initialize report tracking
        self._start_time = time.time()
        self._current_report = LoadReport(
            source=source_str,
            kind=kind,
            load_strategy=options.load_strategy
        )
        
        try:
            # Validate source
            if not Path(source_str).exists():
                raise DataLoaderError(f"Source file not found: {source_str}")
            
            # Detect format if auto
            if kind == "auto":
                detected_kind, confidence = self.detect_format(source_str)
                kind = detected_kind
                self._current_report.format_confidence = confidence
                
                if self.verbose:
                    self.logger.info(f"Auto-detected format: {kind} (confidence: {confidence:.2f})")
            
            # Update report
            self._current_report.kind = kind
            
            # Delegate to appropriate loader
            if kind in ["csv", "tsv"]:
                df = self._load_via_csv_loader(source_str, options)
            elif kind == "excel":
                df = self._load_via_excel_loader(source_str, options)
            elif kind == "json":
                df = self._load_via_json_loader(source_str, options)
            else:
                raise UnsupportedFormatError(f"Unsupported format: {kind}")
            
            # Post-process if needed
            if options.detect_time_columns and not df.empty:
                time_cols = self.detect_time_columns(df)
                if time_cols and options.infer_datetime_format:
                    df = self.parse_datetimes(df, time_cols)
                    self._current_report.detected_time_cols = time_cols
            
            # Update final report metrics
            self._update_final_report_metrics(df)
            
            if self.verbose:
                self.logger.info(f"✅ Successfully loaded {df.shape[0]:,} rows × {df.shape[1]} columns")
            
            return df
            
        except Exception as e:
            if self._current_report:
                self._current_report.errors.append(str(e))
            self.logger.error(f"Loading failed for {source_str}: {e}")
            raise DataLoaderError(f"Failed to load {source_str}: {str(e)}") from e

    def load_csv(
        self,
        source: PathLike,
        *,
        params: Optional[CsvParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
        date_columns: Optional[List[str]] = None,
        chunksize: Optional[int] = None,
        encoding: Optional[str] = None,
        compression: CompressionType = "infer",
    ) -> Union["pd.DataFrame", Iterator["pd.DataFrame"]]:
        """
        CSV/TSV loader with advanced parameter detection.
        
        Manager Priority: CRITICAL for 95% usage CSV format.
        
        Args:
            source: CSV file path
            params: CSV parameters (auto-detected if None)
            dtype_overrides: Custom data types for columns
            date_columns: Columns to parse as dates
            chunksize: Process in chunks (returns iterator)
            encoding: Text encoding (auto-detected if None)
            compression: Compression format
            
        Returns:
            DataFrame or iterator of DataFrames (if chunked)
        """
        return self.csv_loader.load_csv(
            str(source),
            params=params,
            dtype_overrides=dtype_overrides,
            date_columns=date_columns,
            chunksize=chunksize,
            compression=compression
        )

    def load_excel(
        self,
        source: PathLike,
        *,
        params: Optional[ExcelParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        """
        Excel loader with intelligent sheet selection.
        
        Manager Priority: HIGH for 80% usage Excel format.
        
        Args:
            source: Excel file path (.xlsx, .xls)
            params: Excel parameters (auto-detected if None)
            dtype_overrides: Custom data types for columns
            
        Returns:
            DataFrame from selected/detected sheet
        """
        return self.excel_loader.load_excel(
            str(source),
            params=params,
            dtype_overrides=dtype_overrides
        )

    def load_json(
        self,
        source: PathLike,
        *,
        params: Optional[JsonParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        """
        JSON loader with advanced flattening.
        
        Manager Priority: MEDIUM for 70% usage JSON format.
        
        Args:
            source: JSON file path
            params: JSON parameters (auto-detected if None)
            dtype_overrides: Custom data types for columns
            
        Returns:
            DataFrame with flattened JSON structure
        """
        return self.json_loader.load_json(
            str(source),
            params=params,
            dtype_overrides=dtype_overrides
        )

    def parse_datetimes(
        self,
        df: "pd.DataFrame",
        cols: Optional[List[str]] = None,
        *,
        infer: bool = True,
        dayfirst: bool = False,
        errors: str = 'coerce',
        format: Optional[str] = None,
    ) -> "pd.DataFrame":
        """
        Parse datetime columns with intelligent detection and error handling.
        
        Priority: CRITICAL - "can cause lots of troubles and can be pretty common"
        
        Args:
            df: DataFrame with columns to parse
            cols: Specific columns to parse (if None, auto-detect)
            infer: Automatically infer datetime format
            dayfirst: Interpret first value as day
            errors: How to handle parsing errors ('raise', 'coerce', 'ignore')
            format: Explicit datetime format string
            
        Returns:
            DataFrame with parsed datetime columns
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for datetime parsing")
        
        if df.empty:
            return df
        
        df_copy = df.copy()
        
        # Auto-detect columns if not specified
        if cols is None:
            cols = self.detect_time_columns(df_copy)
        
        if not cols:
            if self.verbose:
                self.logger.info("No datetime columns detected")
            return df_copy
        
        success_rates = {}
        
        for col in cols:
            if col not in df_copy.columns:
                if self.verbose:
                    self.logger.warning(f"Column '{col}' not found in DataFrame")
                continue
            
            try:
                original_nulls = df_copy[col].isnull().sum()
                
                # Apply datetime parsing
                if format:
                    df_copy[col] = pd.to_datetime(df_copy[col], format=format, errors=errors)
                else:
                    df_copy[col] = pd.to_datetime(
                        df_copy[col], 
                        infer_datetime_format=infer,
                        dayfirst=dayfirst,
                        errors=errors
                    )
                
                # Calculate success rate
                new_nulls = df_copy[col].isnull().sum()
                failed_conversions = new_nulls - original_nulls
                total_attempts = len(df_copy) - original_nulls
                
                if total_attempts > 0:
                    success_rate = (total_attempts - failed_conversions) / total_attempts
                    success_rates[col] = success_rate
                    
                    if self.verbose:
                        self.logger.info(f"Parsed datetime column '{col}': {success_rate:.1%} success rate")
                
            except Exception as e:
                success_rates[col] = 0.0
                if self.verbose:
                    self.logger.warning(f"Failed to parse datetime column '{col}': {e}")
        
        # Update report if available
        if self._current_report:
            self._current_report.datetime_parsing_success_rate = success_rates
        
        return df_copy

    # -----------------------
    # DETECTION FUNCTIONS (3 methods - Manager Requirements)
    # -----------------------
    
    def detect_format(self, source: PathLike) -> Tuple[Kind, float]:
        """
        Auto-detect file format with confidence score.
        
        Manager Priority: Essential for unified loading interface.
        
        Args:
            source: File path
            
        Returns:
            Tuple of (detected_format, confidence_score)
        """
        source_str = str(source)
        source_path = Path(source_str)
        
        if not source_path.exists():
            raise DataLoaderError(f"Source file not found: {source_str}")
        
        # Primary detection by file extension
        extension = source_path.suffix.lower()
        
        format_map = {
            '.csv': ('csv', 0.9),
            '.tsv': ('tsv', 0.9),
            '.txt': ('csv', 0.6),  # Could be CSV
            '.xlsx': ('excel', 0.95),
            '.xls': ('excel', 0.95),
            '.json': ('json', 0.9),
            '.jsonl': ('json', 0.85),
            '.ndjson': ('json', 0.85)
        }
        
        if extension in format_map:
            detected_format, confidence = format_map[extension]
            
            # Verify with content analysis for ambiguous cases
            if confidence < 0.9:
                content_format, content_confidence = self._detect_format_by_content(source_str)
                if content_confidence > confidence:
                    detected_format, confidence = content_format, content_confidence
            
            if self.verbose:
                self.logger.info(f"Format detected: {detected_format} (confidence: {confidence:.2f})")
            
            return detected_format, confidence
        
        # Fallback to content-based detection
        detected_format, confidence = self._detect_format_by_content(source_str)
        
        if self.verbose:
            if confidence > 0.5:
                self.logger.info(f"Format detected by content: {detected_format} (confidence: {confidence:.2f})")
            else:
                self.logger.warning(f"Format detection uncertain: {detected_format} (confidence: {confidence:.2f})")
        
        return detected_format, confidence

    def detect_encoding(
        self, 
        source: PathLike, 
        *, 
        sample_size: int = 20000,
        confidence_threshold: float = 0.8
    ) -> Tuple[str, float]:
        """
        Critical encoding detection with confidence score.
        
        Priority: CRITICAL - "encoding might cause nasty problems, based on our experience"
        
        Args:
            source: File path
            sample_size: Number of bytes to sample for detection
            confidence_threshold: Minimum confidence for successful detection
            
        Returns:
            Tuple of (detected_encoding, confidence_score)
        """
        # Delegate to CSV loader for most reliable encoding detection
        return self.csv_loader.detect_encoding(
            str(source), 
            sample_size=sample_size,
            confidence_threshold=confidence_threshold
        )

    def sniff_csv_params(
        self, 
        source: PathLike, 
        *, 
        sample_size: int = 20000
    ) -> CsvParams:
        """
        Auto-detect CSV parameters with advanced sniffing.
        
        Manager Priority: Essential for 95% usage CSV format.
        
        Args:
            source: CSV file path
            sample_size: Number of bytes to sample for detection
            
        Returns:
            CsvParams with detected parameters and confidence scores
        """
        return self.csv_loader.sniff_csv_params(str(source), sample_size=sample_size)

    # -----------------------
    # PERFORMANCE (1 method - Manager Requirements)
    # -----------------------
    
    def estimate_memory_usage(
        self, 
        source: PathLike, 
        *, 
        sample_ratio: float = 0.01
    ) -> MemoryEstimate:
        """
        Estimate memory requirements for loading files.
        
        Priority: Essential for large file handling.
        
        Args:
            source: File path
            sample_ratio: Ratio of file to sample for estimation
            
        Returns:
            MemoryEstimate with usage prediction and recommendations
        """
        source_str = str(source)
        
        # Detect format first
        detected_format, _ = self.detect_format(source_str)
        
        # Delegate to appropriate specialized loader
        if detected_format in ["csv", "tsv"]:
            return self.csv_loader.estimate_csv_memory_usage(source_str, sample_ratio=sample_ratio)
        elif detected_format == "excel":
            return self.excel_loader.estimate_excel_memory_usage(source_str)
        elif detected_format == "json":
            return self.json_loader.estimate_json_memory_usage(source_str)
        else:
            # Generic estimation
            file_size_mb = Path(source_str).stat().st_size / 1024 / 1024
            estimated_memory_mb = file_size_mb * 3  # Conservative 3x multiplier
            
            return MemoryEstimate(
                estimated_memory_mb=estimated_memory_mb,
                can_load_in_memory=estimated_memory_mb <= (self.max_memory_usage_gb * 1024)
            )

    # -----------------------
    # REPORTING & ERROR HANDLING (2 methods - Manager Requirements)
    # -----------------------
    
    def build_report(self) -> LoadReport:
        """
        Generate comprehensive load reports.
        
        Priority: Essential for monitoring and debugging.
        
        Returns:
            LoadReport with comprehensive loading metrics and analysis
        """
        if self._current_report is None:
            # Create empty report if no loading operation in progress
            return LoadReport(source="", kind="auto", load_strategy=self.load_strategy)
        
        # Finalize report with any remaining metrics
        if self._start_time:
            self._current_report.load_time_seconds = time.time() - self._start_time
        
        return self._current_report

    def detect_time_columns(
        self,
        df: "pd.DataFrame",
        *,
        hints: Optional[List[str]] = None,
        min_parse_rate: float = 0.8,
        sample_size: Optional[int] = None,
    ) -> List[str]:
        """
        Datetime detection - identify potential datetime columns.
        
        Priority: Essential for parse_datetimes() functionality.
        
        Args:
            df: DataFrame to analyze
            hints: Column name hints for datetime detection
            min_parse_rate: Minimum successful parse rate for detection
            sample_size: Number of rows to sample (None for all)
            
        Returns:
            List of column names likely to contain datetime data
        """
        if df.empty:
            return []
        
        datetime_columns = []
        
        # Common datetime column name patterns
        datetime_patterns = [
            'date', 'time', 'timestamp', 'created', 'updated', 'modified',
            'start', 'end', 'expire', 'valid', 'publish', '_at', '_on',
            'birth', 'death', 'event', 'occur'
        ]
        
        # Priority hints if provided
        if hints:
            datetime_patterns = hints + datetime_patterns
        
        # Sample data if needed
        sample_df = df.head(sample_size) if sample_size else df
        
        for col in df.columns:
            col_str = str(col).lower()
            
            # Skip if column is already datetime
            if df[col].dtype.kind == 'M':  # datetime64 type
                datetime_columns.append(col)
                continue
            
            # Skip numeric columns (unless they might be timestamps)
            if df[col].dtype.kind in 'biufc':  # numeric types
                # Check if could be unix timestamp
                if col_str in ['timestamp', 'ts', 'time']:
                    # Check if values are in reasonable timestamp range
                    sample_values = sample_df[col].dropna()
                    if len(sample_values) > 0:
                        min_val, max_val = sample_values.min(), sample_values.max()
                        # Unix timestamp range: 1970-2050 (roughly)
                        if 0 < min_val < 4000000000 and max_val < 4000000000:
                            datetime_columns.append(col)
                continue
            
            # Check column name patterns
            name_score = 0
            for pattern in datetime_patterns:
                if pattern in col_str:
                    name_score += 1
                    break
            
            # Skip if no name hint and not object/string type
            if name_score == 0 and df[col].dtype.name not in ['object', 'string']:
                continue
            
            # Test actual datetime parsing
            sample_values = sample_df[col].dropna().head(100)
            if len(sample_values) == 0:
                continue
            
            # Use base loader's datetime pattern detection
            detection_result = self.csv_loader.detect_datetime_patterns(sample_values.astype(str).tolist())
            
            parse_success_rate = detection_result.get('parse_success_rate', 0.0)
            
            # Decide based on name hints and parse success
            if name_score > 0 and parse_success_rate >= min_parse_rate * 0.7:  # Lower threshold for name hints
                datetime_columns.append(col)
            elif parse_success_rate >= min_parse_rate:
                datetime_columns.append(col)
        
        if self.verbose and datetime_columns:
            self.logger.info(f"Detected datetime columns: {datetime_columns}")
        
        return datetime_columns

    # -----------------------
    # COMPREHENSIVE SINGLE-CALL OPERATIONS (3 methods)
    # -----------------------

    def load_with_comprehensive_report(
        self,
        source: PathLike,
        *,
        kind: Kind = "auto",
        options: Optional[LoadOptions] = None,
        include_quality_analysis: bool = True,
        include_datetime_detection: bool = True,
    ) -> Tuple["pd.DataFrame", LoadReport]:
        """
        COMPREHENSIVE: Load data with full detection, quality analysis, and reporting.
        
        Combines: detect_format() + detect_encoding() + load() + detect_time_columns() + 
                  parse_datetimes() + analyze_data_quality() + build_report() + error handling
        
        Args:
            source: File path
            kind: Format type or 'auto' for detection
            options: Loading configuration options
            include_quality_analysis: Perform data quality assessment
            include_datetime_detection: Detect and parse datetime columns
            
        Returns:
            Tuple of (loaded_dataframe, comprehensive_report)
        """
        source_str = str(source)
        options = options or LoadOptions()
        
        # Enable comprehensive options
        if include_datetime_detection:
            options.detect_time_columns = True
            options.infer_datetime_format = True
        
        # Load with standard method (already comprehensive)
        df = self.load(source_str, kind=kind, options=options)
        
        # Add quality analysis if requested
        if include_quality_analysis and not df.empty:
            quality_report = self._analyze_comprehensive_quality(df)
            if self._current_report:
                self._current_report.data_quality = quality_report
        
        # Generate optimization suggestions
        if self._current_report:
            file_info = self._get_file_info(source_str)
            memory_estimate = self.estimate_memory_usage(source_str)
            performance_metrics = self._get_performance_metrics()
            
            suggestions = self._generate_optimization_suggestions(file_info, memory_estimate, performance_metrics)
            self._current_report.optimization_suggestions = suggestions
        
        report = self.build_report()
        
        if self.verbose:
            self._log_comprehensive_summary(report)
        
        return df, report

    def load_csv_with_smart_detection(
        self,
        source: PathLike,
        *,
        auto_fix_common_issues: bool = True,
        return_detection_details: bool = True,
    ) -> Tuple["pd.DataFrame", Dict[str, Any]]:
        """
        COMPREHENSIVE: CSV loading with smart detection and issue fixing.
        
        Combines: detect_encoding() + sniff_csv_params() + load_csv() + 
                  error recovery + issue detection + reporting
        
        Manager Priority: CRITICAL for 95% usage CSV format.
        
        Args:
            source: CSV file path
            auto_fix_common_issues: Automatically fix common CSV issues
            return_detection_details: Return detailed detection information
            
        Returns:
            Tuple of (loaded_dataframe, detection_and_issues_report)
        """
        # Delegate to specialized CSV loader
        df, csv_report = self.csv_loader.load_csv_with_smart_detection(
            str(source),
            auto_fix_common_issues=auto_fix_common_issues,
            return_detection_details=return_detection_details
        )
        
        # Convert CSV report to dictionary format
        detection_details = {
            "csv_params": {
                "delimiter": csv_report.detected_params.delimiter if csv_report.detected_params else ",",
                "encoding": csv_report.encoding_detection.get("detected", "utf-8"),
                "header": csv_report.detected_params.header if csv_report.detected_params else 0,
                "confidence_scores": {
                    "delimiter": csv_report.detected_params.delimiter_confidence if csv_report.detected_params else 0.0,
                    "encoding": csv_report.encoding_detection.get("confidence", 0.0)
                }
            },
            "encoding": csv_report.encoding_detection,
            "issues_detected": csv_report.issues_detected,
            "issues_fixed": csv_report.issues_fixed,
            "issues_remaining": csv_report.issues_remaining,
            "data_quality": csv_report.data_quality.__dict__ if csv_report.data_quality else {},
            "performance": {
                "load_time_seconds": csv_report.load_time_seconds,
                "memory_usage_mb": csv_report.memory_usage_mb,
                "processing_speed": csv_report.processing_speed_rows_per_sec
            }
        }
        
        return df, detection_details

    def load_with_fallback_strategies(
        self,
        source: PathLike,
        *,
        max_attempts: int = 3,
        enable_error_recovery: bool = True,
    ) -> Tuple["pd.DataFrame", Dict[str, Any]]:
        """
        COMPREHENSIVE: Load data with multiple fallback strategies on failure.
        
        Combines: detect_format() + load() + error recovery + fallback strategies + 
                  partial loading + comprehensive error reporting
        
        Args:
            source: File path
            max_attempts: Maximum number of fallback attempts
            enable_error_recovery: Enable partial data recovery on errors
            
        Returns:
            Tuple of (loaded_dataframe, recovery_report)
        """
        source_str = str(source)
        recovery_report = {
            "attempts_made": 0,
            "strategies_tried": [],
            "final_status": "failed",
            "recovery_percentage": 0.0,
            "errors_encountered": [],
            "fallback_details": []
        }
        
        # Strategy 1: Standard loading
        try:
            recovery_report["attempts_made"] += 1
            recovery_report["strategies_tried"].append("standard_loading")
            
            df = self.load(source_str)
            
            recovery_report["final_status"] = "success_standard"
            recovery_report["recovery_percentage"] = 100.0
            
            return df, recovery_report
            
        except Exception as e:
            recovery_report["errors_encountered"].append(f"Standard loading: {str(e)}")
            
            if recovery_report["attempts_made"] >= max_attempts:
                recovery_report["final_status"] = "failed_max_attempts"
                return self._create_empty_dataframe(), recovery_report
        
        # Strategy 2: Format-specific recovery
        try:
            recovery_report["attempts_made"] += 1
            recovery_report["strategies_tried"].append("format_specific_recovery")
            
            detected_format, _ = self.detect_format(source_str)
            
            if detected_format == "csv":
                df, _ = self.load_csv_with_smart_detection(source_str, auto_fix_common_issues=True)
            elif detected_format == "excel":
                df, _ = self.excel_loader.load_excel_with_smart_detection(source_str)
            elif detected_format == "json":
                df, _ = self.json_loader.load_json_with_smart_detection(source_str)
            else:
                raise DataLoaderError(f"No recovery strategy for format: {detected_format}")
            
            recovery_report["final_status"] = "success_recovery"
            recovery_report["recovery_percentage"] = 100.0
            
            return df, recovery_report
            
        except Exception as e:
            recovery_report["errors_encountered"].append(f"Format recovery: {str(e)}")
            
            if recovery_report["attempts_made"] >= max_attempts:
                recovery_report["final_status"] = "failed_max_attempts"
                return self._create_empty_dataframe(), recovery_report
        
        # Strategy 3: Partial recovery (if enabled)
        if enable_error_recovery and recovery_report["attempts_made"] < max_attempts:
            try:
                recovery_report["attempts_made"] += 1
                recovery_report["strategies_tried"].append("partial_recovery")
                
                df = self._attempt_partial_recovery(source_str)
                
                if not df.empty:
                    # Calculate recovery percentage
                    estimated_total = self._estimate_total_rows(source_str)
                    actual_rows = len(df)
                    recovery_percentage = (actual_rows / estimated_total * 100) if estimated_total > 0 else 0
                    
                    recovery_report["final_status"] = "success_partial"
                    recovery_report["recovery_percentage"] = recovery_percentage
                    
                    return df, recovery_report
                
            except Exception as e:
                recovery_report["errors_encountered"].append(f"Partial recovery: {str(e)}")
        
        recovery_report["final_status"] = "failed_all_strategies"
        return self._create_empty_dataframe(), recovery_report

    # -----------------------
    # Private/Internal Methods
    # -----------------------
    
    def _load_via_csv_loader(self, source: str, options: LoadOptions) -> "pd.DataFrame":
        """Load via CSV loader with options mapping."""
        csv_params = CsvParams(
            delimiter=options.delimiter,
            encoding=options.encoding,
            header=options.header,
            decimal=options.decimal
        )
        
        return self.csv_loader.load_csv(
            source,
            params=csv_params,
            dtype_overrides=options.dtype_overrides,
            date_columns=options.date_columns,
            chunksize=options.chunksize,
            compression=options.compression
        )
    
    def _load_via_excel_loader(self, source: str, options: LoadOptions) -> "pd.DataFrame":
        """Load via Excel loader with options mapping."""
        excel_params = ExcelParams(sheet=options.sheet)
        
        return self.excel_loader.load_excel(
            source,
            params=excel_params,
            dtype_overrides=options.dtype_overrides
        )
    
    def _load_via_json_loader(self, source: str, options: LoadOptions) -> "pd.DataFrame":
        """Load via JSON loader with options mapping."""
        json_params = JsonParams(
            record_path=options.record_path,
            flatten_nested=options.flatten_json,
            encoding=options.encoding or self.default_encoding
        )
        
        return self.json_loader.load_json(
            source,
            params=json_params,
            dtype_overrides=options.dtype_overrides
        )
    
    def _detect_format_by_content(self, source: str) -> Tuple[Kind, float]:
        """Detect format by analyzing file content."""
        try:
            # Read a sample of the file
            sample = self.csv_loader.sample_file_content(source, sample_size=5000)
            
            if not sample.strip():
                return "csv", 0.0  # Empty file, default to CSV
            
            # JSON detection
            if sample.strip().startswith(('{', '[')):
                try:
                    import json
                    # Try to parse as JSON
                    json.loads(sample[:1000])  # Try first 1000 chars
                    return "json", 0.8
                except:
                    pass
            
            # JSONL detection
            if '\n' in sample:
                lines = [line.strip() for line in sample.split('\n')[:5] if line.strip()]
                if lines and all(line.startswith('{') for line in lines):
                    return "json", 0.7
            
            # CSV detection (fallback)
            # Count common CSV delimiters
            delimiters = [',', ';', '\t', '|']
            delimiter_counts = {d: sample.count(d) for d in delimiters}
            
            if max(delimiter_counts.values()) > 10:  # Reasonable number of delimiters
                return "csv", 0.6
            
            return "csv", 0.3  # Low confidence fallback
            
        except Exception:
            return "csv", 0.1  # Very low confidence fallback
    
    def _update_final_report_metrics(self, df: "pd.DataFrame") -> None:
        """Update final metrics in current report."""
        if not self._current_report or df is None:
            return
        
        # Basic shape info
        if hasattr(df, 'shape'):
            self._current_report.shape = df.shape
            self._current_report.rows_processed = df.shape[0]
            self._current_report.columns_detected = list(df.columns)
            self._current_report.data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Memory usage
        if hasattr(df, 'memory_usage'):
            self._current_report.memory_usage_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        # Processing speed
        if self._start_time and self._current_report.rows_processed > 0:
            elapsed = time.time() - self._start_time
            self._current_report.processing_speed_rows_per_sec = self._current_report.rows_processed / max(elapsed, 0.001)
        
        # File info
        try:
            file_stat = Path(self._current_report.source).stat()
            self._current_report.file_size_bytes = file_stat.st_size
        except:
            pass
    
    def _analyze_comprehensive_quality(self, df: "pd.DataFrame") -> DataQualityReport:
        """Comprehensive data quality analysis."""
        if df.empty:
            return DataQualityReport(quality_score=0.0)
        
        # Basic metrics
        total_cells = df.shape[0] * df.shape[1]
        null_count = df.isnull().sum().sum()
        missing_ratio = null_count / total_cells if total_cells > 0 else 0
        
        duplicate_rows = df.duplicated().sum()
        
        # Column-level analysis
        unique_values = {col: df[col].nunique() for col in df.columns}
        data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Quality scoring
        completeness_score = (1 - missing_ratio) * 100
        uniqueness_score = (1 - duplicate_rows / len(df)) * 100 if len(df) > 0 else 100
        consistency_score = 100  # Could add more sophisticated consistency checks
        
        overall_score = (completeness_score + uniqueness_score + consistency_score) / 3
        
        # Recommendations
        recommendations = []
        if missing_ratio > 0.1:
            recommendations.append("High missing data ratio - investigate data collection process")
        if duplicate_rows > len(df) * 0.05:
            recommendations.append("Significant duplicate rows detected - consider deduplication")
        if len([col for col in df.columns if df[col].dtype == 'object']) > len(df.columns) * 0.8:
            recommendations.append("Many text columns - consider data type optimization")
        
        return DataQualityReport(
            missing_data_ratio=missing_ratio,
            duplicate_rows=duplicate_rows,
            unique_values_per_column=unique_values,
            data_types_detected=data_types,
            quality_score=overall_score,
            recommendations=recommendations
        )
    
    def _get_file_info(self, source: str) -> Dict[str, Any]:
        """Get file information for optimization suggestions."""
        try:
            path = Path(source)
            stat = path.stat()
            return {
                "file_size_mb": stat.st_size / 1024 / 1024,
                "extension": path.suffix.lower()
            }
        except:
            return {"file_size_mb": 0, "extension": ""}
    
    def _get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        if not self._current_report or not self._start_time:
            return {}
        
        elapsed = time.time() - self._start_time
        return {
            "processing_time": elapsed,
            "rows_per_second": self._current_report.processing_speed_rows_per_sec,
            "memory_usage_mb": self._current_report.memory_usage_mb
        }
    
    def _generate_optimization_suggestions(
        self, 
        file_info: Dict[str, Any], 
        memory_estimate: MemoryEstimate, 
        performance_metrics: Dict[str, float]
    ) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []
        
        file_size_mb = file_info.get("file_size_mb", 0)
        
        if file_size_mb > 100:
            suggestions.append("Large file - consider using chunked loading for better memory efficiency")
        
        if not memory_estimate.can_load_in_memory:
            suggestions.append("File exceeds memory limits - use chunked processing")
        
        processing_speed = performance_metrics.get("rows_per_second", 0)
        if processing_speed > 0 and processing_speed < 1000:
            suggestions.append("Slow processing speed - consider data type optimization")
        
        return suggestions
    
    def _log_comprehensive_summary(self, report: LoadReport) -> None:
        """Log comprehensive loading summary."""
        if not self.verbose:
            return
        
        self.logger.info("=" * 80)
        self.logger.info("COMPREHENSIVE LOADING REPORT")
        self.logger.info("=" * 80)
        self.logger.info(f"📁 Source: {Path(report.source).name}")
        self.logger.info(f"📊 Format: {report.kind} (confidence: {report.format_confidence:.2f})")
        
        if report.shape:
            self.logger.info(f"📏 Shape: {report.shape[0]:,} rows × {report.shape[1]} columns")
        
        self.logger.info(f"⏱️  Load Time: {report.load_time_seconds:.2f} seconds")
        self.logger.info(f"💾 Memory Usage: {report.memory_usage_mb:.1f} MB")
        
        if report.data_quality:
            self.logger.info(f"✨ Quality Score: {report.data_quality.quality_score:.1f}/100")
        
        if report.detected_time_cols:
            self.logger.info(f"🕒 DateTime Columns: {len(report.detected_time_cols)}")
        
        if report.optimization_suggestions:
            self.logger.info("💡 Optimization Suggestions:")
            for suggestion in report.optimization_suggestions:
                self.logger.info(f"   • {suggestion}")
        
        self.logger.info("=" * 80)
    
    def _create_empty_dataframe(self) -> "pd.DataFrame":
        """Create empty DataFrame for fallback scenarios."""
        try:
            import pandas as pd
            return pd.DataFrame()
        except ImportError:
            raise ImportError("pandas is required for DataLoader operations")
    
    def _attempt_partial_recovery(self, source: str) -> "pd.DataFrame":
        """Attempt partial data recovery using various strategies."""
        # This would implement various recovery strategies
        # For now, return empty DataFrame
        return self._create_empty_dataframe()
    
    def _estimate_total_rows(self, source: str) -> int:
        """Estimate total rows in file for recovery percentage calculation."""
        try:
            # Quick estimation based on file size and format
            file_size = Path(source).stat().st_size
            
            # Rough estimates per format
            if source.endswith(('.csv', '.tsv')):
                return max(1, file_size // 100)  # ~100 bytes per row average
            elif source.endswith(('.xlsx', '.xls')):
                return max(1, file_size // 200)  # Excel has more overhead
            elif source.endswith('.json'):
                return max(1, file_size // 300)  # JSON can be verbose
            else:
                return max(1, file_size // 150)  # Generic estimate
        except:
            return 1000  # Fallback estimate