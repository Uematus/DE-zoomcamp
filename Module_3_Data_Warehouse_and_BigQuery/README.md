# DE-zoomcamp
Data Engineering Zoomcamp

## Big Query

### Create DataSet
In Google Cloud - Big Query  
Create Dataset: ny_taxi  
In Dataset Create Table: Upload each file {yellow_tripdata_2024_0*}  

### Check Tables
```
SELECT
  table_id,
  row_count,
  ROUND(size_bytes/1024/1024, 2) as size_mb
FROM `de-zoomcamp-484910.ny_taxi.__TABLES__`
WHERE table_id LIKE 'yellow_tripdata_2024%'
ORDER BY table_id;
```
  
Union all tables into one table
```
CREATE OR REPLACE TABLE `de-zoomcamp-484910.ny_taxi.yellow_tripdata` AS
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_01`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_02`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_03`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_04`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_05`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_06`;
```
  
Create View
```
CREATE OR REPLACE VIEW `de-zoomcamp-484910.ny_taxi.external_yellow_tripdata` AS
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_01`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_02`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_03`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_04`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_05`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_06`;
```
  
Create partitioned and clustered table  
```
CREATE OR REPLACE TABLE `de-zoomcamp-484910.ny_taxi.yellow_tripdata_part_clust`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata`;
```