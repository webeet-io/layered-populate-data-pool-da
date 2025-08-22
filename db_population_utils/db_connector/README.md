# Smart Database Connector V3

Intelligent database connector with automatic switching between NeonDB and AWS LayeredDB. Features enhanced populate functionality with comprehensive reporting, schema management, and robust upsert operations.

## Installation

```bash
pip install sqlalchemy pandas psycopg2-binary
```

## Quick Start

### Default NeonDB Connection

```python
from smart_db_connector_enhanced_V3 import db_connector

# Connect to NeonDB (default) - automatically switches to test_berlin_data schema
db = db_connector()

# Check connection health
health = db.health_check()
print(health)  # {'status': 'healthy', 'connection_type': 'NeonDB', 'schemas_available': 4, ...}
```

### AWS LayeredDB Connection

```python
# Option 1: With credentials provided
db = db_connector('layereddb', 'username', 'password')

# Option 2: Interactive credential prompt
db = db_connector('layereddb')  # Will prompt for username/password

# Option 3: Any database name with credentials triggers AWS connection
db = db_connector('mydb', 'username', 'password')
```

## Basic Operations

### 1. Schema and Table Management

```python
# List available schemas
print(db.schemas)  # ['dependency_example', 'nyc_schools', 'public', 'test_berlin_data']

# Switch to a specific schema
db.use('test_berlin_data')

# List tables in current schema
print(db.tables)  # ['berlin_pools', 'berlin_venues', 'colleges_berlin', ...]

# Get detailed table information
table_info = db.get_table_info('berlin_pools')
print(table_info)  # {'schema': 'test_berlin_data', 'columns': [...], ...}
```

### 2. Query Operations

```python
# Execute SQL query
df = db.query("SELECT * FROM berlin_pools LIMIT 5")
print(df.shape)  # (5, 10)

# Query with specific schema
df = db.query("SELECT name, address FROM venues", schema='test_berlin_data')

# Query without info output
df = db.query("SELECT COUNT(*) FROM berlin_venues", show_info=False)
```

### 3. Enhanced Populate Method

The `populate` method is the core feature of V3, offering multiple modes to handle data insertion and comprehensive reporting.

#### Working with Constraints: The `append` Mode

To insert data into a table while preserving its existing `PRIMARY KEY` and `FOREIGN KEY` constraints, you **must** use `mode='append'`. This mode inserts new rows without altering the table's structure.

**Workflow:**
1.  Create the table with all required constraints using SQL.
2.  Prepare a DataFrame that **exactly** matches the table's structure (column names, order, and data types).
3.  Use the `populate()` method with `mode='append'` to load data into it.

> If there are mismatches in data types, column names, or order compared to the table, Python will raise an error. If everything matches, the table will be populated correctly, preserving the constraints and references.

**Example:**

```python
# Step 1: Create a table with constraints using a SQL command
# This assumes a 'districts' table already exists.
create_banks_sql = '''
CREATE TABLE banks (
    bank_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    district_id VARCHAR(20),
    CONSTRAINT fk_banks_district
        FOREIGN KEY (district_id)
        REFERENCES districts(district_id)
);
'''
db.query(create_banks_sql, show_info=False)

# Step 2: Prepare data and populate using 'append' mode
import pandas as pd
banks_df = pd.DataFrame({
    'bank_id': ['BANK001', 'BANK002'],
    'name': ['Global Bank', 'Local Trust'],
    'district_id': ['11001001', '11002002'] # These IDs must exist in the 'districts' table
})

result = db.populate(
    df=banks_df,
    table_name='banks',
    mode='append' # Preserves the table and its constraints
)

print(result) # {'status': 'success', 'rows_inserted': 2, ...}
```

---

#### `upsert` Mode: Insert or Update

This mode updates existing records and inserts new ones based on a specified primary key. It is ideal for data synchronization tasks and requires that the target table has a primary key.

```python
# Update existing records and insert new ones
upsert_data = pd.DataFrame({
    'id': [3, 4, 6],  # 3 & 4 are updated, 6 is inserted
    'name': ['Pool C Updated', 'Pool D Updated', 'Pool F'],
    'location': ['Berlin Updated', 'Cologne Updated', 'Dresden']
})

result = db.populate(
    df=upsert_data,
    table_name='my_pools',
    mode='upsert',
    primary_key=['id'],  # Required for upsert logic
    create_table=True    # Auto-creates table with a PK if it doesn't exist
)

print(result)  # {'status': 'success', 'rows_upserted': 3, 'primary_key': ['id']}
```

#### `replace` Mode: Use with Extreme Caution

This mode first **drops** the existing table (and all its constraints), then creates a new, empty table and inserts the data.

**⚠️ Warning:** This is a destructive operation. **Do not use `replace`** if you need to preserve the table's constraints, as they will be permanently removed. This mode should only be used for temporary or staging tables where data integrity is not enforced by the database schema.


#### Additional Options

-   **Interactive Schema Selection**: `db.populate(df)` will prompt you to select a schema and table if they are not provided.
-   **Comprehensive Reporting**: `show_report=True` provides a detailed analysis of the data before and after the population, including performance metrics.

```python
# Use with a safe mode like 'append' or 'upsert' to see the report
result = db.populate(
    df=banks_df, # using the dataframe from the append example
    table_name='banks',
    mode='append',
    show_report=True
)
# Displays: data analysis, column types, null values, duplicates, performance metrics
```

### 4. Connection Health and Status

