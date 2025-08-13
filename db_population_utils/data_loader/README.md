# DataLoader - Essential Data Loading (Manager Requirements)

## Overview

Essential data loading module implementing **exactly 10 core methods** based on manager requirements. Focuses on 3 critical file formats with intelligent detection and quality assessment.

## Manager Requirements Implementation

```
✓ Loading Functions (5): load(), load_csv(), load_excel(), load_json(), parse_datetimes()
✓ Detection Functions (3): detect_format(), detect_encoding(), sniff_csv_params()
✓ Performance (1): estimate_memory_usage()
✓ Reporting & Error Handling (2): build_report(), detect_time_columns()
```

## Supported Formats (Manager Priority)

| Format  | Priority       | Status    | Usage  | Critical Features           |
|---------|---------------|-----------|--------|-----------------------------|
| CSV/TSV | 95% CRITICAL  | ✅ Full   | Daily  | Encoding detection, params  |
| Excel   | 80% HIGH      | ✅ Full   | Weekly | Sheet selection, detection  |
| JSON    | 70% MEDIUM    | ✅ Full   | Common | Structure flattening        |

**Excluded Formats** (Not in manager requirements):
❌ Parquet, JSON Lines, Google Sheets, URLs, Compressed archives

## Key Features

🎯 **Manager Priorities:**
- **Critical Encoding Detection**: "encoding might cause nasty problems, so we definitely should have it, great job."
- **DateTime Parsing**: "can cause lots of troubles and can be pretty common"
- **CSV Focus**: 95% usage priority with advanced parameter detection
- **Quality Assessment**: Built-in data quality scoring and reporting

✅ **Core Functionality:**
- Intelligent format detection and parameter sniffing
- Memory-efficient processing with estimation
- Comprehensive error handling and recovery
- Quality assessment (no transformation)
- Single-call comprehensive operations

## Installation

```bash
# Essential dependencies
pip install pandas numpy

# Format-specific dependencies
pip install chardet      # CRITICAL: For CSV encoding detection
pip install openpyxl     # HIGH: For Excel (.xlsx) support
pip install xlrd         # For legacy Excel (.xls) support
```

## Quick Start

### Basic Usage (Manager Workflow)

```python
from db_population_utils.data_loader import DataLoader

# Initialize with manager-approved defaults
loader = DataLoader(verbose=True)

# Auto-detect and load (works with all 3 formats)
df = loader.load("data.csv")     # CSV - 95% priority
df = loader.load("report.xlsx")  # Excel - 80% priority  
df = loader.load("api_data.json") # JSON - 70% priority
```

### Critical CSV Loading (95% Usage Priority)

```python
# Smart CSV detection with issue fixing
df, details = loader.load_csv_with_smart_detection("messy_data.csv")

print(f"📄 Detected delimiter: '{details['csv_params']['delimiter']}'")
print(f"📝 Detected encoding: {details['encoding']['detected']}")
print(f"🔧 Issues fixed: {details['issues_fixed']}")

# Quick CSV with encoding detection (manager priority)
from db_population_utils.data_loader import quick_csv_load

df, summary = quick_csv_load("important_data.csv")
print(f"📊 Quality: {summary['quality_score']}/100")
```

### DateTime Parsing (Manager Priority)

```python
# Auto-detect and parse datetime columns
df_with_dates = loader.parse_datetimes(df)

# Comprehensive datetime handling
from db_population_utils.data_loader import load_with_datetime_parsing

df, dt_report = load_with_datetime_parsing("time_series.csv")
print(f"🕒 Detected columns: {dt_report['detected_columns']}")
print(f"✅ Successfully parsed: {dt_report['successful_columns']}")
print(f"📊 Success rate: {dt_report['overall_success_rate']:.1f}%")
```

## Core Methods (Manager Requirements)

### Loading Functions (5 methods)

#### 1. load() - Universal Loading
```python
# Main loading method with auto-detection
df = loader.load("data.csv", kind="auto")

# With options
from db_population_utils.data_loader import LoadOptions
options = LoadOptions(encoding="utf-8", nrows=1000)
df = loader.load("data.xlsx", options=options)
```

#### 2. load_csv() - CSV/TSV (95% Priority)
```python
# Auto-detection (recommended)
df = loader.load_csv("data.csv")

# Custom parameters
from db_population_utils.data_loader import CsvParams
params = CsvParams(delimiter=";", encoding="latin1")
df = loader.load_csv("data.csv", params=params)

# Chunked loading for large files
for chunk in loader.load_csv("large.csv", chunksize=10000):
    process_chunk(chunk)
```

