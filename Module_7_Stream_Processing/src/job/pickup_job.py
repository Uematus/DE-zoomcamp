import os
from pyflink.table import EnvironmentSettings, TableEnvironment

def run_pickup_job():
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = TableEnvironment.create(settings)
    t_env.get_config().set_local_timezone("UTC")
    
    # 1. Source: Kafka (Redpanda)
    source_ddl = """
        CREATE TABLE green_trips (
            lpep_pickup_datetime BIGINT,
            PULocationID INT,
            event_timestamp AS TO_TIMESTAMP(FROM_UNIXTIME(lpep_pickup_datetime / 1000)),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda:9092',
            'properties.group.id' = 'flink-consumer-group-1',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """
    t_env.execute_sql(source_ddl)

    # 2. Destionation: PostgreSQL
    sink_ddl = """
        CREATE TABLE jdbc_sink (
            window_start TIMESTAMP(3),
            PULocationID INT,
            num_trips BIGINT
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'pickup_counts',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        )
    """
    t_env.execute_sql(sink_ddl)

    t_env.execute_sql("""
        INSERT INTO jdbc_sink
        SELECT 
            TUMBLE_START(event_timestamp, INTERVAL '5' MINUTE) AS window_start,
            PULocationID,
            COUNT(*) AS num_trips
        FROM green_trips
        GROUP BY 
            PULocationID, 
            TUMBLE(event_timestamp, INTERVAL '5' MINUTE)
    """)

if __name__ == '__main__':
    run_pickup_job()
