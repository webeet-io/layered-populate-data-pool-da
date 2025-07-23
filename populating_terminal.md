- host: psql -h layered-data-warehouse.cdg2ok68acsn.eu-central-1.rds.amazonaws.com -p 5432 -U postgres -d berlin_project_db -W
- password: b319nnlsekSOfIiVDpRC
- checking the tables in schema:
  
  SELECT table_name
  FROM information_schema.tables
  WHERE table_schema = 'berlin_data';
  
- checking the constraints in the table:
  
  SELECT
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
  FROM
      information_schema.table_constraints AS tc
  JOIN
      information_schema.key_column_usage AS kcu
  ON
      tc.constraint_name = kcu.constraint_name
  AND
      tc.table_schema = kcu.table_schema
  WHERE
      tc.table_schema = 'berlin_data' AND tc.table_name = 'employees';

- alternatively you can do **\d+ table_name**
- the way to populate with csv file:

  \copy berlin_data.employees (id, name) FROM '/path/to/your/employees.csv' DELIMITER ',' CSV HEADER;

- to initiate postgis:

  CREATE EXTENSION postgis;