#### 3. load_excel() - Excel (80% Priority)
```python
# Auto sheet selection
df = loader.load_excel("report.xlsx")

# Specific sheet
from db_population_utils.data_loader import ExcelParams
params = ExcelParams(sheet="Summary")
df = loader.load_excel("report.xlsx", params=params)
```

#### 4. load_json() - JSON (70% Priority)
```python
# Simple JSON
df = loader.load_json("data.json")

# Nested JSON with flattening
from db_population_utils.data_loader import JsonParams
params = JsonParams(record_path=["data", "records"])
df = loader.load_json("nested.json", params=params)
```

#### 5. parse_datetimes() - Critical DateTime Handling
```python
# Auto-detect datetime columns
df_parsed = loader.parse_datetimes(df)

# Specific columns
df_parsed = loader.parse_datetimes(df, cols=['created_at', 'updated_at'])

# Custom format with error handling
df_parsed = loader.parse_datetimes(
    df, 
    cols=['date'], 
    format='%Y-%m-%d',
    errors='coerce'  # Handle parsing errors gracefully
)
```

### Detection Functions (3 methods)

#### 1. detect_format() - Format Detection
```python
# Auto-detect file format
format_type, confidence = loader.detect_format("unknown_file.dat")
print(f"Detected: {format_type} (confidence: {confidence:.2f})")
```

#### 2. detect_encoding() - Critical Encoding Detection
```python
# Critical for CSV files (manager priority)
encoding, confidence = loader.detect_encoding("data.csv")
print(f"Encoding: {encoding} (confidence: {confidence:.2f})")

# With custom sample size
encoding, confidence = loader.detect_encoding("large.csv", sample_size=50000)
```

#### 3. sniff_csv_params() - CSV Parameter Detection
```python
# Auto-detect CSV parameters
params = loader.sniff_csv_params("data.csv")
print(f"Delimiter: '{params.delimiter}'")
print(f"Quote char: '{params.quote_char}'")
print(f"Header row: {params.header}")
print(f"Confidence: {params.delimiter_confidence:.2f}")
```

### Performance (1 method)

#### estimate_memory_usage() - Memory Estimation
```python
# Estimate memory requirements
memory_estimate = loader.estimate_memory_usage("large_file.csv")

print(f"Estimated memory: {memory_estimate.estimated_memory_mb:.1f}MB")
print(f"Can load in memory: {memory_estimate.can_load_in_memory}")

if memory_estimate.recommended_chunksize:
    print(f"Recommended chunk size: {memory_estimate.recommended_chunksize}")
```

### Reporting & Error Handling (2 methods)

#### 1. build_report() - Comprehensive Reporting
```python
# Generate detailed report
df = loader.load("data.csv")
report = loader.build_report()

print(f"📊 Quality Score: {report.data_quality.quality_score}/100")
print(f"⏱️  Load Time: {report.load_time_seconds:.2f}s")
print(f"💾 Memory Usage: {report.memory_usage_mb:.1f}MB")
print(f"🔍 Detected encoding: {report.encoding}")

if report.warnings:
    print(f"⚠️  Warnings: {report.warnings}")
```

#### 2. detect_time_columns() - DateTime Column Detection
```python
# Detect potential datetime columns
time_columns = loader.detect_time_columns(df)
print(f"🕒 Potential datetime columns: {time_columns}")

# With hints and custom settings
time_columns = loader.detect_time_columns(
    df,
    hints=['date', 'created', 'timestamp'],
    min_parse_rate=0.9
)
```

## Comprehensive Operations

### 1. Complete Loading with Full Reporting
```python
# Single call: detection + loading + quality analysis + reporting
df, report = loader.load_with_comprehensive_report(
    "data.csv",
    include_quality_analysis=True,
    include_datetime_detection=True
)

print(f"✅ Loaded {report.shape[0]} rows, {report.shape[1]} columns")
print(f"📊 Quality Score: {report.data_quality.quality_score}/100")
print(f"🕒 Datetime Columns: {report.detected_time_cols}")
print(f"⏱️  Load Time: {report.load_time_seconds:.2f}s")
```

