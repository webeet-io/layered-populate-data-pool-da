# Smart Data Loader

 **Philosophy: "Simple things should be simple!"**

SmartAutoDataLoader - intelligent data loading that works automatically without complex configuration.

## Quick Start

```python
from db_population_utils.data_loader import SmartAutoDataLoader

# Create loader
loader = SmartAutoDataLoader(verbose=True)

# Load any file - everything automatic!
df = loader.load("data.csv")
```

That's it! No configuration needed. The loader automatically:
- ✅ Detects file format (CSV, Excel, JSON)
- ✅ Finds the right encoding (UTF-8, Latin-1, etc.)
- ✅ Discovers delimiters (comma, semicolon, tab)
- ✅ Identifies and parses datetime columns
- ✅ **Intelligently analyzes JSON complexity for deep flattening**
- ✅ **Extracts 500+ columns from complex nested JSON structures**
- ✅ Provides comprehensive reporting
- ✅ Handles errors gracefully

## 🚀 New Feature: Intelligent JSON Deep Flattening

### Automatic Smart Analysis
SmartAutoDataLoader now automatically analyzes JSON complexity and chooses the optimal extraction strategy:

```python
loader = SmartAutoDataLoader(verbose=True)

# Automatic analysis and deep flattening when beneficial
df = loader.load("complex_data.json")

# Output:
# 🗂️ Loading JSON file with intelligent analysis...
# 📊 Standard flattening: (21, 22)
# 🧠 Complexity analysis: {'needs_deep_flattening': True}
# 🔍 Applying deep flattening...
# 📊 Deep flattening: (21, 504)
# 📈 Improvement: 22.9x more columns
# ✅ Using deep flattening (better data extraction)
```

### Before vs After
- **Standard JSON loading**: 22 columns
- **Smart deep flattening**: 504+ columns (23x more data!)

### Complex Nested Structures Supported
- **Workflow Steps**: `workflowSteps_0_id`, `workflowSteps_0_name`, etc.
- **Input Rows**: `workflowSteps_0_inputRows_0_value`, etc.
- **Dropdown Options**: Automatically extracted to separate fields
- **Multi-level Nesting**: No depth limit with smart truncation

### Manual Control Available
```python
# Disable automatic analysis
df = loader.load_json("data.json", auto_deep_flatten=False)

# Force deep flattening
tables = loader.load_json_as_tables("data.json")  # Extract all related tables
```

## Features

SmartAutoDataLoader implements all 12+ essential methods:

### Loading Functions
1. **`load(file_path)`** - Universal loading with auto-detection
2. **`load_csv(file_path)`** - Optimized CSV loading
3. **`load_excel(file_path)`** - Excel file support
4. **`load_json(file_path, auto_deep_flatten=True)`** - Intelligent JSON loading with automatic complexity analysis
5. **`parse_datetimes(df)`** - Intelligent datetime parsing

### Advanced JSON Functions
6. **`load_json_as_tables(file_path)`** - Extract all relational tables from complex JSON
7. **`_analyze_json_complexity(data)`** - Automatic complexity analysis
8. **`_smart_deep_flatten_json(data)`** - Enhanced deep flattening with smart limits

### Detection Functions  
9. **`detect_format(file_path)`** - Automatic format detection
10. **`detect_encoding(file_path)`** - Smart encoding detection
11. **`sniff_csv_params(file_path)`** - CSV parameter discovery

### Analysis & Reporting
12. **`estimate_memory_usage(file_path)`** - Memory requirements prediction
13. **`build_report()`** - Comprehensive loading reports
14. **`detect_time_columns(df)`** - Automatic datetime column detection

## Real Examples

### Complex JSON with Automatic Deep Flattening
```python
loader = SmartAutoDataLoader(verbose=True)
df = loader.load("workflow_data.json")

# Output:
# 🎯 SmartAutoDataLoader ready!
# 🎯 Loading file: workflow_data.json
# 🔍 Format detected: json
# 🗂️ Loading JSON file with intelligent analysis...
# 📊 Standard flattening: (21, 22)
# 🧠 Complexity analysis: {'max_nesting_depth': 4, 'nested_arrays': 2, 'needs_deep_flattening': True}
# 🔍 Applying deep flattening...
# 📊 Deep flattening: (21, 504)
# 📈 Improvement: 22.9x more columns
# ✅ Using deep flattening (better data extraction)
# ✅ JSON loaded: 21 rows, 504 columns
```

