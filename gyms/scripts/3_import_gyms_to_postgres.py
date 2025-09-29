import pandas as pd
import os
from sqlalchemy import create_engine, text

# === CONFIG ===
DB_USER = "neondb_owner"
DB_PASS = "npg_CeS9fJg2azZD"
DB_HOST = "ep-falling-glitter-a5m0j5gk-pooler.us-east-2.aws.neon.tech"
DB_PORT = "5432"
DB_NAME = "neondb"
CSV_PATH = os.path.join('gyms/sources/gyms_with_district.csv')
TABLE_NAME = "gyms"

# === 1. Load and Clean CSV ===
df = pd.read_csv(CSV_PATH)
# Drop all columns with ".1" in their name (leftovers from joins)
df = df.drop(columns=[col for col in df.columns if ".1" in col], errors="ignore")

# --- district_id als sauberer VARCHAR ohne .0 ---
df['district_id'] = df['district_id'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x != '' else None)

# --- Wähle exakt die gewünschte Reihenfolge der Spalten (wie in deiner CSV) ---
final_cols = [
    "gym_id", "district_id", "name", "address", "postal_code", "phone_number",
    "email", "coordinates", "latitude", "longitude", "neighborhood", "district"
]
for col in final_cols:
    if col not in df.columns:
        df[col] = None  # Leere Spalten auffüllen, falls in CSV nicht vorhanden
df = df[final_cols]

print("Prepared DataFrame columns:", list(df.columns))
print(df.head(2))

# === 2. Connect to Database ===
conn_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)

with engine.connect() as conn:
    # --- 3. Create table if not exists (exakt die gewünschte Struktur) ---
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS gyms (
        gym_id VARCHAR(20) PRIMARY KEY,
        district_id VARCHAR(20),
        name VARCHAR(200),
        address VARCHAR(200),
        postal_code VARCHAR(10),
        phone_number VARCHAR(50),
        email VARCHAR(100),
        coordinates VARCHAR(200),
        latitude DECIMAL(9,6),
        longitude DECIMAL(9,6),
        neighborhood VARCHAR(100),
        district VARCHAR(100),
        CONSTRAINT district_id_fk FOREIGN KEY (district_id)
            REFERENCES test_berlin_data.districts(district_id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
    );
    """
    conn.execute(text(create_table_sql))
    print("Table 'gyms' checked/created.")

    # --- 4. Leeren vor neuem Import ---
    conn.execute(text(f"TRUNCATE {TABLE_NAME};"))
    print(f"Table '{TABLE_NAME}' was emptied (TRUNCATE).")

    # --- 5. Import mit Chunks ---
    df.to_sql(TABLE_NAME, engine, if_exists="append", index=False, chunksize=100)
    print(f"Imported {len(df)} rows into table '{TABLE_NAME}'.")

    # --- 6. (Optional) Geometrie-Spalte für PostGIS ---
    add_geom_sql = """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='gyms' AND column_name='geom'
        ) THEN
            ALTER TABLE gyms ADD COLUMN geom geometry(Point, 4326);
        END IF;
    END$$;
    """
    conn.execute(text(add_geom_sql))

    update_geom_sql = """
    UPDATE gyms SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    WHERE geom IS NULL AND longitude IS NOT NULL AND latitude IS NOT NULL;
    """
    conn.execute(text(update_geom_sql))
    print("Geometry column updated.")

print("Done importing gyms.")