### 2. CSV with Smart Detection and Issue Fixing
```python
# Comprehensive CSV handling with automatic issue resolution
df, details = loader.load_csv_with_smart_detection(
    "problematic_data.csv",
    auto_fix_common_issues=True
)

print(f"📄 Delimiter: '{details['csv_params']['delimiter']}'")
print(f"📝 Encoding: {details['encoding']['detected']}")
print(f"🔧 Issues fixed: {details['issues_fixed']}")
print(f"⚠️  Issues remaining: {details['issues_remaining']}")
```

### 3. Fallback Loading with Error Recovery
```python
# Multiple fallback strategies for problematic files
df, recovery = loader.load_with_fallback_strategies(
    "difficult_file.csv",
    max_attempts=3,
    enable_error_recovery=True
)

print(f"📊 Final result: {recovery['final_status']}")
print(f"🔄 Attempts made: {recovery['attempts_made']}")
print(f"💾 Data recovered: {recovery['recovery_percentage']:.1f}%")
```

## Configuration and Options

### LoadOptions Configuration
```python
from db_population_utils.data_loader import LoadOptions, LoadStrategy

options = LoadOptions(
    # Format detection
    kind="auto",  # or "csv", "excel", "json"
    encoding="utf-8",
    compression="infer",
    
    # Performance
    nrows=10000,
    low_memory=True,
    load_strategy=LoadStrategy.MEMORY_EFFICIENT,
    
    # CSV specific
    delimiter=",",
    header=0,
    
    # Excel specific  
    sheet="auto",
    
    # JSON specific
    flatten_json=True,
    
    # DateTime handling (manager priority)
    detect_time_columns=True,
    infer_datetime_format=True,
    
    # Error handling
    on_bad_lines="error",  # or "warn", "skip"
    error_tolerance=0.0
)

df = loader.load("data.csv", options=options)
```

### Format-Specific Parameters
```python
# CSV Parameters
from db_population_utils.data_loader import CsvParams

csv_params = CsvParams(
    delimiter=",",
    encoding="utf-8", 
    header=0,
    quote_char='"',
    null_values=['', 'NULL', 'na']
)

# Excel Parameters
from db_population_utils.data_loader import ExcelParams

excel_params = ExcelParams(
    sheet="Summary",
    header=0,
    engine="openpyxl"
)

# JSON Parameters
from db_population_utils.data_loader import JsonParams

json_params = JsonParams(
    record_path=["data", "records"],
    orient="records"
)
```

## Error Handling

### Common Error Scenarios
```python
from db_population_utils.data_loader import (
    DataLoaderError, 
    DetectionError, 
    UnsupportedFormatError,
    LoadingMemoryError
)

try:
    df = loader.load("problematic_file.csv")
except DetectionError as e:
    print(f"Detection failed: {e}")
    # Try manual parameters
    
except UnsupportedFormatError as e:
    print(f"Unsupported format: {e}")
    
except LoadingMemoryError as e:
    print(f"Memory issue: {e}")
    # Try chunked loading
    
except DataLoaderError as e:
    print(f"General loading error: {e}")
```

### Graceful Error Recovery
```python
# Load with error tolerance
try:
    df, recovery_info = loader.load_with_fallback_strategies(
        "problematic_file.csv",
        enable_error_recovery=True
    )
    
    if recovery_info['final_status'] == 'partial_success':
        print(f"⚠️  Partial load: {recovery_info['recovery_percentage']:.1f}%")
    
except DataLoaderError:
    print("❌ Complete failure - file may be corrupted")
```

## Integration with Data Pipeline

### Complete Manager Workflow
```python
from db_population_utils.data_loader import DataLoader
from db_population_utils import DataProcessor, DBConnector

# Step 1: Load with quality assessment
loader = DataLoader(verbose=True)
df_raw, report = loader.load_with_comprehensive_report("data.csv")

print(f"📊 Data Quality: {report.data_quality.quality_score}/100")

# Step 2: Process only if quality is acceptable
if report.data_quality.quality_score > 80:
    # DataProcessor handles transformations (separate class)
    processor = DataProcessor()
    df_clean = processor.clean_data(df_raw)
    
    # Step 3: Store in database
    connector = DBConnector()
    success, db_report = connector.insert_dataframe_with_report(
        df_clean, "processed_data", target="ingestion"
    )
    
    if success:
        print(f"✅ Pipeline completed: {db_report.rows_inserted} rows inserted")
    else:
        print(f"❌ Database insertion failed: {db_report.errors}")
else:
    print(f"⚠️  Data quality too low ({report.data_quality.quality_score}/100)")
    print(f"Recommendations: {report.data_quality.recommendations}")
```