### CSV with Automatic Detection
```python
loader = SmartAutoDataLoader(verbose=True)
df = loader.load("sales_data.csv")

# Output:
# 🎯 SmartAutoDataLoader ready!
# 🎯 Loading file: sales_data.csv
# 🔍 Format detected: csv
# 📊 Loading CSV file...
# 🔤 Encoding detected: utf-8
# 🗓️ Searching for date columns...
#    📅 Found date columns: ['order_date', 'ship_date']
# ✅ CSV loaded: 10000 rows, 8 columns
```

## API Reference

### SmartAutoDataLoader Class

```python
class SmartAutoDataLoader:
    def __init__(self, verbose: bool = False):
        """Initialize smart data loader.
        
        Args:
            verbose: Enable detailed logging
        """
    
    def load(self, file_path: str) -> pd.DataFrame:
        """Universal file loading with auto-detection.
        
        Automatically detects format, encoding, delimiters, and dates.
        """
    
    def build_report(self) -> LoadReport:
        """Get comprehensive loading report."""
```

## Why SmartAutoDataLoader?

###  **Automatic Everything**
- No manual encoding/delimiter specification
- No complex configuration objects
- No trial-and-error loading

###  **Intelligent Detection**
- Learns from file content, not just extensions
- Handles edge cases and problematic files
- Provides detailed feedback on what was detected

###  **Robust Error Handling**  
- Graceful fallbacks for encoding issues
- Recovery strategies for malformed data
- Comprehensive error reporting

---

**Built with ❤️ for data scientists who want to focus on analysis, not file loading hassles.**

# SmartAutoDataLoader

Intelligent data loader with automatic format detection and comprehensive data processing capabilities.

## New Features (v1.1.0)

### Enhanced JSON Processing
- **Relational Table Extraction**: Automatically extracts nested JSON structures into separate related tables
- **Smart Flattening Modes**: Choose between 'smart', 'simple', or 'relational' flattening
- **Special Structure Detection**: Automatically handles dropdown options, arrays, and complex nested data
- **German Character Support**: Proper handling of umlauts (ä, ö, ü, ß) in table names

### Usage Examples

#### Basic JSON Loading
```python
loader = SmartAutoDataLoader(verbose=True)
df = loader.load("data.json")  # Standard flattening
```

#### Relational Table Extraction
```python
# Extract all related tables from complex JSON
tables = loader.load_json_as_tables("complex_structure.json")

# Access individual tables
main_table = tables.get('main')
workflow_table = tables.get('workflow_steps')
inputs_table = tables.get('workflow_steps_input_rows')
dropdown_options = tables.get('workflow_steps_input_rows_dropdown_options')

# Print table summary
for table_name, df in tables.items():
    print(f"{table_name}: {df.shape}")
```

#### Flatten Mode Options
```python
# Smart flattening (default) - automatically chooses best strategy
df = loader.load_json("data.json", flatten_mode='smart')

# Simple flattening - basic pandas json_normalize
df = loader.load_json("data.json", flatten_mode='simple')

# Relational extraction - returns main table, extracts others separately
df = loader.load_json("data.json", flatten_mode='relational')
```

## Manager Requirements Implementation

✅ **Loading Functions (5)**:
- `load()` - Universal loading with auto-delegation
- `load_csv()` - CSV loading with parameter detection (95% priority)
- `load_excel()` - Excel loading with sheet detection (80% priority)
- `load_json()` - Enhanced JSON loading with relational extraction (70% priority)
- `parse_datetimes()` - Automatic datetime parsing

✅ **Detection Functions (3)**:
- `detect_format()` - File format detection
- `detect_encoding()` - Critical encoding detection for CSV
- `sniff_csv_params()` - CSV parameter sniffing

✅ **Performance & Reporting (2)**:
- `estimate_memory_usage()` - Memory estimation
- `build_report()` - Comprehensive loading reports
- `detect_time_columns()` - DateTime column detection

