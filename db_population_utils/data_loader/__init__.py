# db_population_utils/data_loader/__init__.py

"""
DataLoader Module - Pure Data Loading Utilities

This module provides comprehensive data loading capabilities with intelligent 
format detection and quality assessment for multiple file formats.

Main Components:
- DataLoader: Core data loading class focused on loading files as-is
- Configuration classes for fine-grained control (CsvParams, LoadOptions, etc.)  
- Report classes for comprehensive quality analysis and loading metrics
- Custom exceptions for robust error handling

Philosophy:
DataLoader is focused on PURE LOADING - getting data from files into pandas 
DataFrames as-is, with quality assessment and reporting. All data transformations
and preprocessing are handled by the separate DataProcessor class.

Usage Examples:
    # Basic usage - load file as-is
    from db_population_utils.data_loader import DataLoader, LoadOptions
    loader = DataLoader(verbose=True, cache_enabled=True)
    df = loader.load("data.csv")  # Raw data, no transformations
    
    # Advanced usage with quality assessment
    options = LoadOptions(validation_level=ValidationLevel.COMPREHENSIVE)
    df = loader.load("data.xlsx", options=options)
    
    # Quick loading with quality profiling
    from db_population_utils.data_loader import quick_load
    df, report = quick_load("data.csv", validation_level=ValidationLevel.BASIC)
    print(f"Quality Score: {report.data_quality.quality_score}/100")
"""

# Enhanced data loading components  
from .data_loader import (
    # Core classes
    DataLoader,
    
    # Configuration classes
    CsvParams,
    ExcelParams,
    JsonParams,
    LoadOptions,
    PreprocessingStep,
    
    # Report classes
    LoadReport,
    DataQualityReport,
    ValidationReport,
    MemoryEstimate,
    StreamingResult,
    
    # Type definitions and enums
    Kind,
    LoadStrategy,
    ValidationLevel,
    SourceLike,
    PathLike,
    PreprocessingStrategy,
    CompressionType,
    
    # Custom exceptions
    DataLoaderError,
    DetectionError,
    ValidationError as DataValidationError,  # Renamed to avoid conflict
    UnsupportedFormatError,
    MemoryError as DataMemoryError,  # Renamed to avoid conflict with builtin
)

# Module metadata
__version__ = "0.2.0"
__author__ = "Your Team"
__description__ = "Advanced data loading utilities with intelligent format detection"

# Public API - only DataLoader related components
__all__ = [
    # Core class
    "DataLoader",
    
    # Configuration classes
    "CsvParams",
    "ExcelParams", 
    "JsonParams",
    "LoadOptions",
    "PreprocessingStep",  # Still used for configuration, but processing happens in DataProcessor
    
    # Report classes
    "LoadReport",
    "DataQualityReport",
    "ValidationReport",
    "MemoryEstimate",
    "StreamingResult",
    
    # Type definitions
    "Kind",
    "LoadStrategy",
    "ValidationLevel",
    "SourceLike",
    "PathLike",
    "PreprocessingStrategy", 
    "CompressionType",
    
    # Data loading exceptions
    "DataLoaderError",
    "DetectionError",
    "DataValidationError",
    "UnsupportedFormatError",
    "DataMemoryError",
    
    # Module info
    "__version__",
    
    # Convenience functions (defined below)
    "create_loader_with_defaults",
    "quick_load",
    "load_with_profile",
]

# DataLoader-specific convenience functions
def create_loader_with_defaults(
    load_strategy: LoadStrategy = LoadStrategy.PERFORMANCE,
    validation_level: ValidationLevel = ValidationLevel.BASIC,
    enable_caching: bool = True,
    max_memory_gb: float = 4.0,
    **kwargs
) -> DataLoader:
    """
    Create DataLoader with sensible defaults for common use cases.
    
    Args:
        load_strategy: Default loading strategy
        validation_level: Default validation level
        enable_caching: Enable detection result caching
        max_memory_gb: Maximum memory usage
        **kwargs: Additional DataLoader arguments
        
    Returns:
        Configured DataLoader instance
        
    Example:
        loader = create_loader_with_defaults(
            load_strategy=LoadStrategy.MEMORY_EFFICIENT,
            validation_level=ValidationLevel.STRICT
        )
    """
    return DataLoader(
        verbose=True,
        cache_enabled=enable_caching,
        max_memory_usage_gb=max_memory_gb,
        load_strategy=load_strategy,
        validation_level=validation_level,
        **kwargs
    )