### Datetime Processing Pipeline
```python
# Critical datetime handling (manager priority)
df, dt_report = load_with_datetime_parsing("time_series.csv")

if dt_report['overall_success_rate'] > 80:
    print(f"✅ DateTime parsing successful: {dt_report['successful_columns']}")
    
    # Continue with time series processing
    processor = DataProcessor()
    df_processed = processor.process_time_series(df)
else:
    print(f"⚠️  DateTime parsing issues: {dt_report['failed_columns']}")
    # Manual datetime handling may be required
```

## Performance Tips

### Memory Management
```python
# Check memory requirements first
memory_est = loader.estimate_memory_usage("large_file.csv")

if not memory_est.can_load_in_memory:
    # Use chunked processing
    for chunk in loader.load_csv("large_file.csv", chunksize=10000):
        process_chunk(chunk)
else:
    # Load normally
    df = loader.load_csv("large_file.csv")
```

### CSV Optimization (95% Priority)
```python
# Enable caching for repeated CSV operations
loader = DataLoader(cache_enabled=True)

# Pre-detect parameters for batch processing
csv_params = loader.sniff_csv_params("template.csv")

# Reuse parameters for similar files
for file in similar_csv_files:
    df = loader.load_csv(file, params=csv_params)
    process_file(df)
```

## Convenience Functions

```python
from db_population_utils.data_loader import (
    create_essential_loader,
    quick_csv_load,
    load_with_datetime_parsing,
    check_format_support
)

# Quick setup
loader = create_essential_loader(verbose=True, max_memory_gb=8.0)

# Quick CSV (95% priority format)
df, summary = quick_csv_load("data.csv", auto_detect_encoding=True)

# DateTime focus
df, dt_report = load_with_datetime_parsing("time_data.csv")

# Check what's supported
support = check_format_support()
print(f"CSV support: {support['csv']['status']}")
print(f"Excel support: {support['excel']['status']}")
print(f"JSON support: {support['json']['status']}")
```

## Troubleshooting

### Common Issues

**1. Encoding Problems (Manager Priority)**
```python
# Encoding detection failing
encoding, confidence = loader.detect_encoding("problematic.csv")
if confidence < 0.8:
    # Try common encodings manually
    for enc in ['utf-8', 'latin1', 'cp1252']:
        try:
            df = loader.load_csv("problematic.csv", encoding=enc)
            break
        except UnicodeDecodeError:
            continue
```

**2. DateTime Parsing Issues (Manager Priority)**
```python
# Auto-detection failing
time_cols = loader.detect_time_columns(df)
if not time_cols:
    # Manual hints
    time_cols = loader.detect_time_columns(
        df, 
        hints=['date', 'created', 'timestamp', 'time']
    )

# Custom parsing for difficult formats
df_parsed = loader.parse_datetimes(
    df, 
    cols=time_cols,
    errors='coerce',  # Handle errors gracefully
    dayfirst=True     # European date format
)
```

**3. Large File Handling**
```python
# Memory estimation first
memory_est = loader.estimate_memory_usage("huge_file.csv")
if memory_est.recommended_chunksize:
    # Use recommended chunk size
    chunks = loader.load_csv(
        "huge_file.csv", 
        chunksize=memory_est.recommended_chunksize
    )
    for chunk in chunks:
        process_chunk(chunk)
```

## Dependencies

**Required:**
```bash
pip install pandas>=1.3.0 numpy>=1.20.0
```

**Format-Specific:**
```bash
pip install chardet      # CRITICAL: CSV encoding detection
pip install openpyxl     # HIGH: Excel (.xlsx) support  
pip install xlrd         # For legacy Excel (.xls)
```

**Optional:**
```bash
pip install python-magic  # Enhanced file type detection
```

## License

MIT License

## Contributing

1. Follow manager requirements: exactly 10 core methods
2. Maintain focus on 3 priority formats: CSV (95%), Excel (80%), JSON (70%)
3. Emphasize encoding detection and datetime parsing
4. Include comprehensive error handling and reporting
5. Write tests for all core functionality
6. Update documentation for any API changes

---

**Manager Requirements Summary:**
- ✅ **10 Core Methods**: Exactly as specified in requirements
- ✅ **3 Priority Formats**: CSV (95%), Excel (80%), JSON (70%)
- ✅ **Critical Features**: Encoding detection, datetime parsing
- ✅ **Quality Focus**: Assessment without transformation
- ✅ **Integration Ready**: Works with DataProcessor and DBConnector