"""
DataLoader Package - Smart Data Loading with Format Detection

This package provides intelligent data loading capabilities for CSV, Excel, and JSON files
with automatic format detection, encoding detection, and comprehensive error handling.

Main Classes:
- SmartAutoDataLoader: Full implementation with all features
- SmartAutoDataLoader (from stub): Skeleton version for development

Features:
- Universal loading with auto-format detection
- CSV: 95% priority (CRITICAL) - encoding/delimiter detection
- Excel: 80% priority (HIGH) - sheet detection and selection  
- JSON: 70% priority (MEDIUM) - structure flattening and relational extraction
- Automatic datetime parsing across all formats
- Performance monitoring and comprehensive reporting
- Enhanced JSON handling with relational table extraction
"""

from .smart_auto_data_loader import SmartAutoDataLoader, LoadReport

__version__ = "1.1.0"
__all__ = ["SmartAutoDataLoader", "LoadReport"]

# Quick usage examples
__doc__ += """

Quick Usage:
    from db_population_utils.data_loader import SmartAutoDataLoader
    
    # Basic loading
    loader = SmartAutoDataLoader(verbose=True)
    df = loader.load("data.csv")  # Auto-detects format
    
    # JSON with relational extraction
    tables = loader.load_json_as_tables("complex_data.json")
    for table_name, df in tables.items():
        print(f"{table_name}: {df.shape}")
    
    # Comprehensive reporting
    report = loader.build_report("data.xlsx")
    print(f"Quality score: {report.quality_score}")
"""