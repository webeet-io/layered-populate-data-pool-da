# import_gyms_to_postgres.py

"""
Import cleaned gyms data into PostgreSQL using SQLAlchemy.
- Reads gyms_with_district.csv
- Inserts into 'gyms' table (must match your DB schema!)
"""

import pandas as pd
from sqlalchemy import create_engine, text

# --- Config (edit to your settings) ---
DB_USER = "neondb_owner"
DB_PASS = "npg_CeS9fJg2azZD"
DB_HOST = "ep-falling-glitter-a5m0j5gk-pooler.us-east-2.aws.neon.tech"
DB_PORT = "5432"
DB_NAME = "neondb"

CSV_PATH = "gyms/sources/gyms_with_district.csv"
TABLE_NAME = "gyms"

# Build connection string
conn_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)

# --- 1. Read CSV ---
df = pd.read_csv(CSV_PATH)

# --- 2. Insert Data (replace or append as needed) ---
with engine.connect() as conn:
    # Optional: Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS gyms (
        id SERIAL PRIMARY KEY,
        name TEXT,
        street TEXT,
        housenumber TEXT,
        postcode TEXT,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        opening_hours TEXT,
        phone TEXT,
        website TEXT,
        wheelchair TEXT,
        osm_id TEXT,
        osm_type TEXT,
        source TEXT,
        district_id VARCHAR(20),
        district TEXT
    );
    """
    conn.execute(text(create_table_sql))
    print("Table 'gyms' checked/created.")

    # --- Insert data ---
    df.to_sql(TABLE_NAME, engine, if_exists="append", index=False)
    print(f"Imported {len(df)} rows into table '{TABLE_NAME}'.")

    # --- Optional: Add PostGIS geometry column and update with lat/lon ---
    add_geom_sql = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='gyms' AND column_name='geom') THEN
            ALTER TABLE gyms ADD COLUMN geom geometry(Point, 4326);
        END IF;
    END$$;
    """
    conn.execute(text(add_geom_sql))

    update_geom_sql = """
    UPDATE gyms SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    WHERE geom IS NULL;
    """
    conn.execute(text(update_geom_sql))
    print("Geometry column updated.")

# --- Done! ---
print("Done importing gyms.")
