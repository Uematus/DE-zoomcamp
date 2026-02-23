/* @bruin

name: main.query
type: duckdb.sql
connection: duckdb-default

materialization:
  type: table

@bruin */

SELECT
    *
FROM ingestion.trips
--limit 100