### New JSON Methods:
- `load_json_as_tables()` - Extract all relational tables
- `_extract_relational_tables()` - Core relational extraction logic
- `_normalize_table_name()` - Database-compatible name normalization

## Enhanced JSON Processing Features

### Intelligent Complexity Analysis
The loader automatically analyzes JSON structure and decides when deep flattening is beneficial:

```python
complexity_metrics = {
    'total_items': 21,
    'max_nesting_depth': 4,
    'nested_arrays': 2,
    'nested_objects': 15,
    'needs_deep_flattening': True  # Automatic decision
}
```

### Smart Deep Flattening
- **Automatic Limits**: Prevents excessive column creation (max 50 array items per level)
- **Metadata Preservation**: Adds `_total_count` and `_truncated_at` fields when limiting
- **Type Intelligence**: Handles lists of objects vs. simple lists differently
- **Memory Efficiency**: Smart truncation for very large nested structures

### Real-World Example: Workflow Data
Input JSON with complex nesting:
```json
[
  {
    "id": "workflow-123",
    "workflowSteps": [
      {
        "id": "step-1",
        "inputRows": [
          {
            "id": "input-1",
            "dropdownOptions": [
              {"value": "opt1", "label": "Option 1"}
            ]
          }
        ]
      }
    ]
  }
]
```

Automatically extracted columns:
- `id`: Main workflow ID
- `workflowSteps_0_id`: First step ID
- `workflowSteps_0_inputRows_0_id`: First input ID
- `workflowSteps_0_inputRows_0_dropdownOptions_0_value`: First dropdown value
- ...and 500+ more detailed fields

### Performance & Memory Management
- **Smart Analysis**: Only applies deep flattening when beneficial (>2x improvement)
- **Automatic Fallback**: Falls back to standard flattening for simple structures
- **Memory Monitoring**: Built-in memory usage estimation and warnings
- **Truncation Metadata**: Preserves information about truncated large arrays

## JSON Structure Examples

### Input JSON Structure:
```json
[
  {
    "id": 1,
    "name": "Order",
    "workflowSteps": [
      {
        "id": 10,
        "name": "Step 1",
        "inputRows": [
          {
            "id": 100,
            "name": "Field 1",
            "dropdownOptions": [
              {"value": "opt1", "label": "Option 1"},
              {"value": "opt2", "label": "Option 2"}
            ]
          }
        ]
      }
    ]
  }
]
```

### Extracted Tables:
1. **main** - Main orders table
2. **workflow_steps** - Workflow steps with parent_id
3. **workflow_steps_input_rows** - Input rows with parent_id
4. **workflow_steps_input_rows_dropdown_options** - Dropdown options

## Quality Features

- **Automatic Encoding Detection**: Supports UTF-8, Latin-1, CP1252, etc.
- **Smart Delimiter Detection**: Comma, semicolon, tab, pipe
- **DateTime Pattern Recognition**: Multiple international date formats
- **Intelligent JSON Analysis**: Automatic complexity assessment and optimal strategy selection
- **Deep Nested Extraction**: Up to 500+ columns from complex JSON structures
- **Memory-Aware Processing**: Smart limits and truncation for large datasets
- **Error Recovery**: Graceful fallbacks and comprehensive error reporting
- **Performance Monitoring**: Memory estimation and loading time tracking
- **German Language Support**: Proper handling of umlauts and special characters

## Priority System

- **CSV/TSV**: 95% priority (CRITICAL) - Full parameter detection
- **Excel**: 80% priority (HIGH) - Sheet detection and selection
- **JSON**: 70% priority (MEDIUM) - Enhanced intelligent deep extraction

## Installation

```python
from db_population_utils.data_loader import SmartAutoDataLoader

loader = SmartAutoDataLoader(verbose=True)
```

## Testing

Comprehensive test suites available:
- `test_csv_loader.ipynb` - CSV functionality testing
- `test_excel_loader.ipynb` - Excel functionality testing  
- `test_json_loader.ipynb` - JSON functionality testing
- `test_row_data.ipynb` - Real-world data testing