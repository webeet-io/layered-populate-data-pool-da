scripts/kindergardens_data_transformation.ipynb
## Day 5: Table Finalization & Test Insert (Kindergartens)

**Table**: `test_berlin_data.kindergardens`  
**PK**: `kindergarten_id`  
**FK (planned/enabled)**: `district_id` → `test_berlin_data.districts(district_id)`

**Creation SQL**: see `/sql/kindergardens_table.sql`  
**Import**: DBeaver CSV import of `kindergartens_berlin_final_ready.csv`

**Validation results**
- Row count: 2,298
- Outside Berlin bounds: <n>
- NULL `district_id`: <n>
- Contact sanity: bad_emails <n>, bad_websites <n>, bad_phones <n>
- PK duplicates: 0

**Assumptions & adjustments**
- Some `district_id` may be NULL initially; postcode/spatial fallback planned
- FK enforced once coverage is complete
- Indexes added for district_id, name, and (lat, lon)

sql/kindergardens_validation.sql
-- Row count
SELECT COUNT(*) AS row_count
FROM test_berlin_data.kindergardens;

-- Coordinates within Berlin bounds
SELECT COUNT(*) AS outside_bounds
FROM test_berlin_data.kindergardens
WHERE latitude NOT BETWEEN 52.3 AND 52.7
   OR longitude NOT BETWEEN 13.1 AND 13.7;

-- Remaining NULL district_id
SELECT COUNT(*) AS null_district_id
FROM test_berlin_data.kindergardens
WHERE district_id IS NULL;

-- Contacts sanity
SELECT
  COUNT(*) FILTER (WHERE email IS NULL OR email='' OR email ILIKE 'unknown' OR email NOT LIKE '%@%') AS bad_emails,
  COUNT(*) FILTER (WHERE website IS NULL OR website='' OR website ILIKE 'unknown' OR website NOT LIKE 'http%') AS bad_websites,
  COUNT(*) FILTER (WHERE phone_number IS NULL OR phone_number='' OR phone_number ILIKE 'unknown') AS bad_phones
FROM test_berlin_data.kindergardens;

-- Duplicates on PK
SELECT kindergarten_id, COUNT(*)
FROM test_berlin_data.kindergardens
GROUP BY kindergarten_id
HAVING COUNT(*) > 1;
