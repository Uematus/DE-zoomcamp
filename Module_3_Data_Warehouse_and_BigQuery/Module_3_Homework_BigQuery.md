
## Question 1. Counting records
What is count of records for the 2024 Yellow Taxi Data?  
```
SELECT
  count(*)
FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata`;
```

20 332 093

## Question 2. Data read estimation
Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?  
```
SELECT 
  count(distinct PULocationID)
FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata`;
```

0 MB for the External Table and 155.12 MB for the Materialized Table

## Question 3. Understanding columnar storage
Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?  

BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.  

## Question 4. Counting zero fare trips
How many records have a fare_amount of 0?  
```
SELECT
  count(fare_amount)
FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata`
WHERE fare_amount = 0;
```

8 333  

## Question 5. Partitioning and clustering
What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)  

Partition by tpep_dropoff_datetime and Cluster on VendorID  

## Question 6. Partition benefits
Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive)

Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values?

Choose the answer which most closely matches.  

310.24 MB for non-partitioned table and 26.84 MB for the partitioned table

## Question 7. External table storage
Where is the data stored in the External Table you created?  

GCP Bucket

## Question 8. Clustering best practices
It is best practice in Big Query to always cluster your data:  

False



