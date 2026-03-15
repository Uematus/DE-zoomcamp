from pyflink.table import EnvironmentSettings, TableEnvironment

def run_tips_job():
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = TableEnvironment.create(settings)
    t_env.get_config().set_local_timezone("UTC")
    
    # Source
    source_ddl = """
        CREATE TABLE green_trips (
            lpep_pickup_datetime BIGINT,
            tip_amount DOUBLE,
            event_timestamp AS TO_TIMESTAMP(FROM_UNIXTIME(lpep_pickup_datetime / 1000)),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda:9092',
            'properties.group.id' = 'flink-tips-group',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """
    t_env.execute_sql(source_ddl)

    # 2. Destination
    sink_ddl = """
        CREATE TABLE jdbc_sink (
            window_start TIMESTAMP(3),
            total_tip DOUBLE
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'tip_stats',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        )
    """
    t_env.execute_sql(sink_ddl)

    t_env.execute_sql("""
        INSERT INTO jdbc_sink
        SELECT 
            TUMBLE_START(event_timestamp, INTERVAL '1' HOUR) AS window_start,
            SUM(tip_amount) AS total_tip
        FROM green_trips
        GROUP BY 
            TUMBLE(event_timestamp, INTERVAL '1' HOUR)
    """)

if __name__ == '__main__':
    run_tips_job()