def quick_load(
    source: SourceLike,
    **load_options
) -> tuple["pd.DataFrame", LoadReport]:
    """
    Quick data loading utility with automatic optimization.
    
    Args:
        source: Data source (file path, URL, etc.)
        **load_options: Options passed to DataLoader and load method
        
    Returns:
        Tuple of (DataFrame, LoadReport)
        
    Example:
        df, report = quick_load(
            "data.csv", 
            validation_level=ValidationLevel.COMPREHENSIVE
        )
    """
    # Extract loader options vs load options
    loader_options = {k: v for k, v in load_options.items() 
                     if k in ['verbose', 'cache_enabled', 'max_memory_usage_gb', 
                             'load_strategy', 'validation_level']}
    
    load_method_options = {k: v for k, v in load_options.items() 
                          if k not in loader_options}
    
    # Create loader
    loader = create_loader_with_defaults(**loader_options)
    
    # Create load options if any specific options provided
    options = LoadOptions(**load_method_options) if load_method_options else None
    
    # Load data
    df = loader.load(source, options=options)
    report = loader.build_report()
    
    return df, report


def load_with_profile(
    source: SourceLike,
    include_quality_analysis: bool = True,
    **load_options
) -> tuple["pd.DataFrame", LoadReport, "DataQualityReport"]:
    """
    Load data with comprehensive profiling and quality analysis.
    
    Args:
        source: Data source
        include_quality_analysis: Include data quality analysis
        **load_options: Options for loading
        
    Returns:
        Tuple of (DataFrame, LoadReport, DataQualityReport)
        
    Example:
        df, load_report, quality_report = load_with_profile(
            "data.csv",
            validation_level=ValidationLevel.COMPREHENSIVE
        )
    """
    # Create loader with profiling enabled
    loader = create_loader_with_defaults(
        validation_level=ValidationLevel.COMPREHENSIVE,
        **load_options
    )
    
    # Load data
    df = loader.load(source)
    load_report = loader.build_report()
    
    # Generate quality analysis
    quality_report = None
    if include_quality_analysis:
        quality_report = loader.analyze_data_quality(df, include_profiling=True)
    
    return df, load_report, quality_report


# Optional: Add logging configuration
import logging
import sys
import warnings

# Set up module logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Check for required dependencies for DataLoader
_DATA_LOADER_DEPENDENCIES = {
    'pandas': "pip install pandas>=1.3.0", 
    'numpy': "pip install numpy>=1.20.0"
}

_OPTIONAL_DATA_DEPENDENCIES = {
    'openpyxl': "pip install openpyxl  # For Excel support",
    'xlrd': "pip install xlrd  # For legacy Excel support", 
    'pyarrow': "pip install pyarrow  # For Parquet support",
    'fastparquet': "pip install fastparquet  # Alternative Parquet support",
    'chardet': "pip install chardet  # For encoding detection",
    'python-magic': "pip install python-magic  # For file type detection",
    'jsonpath-ng': "pip install jsonpath-ng  # For JSONPath support"
}

# Check required dependencies
for dep, install_cmd in _DATA_LOADER_DEPENDENCIES.items():
    try:
        __import__(dep)
    except ImportError:
        warnings.warn(
            f"Required dependency '{dep}' not found. Install with: {install_cmd}",
            ImportWarning,
            stacklevel=2
        )

def check_optional_dependency(dep_name: str) -> bool:
    """Check if optional dependency is available."""
    try:
        __import__(dep_name)
        return True
    except ImportError:
        return False

# Export dependency checker
__all__.append("check_optional_dependency")

# DataLoader-specific performance tips
"""
DataLoader Performance Tips (Pure Loading Focus):
    - Enable caching for repeated operations: DataLoader(cache_enabled=True)
    - Use chunked loading for large files: load(options=LoadOptions(chunksize=10000))
    - Leverage parallel processing: DataLoader(parallel_processing=True)  
    - Use appropriate load strategy: LoadStrategy.MEMORY_EFFICIENT for large datasets
    
Memory Management:
    - Set memory limits: DataLoader(max_memory_usage_gb=8.0)
    - Use streaming for very large files: loader.load_streaming(source)
    - Monitor memory usage: report.memory_usage_mb
    
Data Quality Assessment:
    - Enable comprehensive validation: LoadOptions(validation_level=ValidationLevel.COMPREHENSIVE)
    - Review quality reports: loader.analyze_data_quality(df)  
    - Use profiling: load_with_profile() function
    - Quality scores help decide if data needs processing

Format Support (6 Core Formats):
    - CSV/TSV: Automatic delimiter and encoding detection
    - Excel: Smart sheet selection and merged cell handling  
    - JSON: Nested structure flattening with JSONPath
    - JSON Lines: Streaming support for large log files
    - Parquet: Column selection and predicate pushdown
    - Google Sheets: Direct loading from share URLs

Integration with DataProcessor:
    DataLoader focuses on LOADING, DataProcessor handles TRANSFORMATIONS:
    
    loader = DataLoader()           # Pure loading
    processor = DataProcessor()     # Pure processing  
    
    df_raw = loader.load("data.csv")                    # Load as-is
    quality = loader.analyze_data_quality(df_raw)       # Assess quality
    
    if quality.quality_score > 70:
        df_clean = processor.clean_data(df_raw)          # Transform in separate class
"""