# Smart DB Connector (`db_population_utils`)

Utilities for **smart database operations**: one-call execution with automatic connection checks, data profiling, metrics collection, and detailed reporting.

## Installation

```bash
pip install sqlalchemy pandas
# For PostgreSQL:
# pip install psycopg2-binary
# or
# pip install psycopg
```

## Quick Start

```python
from db_population_utils import SmartDBConnector, create_sample_connector

# Ready-to-use demo connector (SQLite in-memory)
db = create_sample_connector("sqlite")

# Check connection health
health = db.health_check()
print(health)  # {'status': 'healthy', 'database_version': '...', 'connection_time_ms': 12.3, ...}
```

## Manual Connector Setup

```python
from db_population_utils import SmartDBConnector

db = SmartDBConnector(
    "postgresql://user:pass@localhost:5432/mydb",
    pool_size=10,
    echo_sql=True,       # log executed SQL
    auto_optimize=True   # automatic query optimization
)
```

## Smart Operations (one-call)

### 1) `smart_query` — SELECT with data profiling and metrics

```python
res = db.smart_query(
    "SELECT id, email FROM users WHERE created_at > :ts",
    params={"ts": "2024-01-01"},
    analyze_data=True,    # enable result profiling
    cache_results=False
)

df = res["data"]         # pandas.DataFrame with results
report = res["report"]   # SmartReport
print(report.summary())  # short summary
```

Result structure:
```python
{
  "success": bool,
  "data": pandas.DataFrame,
  "report": SmartReport,
  "cached": bool
}
```

---

### 2) `smart_insert` — Insert DataFrame with pre-checks and indexing

```python
import pandas as pd

df = pd.DataFrame(
    [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
)

ins = db.smart_insert(
    dataframe=df,
    table="users_staging",
    schema=None,          # or "staging"
    if_exists="append",   # "append" | "replace" | "fail"
    chunk_size=5000,
    create_indexes=True
)

print(ins["success"], ins["rows_inserted"])
print(ins["table_created"], ins["indexes_created"])
print(ins["report"].summary())
```

Result structure:
```python
{
  "success": bool,
  "rows_inserted": int,
  "report": SmartReport,
  "table_created": bool,
  "indexes_created": list[str]
}
```

---

### 3) `smart_execute` — DML/DDL with impact analysis

```python
exe = db.smart_execute(
    "UPDATE users SET active = :flag WHERE last_login < :cutoff",
    params={"flag": False, "cutoff": "2024-01-01"},
    analyze_impact=True,   # analyze SQL type & impact
    auto_commit=True       # auto-commit transaction
)

print(exe["success"], exe["rows_affected"], exe["sql_type"])
print(exe["impact_analysis"])
print(exe["report"].summary())
```

Result structure:
```python
{
  "success": bool,
  "rows_affected": int,
  "report": SmartReport,
  "sql_type": str,        # e.g. 'UPDATE' | 'INSERT' | 'DELETE' | 'DDL'
  "impact_analysis": dict
}
```

---

### 4) `get_table_info` — Table schema and metadata

```python
info = db.get_table_info("users", schema="public")
if info.get("exists"):
    print("columns:", info["columns"])
    print("primary_key:", info["primary_key"])
    print("foreign_keys:", info["foreign_keys"])
    print("indexes:", info["indexes"])
else:
    print("Table not found:", info.get("error"))
```

Result structure:
```python
{
  "exists": bool,
  "columns": list[dict],
  "primary_key": list[str],
  "foreign_keys": list[dict],
  "indexes": list[str],
  "column_count": int,
  "has_primary_key": bool
}
```

---

## The `SmartReport` Class

`SmartReport` provides detailed reporting for all operations.

Key fields (partial list):
- `operation: str`
- `success: bool`
- `timestamp: str`
- `execution_time_ms: float`
- Data metrics: `rows_affected`, `rows_retrieved`, `columns_count`, `data_size_mb`
- Connection health: `connection_healthy`, `database_version`, `connection_time_ms`
- Diagnostics & performance: `optimization_applied`, `cpu_time_ms`, `io_operations`
- Messages: `info`, `warnings`, `errors`, `recommendations`

Useful methods:
```python
rep = exe["report"]  # from any operation result
print(rep.summary())
print(rep.errors)
print(rep.warnings)
print(rep.info)
```

---

## Demo

```python
from db_population_utils import run_comprehensive_demo

run_comprehensive_demo()  # runs a full demo on SQLite
```

---

## Closing the Connection

```python
db.close()
```
