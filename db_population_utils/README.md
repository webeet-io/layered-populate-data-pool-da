# DB Population Utilities

Reusable building blocks for consistent data ingestion across layers (banks, hospitals, schools, etc.).

---

---

## Main Components

- **data_loader**  
  SmartAutoDataLoader and helpers for robust, automatic data loading from files (CSV, Excel, etc.) into a pandas DataFrame.
  See [data_loader/README.md](data_loader/README.md) for full documentation.

- **data_processor**  
  DataProcessor for column standardization, type conversion, missing value handling, and DataFrame preparation.
See [data_processor/README.md](data_processor/readme.md) for details and usage examples.
- **db_connector**  
  Universal connector for NeonDB and AWS LayeredDB.  
  Supports health checks, SQL execution, and automatic DataFrame population with schema/constraint awareness.  
  See [db_connector/README.md](db_connector/README.md) for details and usage examples.



---

## Data Population Workflow (NeonDB & AWS LayeredDB)

### 1. Load Data

```python
from data_loader.smart_auto_data_loader import SmartAutoDataLoader

loader = SmartAutoDataLoader(verbose=True)
raw_df = loader.load('data/tutorial_customers.csv')
## Project layout

├── db_population_utils/
│   ├── __init__.py
│   ├── db_connector/
│   │   ├── __init__.py
│   │   ├── db_connector.py
│   │   └── README.md
│   ├── data_loader/
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   └── README.md
│   ├── data_processor/
│   │   ├── __init__.py
│   │   ├── data_processor.py
│   │   └── README.md
│   └── data_populator/
│       ├── __init__.py
│       ├── db_populater.py
│       └── README.md
├── data/                            #row data for tests 
├── examples/
│   ├── example_usage.py
│   └── tutorial.ipynb
├── tests/
│   ├── test_db_connector_design.py
│   └── test_data_loader_design.py
└── README.md

````

---

## Components

- **DBConnector** *(MVP implemented)*: pooled connections for `ingestion` & `app`, health check, SQL exec, DataFrame I/O.
- **DataLoader** *(design stub)*: robust loading for CSV/TSV, Excel, JSON (encoding/delimiter sniffing, JSON flattening, datetime+TZ handling).
- **DataProcessor** *(design stub)*: common preprocessing (standardize columns, type coercion, nulls, dedupe, validation).


---

## Quick start

**End-to-end population example (NeonDB or AWS LayeredDB):**

```python
from data_loader.smart_auto_data_loader import SmartAutoDataLoader
from data_processor.data_processor import DataProcessor
from db_connector.smart_db_connector_enhanced_V3 import db_connector

# 1. Load data from file
loader = SmartAutoDataLoader(verbose=True)
raw_df = loader.load('data/tutorial_customers.csv')

# 2. Process and clean data
processor = DataProcessor()
type_hints = {'customer_id': 'int', 'has_subscription': 'bool'}
processed_df = processor.preprocess_loaded_data(
    raw_df,
    type_hints=type_hints,
    datetime_columns=['joined_date']
)

# 3. Connect to database (NeonDB by default)
db = db_connector()
schema_name = 'test_berlin_data'
table_name = 'tutorial_customers_quickstart'

# 4. Create table (drop if exists for demo)
db.query(f'DROP TABLE IF EXISTS {schema_name}.{table_name} CASCADE;', show_info=False)
db.query(f'''
CREATE TABLE {schema_name}.{table_name} (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    joined_date DATE,
    city VARCHAR(100),
    has_subscription BOOLEAN,
    district_id INTEGER,
    district VARCHAR(100),
    -- Foreign key constraint for LayeredDB (comment if districts table does not exists)
    ,CONSTRAINT fk_district_id FOREIGN KEY (district_id) REFERENCES {aws_schema_name}.districts(district_id)
);
''', show_info=False)

# 5. Populate data
db.populate(
    df=processed_df,
    table_name=table_name,
    schema=schema_name,
    mode='append',
    show_report=True
)

# 6. Verify
print(db.query(f"SELECT * FROM {schema_name}.{table_name} LIMIT 3"))
```

**To use with AWS LayeredDB:**  
Just create the connector with credentials:
```python
aws_db = db_connector(database='layereddb', username='USERNAME', password='PASSWORD')
# ...repeat steps 4-6 with aws_db...
```

See [tutorial.ipynb](tutorial.ipynb) for a full workflow and more advanced scenarios.
````