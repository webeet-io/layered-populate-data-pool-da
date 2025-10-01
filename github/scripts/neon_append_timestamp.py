import os
import sys
import psycopg2

DB_URL = os.environ.get("NEON_DB_URL")
if not DB_URL:
    print("ERROR: NEON_DB_URL is not set.")
    sys.exit(1)

# Метаданные ранa из GitHub
RUN_ID = os.environ.get("GITHUB_RUN_ID")
GIT_REF = os.environ.get("GITHUB_REF_NAME")
GIT_SHA = os.environ.get("GITHUB_SHA")

DDL = """
CREATE TABLE IF NOT EXISTS immowelt_test_appends (
    id BIGSERIAL PRIMARY KEY,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    workflow_run_id TEXT,
    git_ref TEXT,
    git_sha TEXT
);
"""

INSERT_SQL = """
INSERT INTO immowelt_test_appends (workflow_run_id, git_ref, git_sha)
VALUES (%s, %s, %s)
RETURNING id, inserted_at;
"""

SELECT_LAST = """
SELECT id, inserted_at, workflow_run_id, git_ref, git_sha
FROM immowelt_test_appends
ORDER BY inserted_at DESC
LIMIT 3;
"""

try:
    # sslmode=require важен для Neon
    conn = psycopg2.connect(DB_URL, sslmode="require")
    conn.autocommit = False
    with conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute(INSERT_SQL, (RUN_ID, GIT_REF, GIT_SHA))
            new_id, ts = cur.fetchone()
            print(f"Inserted row id={new_id}, inserted_at={ts}")

            cur.execute(SELECT_LAST)
            rows = cur.fetchall()
            print("Last rows:")
            for r in rows:
                print(r)
except Exception as e:
    print("ERROR while appending timestamp:", e)
    sys.exit(1)
finally:
    try:
        conn.close()
    except Exception:
        pass