```python
# Comprehensive health check
health = db.health_check()
print(health)
# {
#   'status': 'healthy',
#   'connection_type': 'NeonDB',
#   'database': 'neondb',
#   'schemas_available': 4,
#   'current_schema': 'test_berlin_data',
#   'tables_in_current_schema': 30,
#   'connection': 'active'
# }

# Show connection summary
db.show_connection_info()
```

## Advanced Features

### SSH Tunnel Support (AWS LayeredDB)

The connector automatically detects and validates SSH tunnel connections:

```python
# Requires SSH tunnel running on localhost:5433
db = db_connector('layereddb', 'username', 'password')

# Will automatically:
# 1. Check tunnel connectivity on localhost:5433
# 2. Fall back to NeonDB if tunnel not available
# 3. Provide troubleshooting guidance
```

### Automatic Table Creation with Constraints

```python
# Creates table with optimized data types and primary key constraints
result = db.populate(
    df=df,
    table_name='new_table',
    mode='upsert',
    primary_key=['id'],
    create_table=True  # Auto-creates with constraints
)

# Generated SQL example:
# CREATE TABLE test_berlin_data.new_table (
#     id INTEGER NOT NULL,
#     name VARCHAR(255),
#     value DECIMAL(15,6),
#     active BOOLEAN,
#     CONSTRAINT pk_new_table PRIMARY KEY (id)
# );
```

### Error Handling and Fallbacks

```python
try:
    result = db.populate(df, 'table', mode='upsert', primary_key=['id'])
    if result['status'] == 'error':
        print(f"Error: {result['error']}")
        # Automatic fallback to append mode if upsert fails
except Exception as e:
    print(f"Population failed: {e}")
```

## Examples by Use Case

### Data Migration
```python
# Migrate data from one schema to another
source_data = db.query("SELECT * FROM old_schema.users")
result = db.populate(source_data, 'users', schema='new_schema', mode='replace')
```

### Data Synchronization
```python
# Keep tables in sync with upsert
latest_data = get_latest_data_from_api()  # Your data source
result = db.populate(
    df=latest_data,
    table_name='sync_table',
    mode='upsert',
    primary_key=['id', 'updated_at'],
    create_table=True
)
```

### Batch Processing
```python
# Process large datasets in chunks
for chunk in pd.read_csv('large_file.csv', chunksize=1000):
    result = db.populate(chunk, 'processing_table', mode='append')
    if result['status'] != 'success':
        print(f"Chunk failed: {result['error']}")
        break
```

## Connection Management

```python
# Close connection properly
db.close()

# Context manager usage (auto-close)
from smart_db_connector_enhanced_V3 import db_connector

with db_connector() as db:
    df = db.query("SELECT * FROM my_table")
    # Connection automatically closed when exiting context
```

## Requirements

- **Python 3.8+**
- **PostgreSQL** databases (NeonDB, AWS RDS)
- **SSH tunnel** for AWS LayeredDB connections

### Required Dependencies
```bash
pip install sqlalchemy>=1.4.0 pandas>=1.3.0 psycopg2-binary>=2.9.0
```

### AWS LayeredDB Setup
1. Set up SSH tunnel to AWS RDS:
   ```bash
   ./connect-db.sh  # Your SSH tunnel script
   ```
2. Verify tunnel is running on `localhost:5433`
3. Use connector with credentials

## Troubleshooting

### Common Issues

#### 1. AWS Connection Falls Back to NeonDB
**Problem**: Connector switches to NeonDB instead of connecting to AWS
**Solutions**:
- Check SSH tunnel is running: `netstat -an | grep 5433`
- Verify tunnel script: `./connect-db.sh`
- Ensure correct credentials are provided
- Check tunnel endpoint: `localhost:5433`

#### 2. Upsert Operations Fail
**Problem**: `psycopg2.errors.InvalidColumnReference` - no unique constraint
**Solutions**:
- Use `create_table=True` for new tables
- Specify `primary_key` parameter for upsert mode
- Check existing table has primary key constraints

#### 3. Schema Not Found
**Problem**: `ValueError: Schema 'xyz' not found`
**Solutions**:
- Use `db.schemas` to list available schemas
- Check schema name spelling
- Use `db.use('schema_name')` to switch schemas

#### 4. Interactive Prompts in Scripts
**Problem**: `EOFError` when running scripts with interactive prompts
**Solutions**:
- Always provide `schema` and `table_name` parameters
- Use `show_report=False` for automated scripts
- Set environment variables for non-interactive mode

### Performance Tips

1. **Batch Processing**: Use `chunksize` for large datasets
2. **Connection Pooling**: Reuse connections for multiple operations
3. **Upsert vs Replace**: Use upsert for incremental updates
4. **Schema Specification**: Always specify schema to avoid prompts

### Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

db = db_connector()  # Will show detailed connection info
```

Check connection health:
```python
health = db.health_check()
if health['status'] != 'healthy':
    print(f"Connection issue: {health}")
```

## Version Information

- **V3**: Current version with enhanced populate, upsert, and production optimizations
- **V2**: Legacy version with basic populate functionality
- **Migration**: V2 code is compatible with V3 - just update import statements

### Breaking Changes from V2
- Main class renamed from `SmartDbConnectorV2` to `db_connector` function
- Enhanced populate method with new parameters (`mode`, `primary_key`, `create_table`)
- Improved error handling with custom exception types
- Performance optimizations and type safety improvements

## Support

For issues, questions, or contributions:
1. Check this README for common solutions
2. Review the comprehensive test notebook: `tests/test_smart_db_connector_V3_comprehensive.ipynb`
3. Run the test script: `python test_v3_functionality.py`
