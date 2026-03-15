## Question 1. Redpanda version
Run rpk version inside the Redpanda container:
  
```
docker exec -it module_7-redpanda-1 rpk version
```

v23.3.5

## Question 2. Sending data to Redpanda
Create a topic called green-trips:
```
docker exec -it module_7-redpanda-1 rpk topic create green-trips
```

Now write a producer to send the green taxi data to this topic.

Read the parquet file and keep only these columns:

* lpep_pickup_datetime
* lpep_dropoff_datetime
* PULocationID
* DOLocationID
* passenger_count
* trip_distance
* tip_amount
* total_amount

Convert each row to a dictionary and send it to the green-trips topic. You'll need to handle the datetime columns - convert them to strings before serializing to JSON.

Measure the time it takes to send the entire dataset and flush:
```
from time import time

t0 = time()

# send all rows ...

producer.flush()

t1 = time()
print(f'took {(t1 - t0):.2f} seconds')
How long did it take to send the data?
```

took 538.07 seconds

## Question 3. Consumer - trip distance
Write a Kafka consumer that reads all messages from the green-trips topic (set auto_offset_reset='earliest').

Count how many trips have a trip_distance greater than 5.0 kilometers.

How many trips have trip_distance > 5?

8506

## Question 4. Tumbling window - pickup location
Create a Flink job that reads from green-trips and uses a 5-minute tumbling window to count trips per PULocationID.

Write the results to a PostgreSQL table with columns: window_start, PULocationID, num_trips.

After the job processes all data, query the results:
```sql
SELECT PULocationID, num_trips
FROM <your_table>
ORDER BY num_trips DESC
LIMIT 3;
```
Which PULocationID had the most trips in a single 5-minute window?

74

## Question 5. Session window - longest streak
Create another Flink job that uses a session window with a 5-minute gap on PULocationID, using lpep_pickup_datetime as the event time with a 5-second watermark tolerance.

A session window groups events that arrive within 5 minutes of each other. When there's a gap of more than 5 minutes, the window closes.

Write the results to a PostgreSQL table and find the PULocationID with the longest session (most trips in a single session).

How many trips were in the longest session?

81

## Question 6. Tumbling window - largest tip
Create a Flink job that uses a 1-hour tumbling window to compute the total tip_amount per hour (across all locations).

Which hour had the highest total tip amount?

2025-10-16 18:00:00