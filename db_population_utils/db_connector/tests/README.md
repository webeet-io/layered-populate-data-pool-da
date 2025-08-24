# Smart DB Connector V3 - Functional Constraint Testing

This document explains the testing methodology used in `test_constraints_final.ipynb` to verify that the `Smart DB Connector V3` correctly handles database constraints.

## Test Objectives

The primary goal of this test is to ensure that the `populate()` function can insert data into tables with pre-existing `PRIMARY KEY` and `FOREIGN KEY` constraints without disabling or removing them. The test is designed to be functional, meaning it actively tries to violate constraints to confirm they are enforced by the database.

## Testing Methodology

The test is performed across two different PostgreSQL databases (NeonDB and AWS LayeredDB) to ensure broad compatibility.

### Step 1: Database Connection

The script begins by establishing connections to both NeonDB and AWS LayeredDB using the `db_connector`.

### Step 2: Dynamic Foreign Key (FK) Column Detection

A critical feature of the test is its ability to adapt to different database schemas.
1.  It inspects the `districts` table in each database.
2.  It dynamically identifies the correct column to use for the Foreign Key relationship. In NeonDB, this is the `district` column, while in AWS LayeredDB, it is `district_id`.
This ensures the test logic is not hard-coded to a specific schema.

### Step 3: Test Table Creation

1.  A new table with a unique name (e.g., `smart_banks_test_...`) is created in both databases.
2.  The `CREATE TABLE` statement explicitly defines a `PRIMARY KEY` on the `bank_id` column and a `FOREIGN KEY` constraint on the `district_id` column, which references the `districts` table.
3.  **Transaction Handling**: The DDL statements are wrapped in a transaction (`conn.begin()` and `trans.commit()`) to ensure atomicity, which is critical for PostgreSQL.

### Step 4: Data Population with `mode='append'`

1.  A sample Pandas DataFrame is created with valid data.
2.  The `db.populate()` function is called with `mode='append'`.
3.  **Critical Insight**: Using `mode='append'` is the only method that preserves the existing table structure, including its constraints. Other modes, like `'replace'`, would drop and recreate the table, destroying the constraints.

### Step 5: Functional Constraint Verification

This is the core of the test, where we verify the constraints are active and enforced.

1.  **Primary Key Test**:
    -   An attempt is made to insert a new row with a `bank_id` that already exists in the table.
    -   **Expected Outcome**: The database rejects the insertion and raises a `UniqueViolation` (or similar) error. The test succeeds if this specific error is caught.

2.  **Foreign Key Test**:
    -   An attempt is made to insert a new row with a `district_id` that does not exist in the parent `districts` table.
    -   **Expected Outcome**: The database rejects the insertion and raises a `ForeignKeyViolation` error. The test succeeds if this specific error is caught.

### Step 6: Final Verification

After all population and violation attempts, the script queries the database's information schema to confirm that the original `PRIMARY KEY` and `FOREIGN KEY` constraints are still attached to the table.

## Key Insights and Conclusion

-   **Production Ready**: The `Smart DB Connector V3` is confirmed to work correctly with database constraints when the proper methodology is followed.
-   **`mode='append'` is Essential**: This is the key to working with existing table structures and preserving constraints.
-   **Dynamic and Functional Testing**: The test is robust because it adapts to different schemas and functionally validates that constraints are not just present, but actively enforced by the database.

The successful completion of these tests on both database platforms demonstrates that the connector is reliable for use in a production environment where data integrity is enforced by database constraints.
