# DBConnector Class Design

## Overview
`DBConnector` (core, required now)

**Responsibility**: Centralize DB configuration and pooled connections for multiple environments (e.g., `ingestion`, `app`).

## Core Methods (Original Design)

### Initialization
* `__init__(ingestion: Optional[DBSettings], app: Optional[DBSettings], echo: bool=False)` - Initialize connector with database settings

### Connection Management
* `get_engine(target: Literal["ingestion","app"]) -> Engine` - Get SQLAlchemy engine for specified target
* `connect(target="ingestion") -> contextmanager[Connection]` - Get connection context manager
* `transaction(target="ingestion") -> contextmanager[Connection]` - Get transaction context manager
* `test_connection(target="ingestion") -> dict` - Test connection and return status info

### Query Execution
* `execute(sql: str, params: dict|None=None, target="ingestion") -> int` - Execute SQL statement and return affected rows
* `fetch_df(sql: str, params: dict|None=None, target="ingestion") -> pd.DataFrame` - Execute query and return DataFrame *(optional but very handy)*

### Data Operations
* `to_sql(df: pd.DataFrame, table: str, schema: str|None=None, if_exists="append", target="ingestion") -> None` - Write DataFrame to database table

### Cleanup
* `dispose_engine(target)` - Dispose specific engine and its connection pool
* `dispose_all()` - Dispose all engines and connection pools

## Enhanced Methods (Extensions)

### Configuration Management
* `load_config_from_file(path: str) -> None` - Load database configuration from YAML/JSON file
* `load_config_from_env() -> None` - Load configuration from environment variables
* `validate_config() -> dict` - Validate database connection settings
* `get_connection_info(target: str) -> dict` - Get connection info without sensitive data (passwords)

### Schema Management
* `get_table_schema(table: str, schema: str = None, target="ingestion") -> dict` - Retrieve table schema information
* `table_exists(table: str, schema: str = None, target="ingestion") -> bool` - Check if table exists
* `create_schema(schema: str, target="ingestion") -> bool` - Create database schema
* `drop_table(table: str, schema: str = None, target="ingestion") -> bool` - Drop table if exists
* `get_table_columns(table: str, schema: str = None, target="ingestion") -> list` - Get list of table columns

### Batch Operations & Performance
* `execute_batch(statements: list[str], target="ingestion") -> list[int]` - Execute multiple SQL statements in batch
* `bulk_insert(data: list[dict], table: str, schema: str = None, batch_size=1000, target="ingestion") -> None` - Bulk insert data with batching
* `copy_table(source_table: str, dest_table: str, source_target="app", dest_target="ingestion") -> int` - Copy table between databases

### Monitoring & Logging
* `get_connection_status(target: str = None) -> dict` - Get status of connections (all or specific target)
* `get_pool_stats(target: str) -> dict` - Get connection pool statistics
* `log_query_performance(enabled: bool = True) -> None` - Enable/disable query performance logging

### Migration & Backup Support
* `backup_table(table: str, backup_path: str, target="ingestion") -> bool` - Backup table to file
* `restore_table(table: str, backup_path: str, target="ingestion") -> bool` - Restore table from backup file
* `run_migration_script(script_path: str, target="ingestion") -> bool` - Execute migration script from file

### Enhanced Error Handling
* `retry_connection(target: str, max_retries=3) -> bool` - Retry connection with exponential backoff
* `health_check(target: str = None) -> dict` - Comprehensive health check of connections
* `get_last_error(target: str) -> str` - Get last error message for target

### Integration Support
* `register_processor(processor: 'DataProcessor') -> None` - Register DataProcessor instance for integration
* `register_populater(populater: 'DBPopulater') -> None` - Register DBPopulater instance for integration
* `get_table_for_processing(table: str, target="ingestion") -> pd.DataFrame` - Retrieve table data for processing

### Utility Methods
* `close_idle_connections(target: str = None, idle_timeout=300) -> int` - Close idle connections older than timeout
* `vacuum_table(table: str, target="ingestion") -> None` - Run VACUUM on table (PostgreSQL specific)
* `analyze_table(table: str, target="ingestion") -> dict` - Get table statistics and analysis
* `estimate_table_size(table: str, target="ingestion") -> dict` - Estimate table size and row count

### Advanced Context Managers
* `batch_transaction(target="ingestion") -> contextmanager` - Context manager for batch operations with transaction
* `read_only_connection(target="app") -> contextmanager` - Context manager for read-only operations
* `with_timeout(seconds: int, target="ingestion") -> contextmanager` - Context manager with query timeout

## Enhanced Initialization

```python
def __init__(
    self,
    ingestion: Optional[DBSettings] = None,
    app: Optional[DBSettings] = None,
    echo: bool = False,
    pool_size: int = 5,              # Connection pool size
    max_overflow: int = 10,          # Maximum pool overflow
    pool_timeout: int = 30,          # Pool checkout timeout
    pool_recycle: int = 3600,        # Connection recycle time
    config_file: Optional[str] = None,  # Path to configuration file
    auto_load_env: bool = True       # Automatically load from environment
)
```

## Usage Examples

### Basic Usage
```python
# Initialize with enhanced configuration
db = DBConnector(
    config_file="db_config.yaml",
    echo=True,
    pool_size=10
)

# Health check
health_status = db.health_check()

# Schema operations
if not db.table_exists("users", "public"):
    db.create_schema("public")
```

### Batch Operations
```python
# Batch processing with transaction
with db.batch_transaction("ingestion") as conn:
    db.bulk_insert(data, "staging_table", batch_size=5000)
    db.execute("CALL process_staging_data()")
```

### Monitoring
```python
# Get pool statistics
stats = db.get_pool_stats("ingestion")

# Performance monitoring
db.log_query_performance(True)
```

## Integration Points

This enhanced `DBConnector` class serves as the foundation for:
- `DataProcessor` class integration for data preprocessing
- `DBPopulater` class integration for data insertion
- Configuration management across the entire data pipeline
- Monitoring and logging capabilities for production environments