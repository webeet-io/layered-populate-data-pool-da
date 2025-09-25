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

# --- 1. Read CSV and DROP all duplicate .1 columns ---
df = pd.read_csv(CSV_PATH)
df = df.drop(columns=[col for col in df.columns if ".1" in col], errors="ignore")

# --- 2. Insert Data (replace or append as needed) ---
with engine.connect() as conn:
    # Delete duplicate columns, if exists
    conn.execute(text('ALTER TABLE gyms DROP COLUMN IF EXISTS "district_id.1";'))

    # Create table if not exists
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
        district_id VARCHAR,
        district VARCHAR
    );
    """
    conn.execute(text(create_table_sql))
    print("Table 'gyms' checked/created.")

    # *** Delete Table before import ***
    truncate_sql = f"TRUNCATE {TABLE_NAME};"
    conn.execute(text(truncate_sql))
    print(f"Table '{TABLE_NAME}' was emptied (TRUNCATE).")

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
# --- End of Script ---