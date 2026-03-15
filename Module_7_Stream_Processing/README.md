# DE-zoomcamp
Data Engineering Zoomcamp

## Module 7: Stream Processing

### Installation
For low resources  

#### Dockerfile.flink
```bash
FROM flink:1.18-java17

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        wget \
        ca-certificates && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    apache-flink==1.18.0 \
    kafka-python-ng \
    pandas \
    pyarrow \
    psycopg2-binary

RUN mkdir -p /opt/flink/lib && \
    wget -q -P /opt/flink/lib https://repo1.maven.org/maven2/org/apache/flink/flink-json/1.18.0/flink-json-1.18.0.jar && \
    wget -q -P /opt/flink/lib https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.1.0-1.18/flink-connector-kafka-3.1.0-1.18.jar && \
    wget -q -P /opt/flink/lib https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar && \
    wget -q -P /opt/flink/lib https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.2.0-1.18/flink-connector-jdbc-3.2.0-1.18.jar && \
    wget -q -P /opt/flink/lib https://jdbc.postgresql.org/download/postgresql-42.7.3.jar

RUN chown -R flink:flink /opt/flink
USER flink
WORKDIR /opt/flink
```

#### flink-conf.yaml
```bash
jobmanager.rpc.address: flink
taskmanager.numberOfTaskSlots: 1
parallelism.default: 1

# limit 800M
jobmanager.memory.process.size: 350m
taskmanager.memory.process.size: 400m

taskmanager.memory.flink.size: 250m
taskmanager.memory.jvm-metaspace.size: 64m
taskmanager.memory.jvm-overhead.min: 64m
taskmanager.memory.jvm-overhead.max: 100m

blob.server.port: 6124
query.server.port: 6125
rest.port: 8081
```

#### Dockerfile.python
```bash
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Установка библиотек (используем стабильные версии)
RUN pip install --no-cache-dir \
    jupyter==1.1.1 \
    notebook==7.3.2 \
    ipykernel==6.29.5 \
    pandas==2.2.3 \
    kafka-python-ng \
    psycopg2-binary \
    pyarrow==19.0.1

# Конфигурация Jupyter для работы без токена
RUN jupyter notebook --generate-config && \
    echo "c.ServerApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.password = ''" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.allow_origin = '*'" >> /root/.jupyter/jupyter_notebook_config.py

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
```

#### docker-compose.yml
```bash
services:
  redpanda:
    image: redpandadata/redpanda:v23.3.5
    command:
      - redpanda
      - start
      - --overprovisioned
      - --smp=1
      - --memory=256M
      - --reserve-memory=0M
      - --node-id=0
      - --check=false
      - --kafka-addr=PLAINTEXT://0.0.0.0:9092
      - --advertise-kafka-addr=PLAINTEXT://redpanda:9092
    ports:
      - "9092:9092"
    healthcheck:
      test: ["CMD", "rpk", "cluster", "info"]
      interval: 5s
    deploy:
      resources:
        limits:
          memory: 400M

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 256M

  flink:
    build:
      context: .
      dockerfile: Dockerfile.flink
    command: jobmanager
    ports:
      - "8081:8081"
    volumes:
      - ./src:/opt/src
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: flink
        jobmanager.memory.process.size: 800m
        jobmanager.memory.jvm-metaspace.size: 128m
        jobmanager.memory.jvm-overhead.min: 64m
    deploy:
      resources:
        limits:
          memory: 1000M

  taskmanager:
    build:
      context: .
      dockerfile: Dockerfile.flink
    command: taskmanager
    depends_on:
      - flink
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: flink
        taskmanager.numberOfTaskSlots: 1
        # Увеличиваем общий процесс, но зажимаем внутренние части
        taskmanager.memory.process.size: 800m
        taskmanager.memory.framework.heap.size: 64m
        taskmanager.memory.framework.off-heap.size: 64m
        taskmanager.memory.jvm-metaspace.size: 128m
        taskmanager.memory.jvm-overhead.min: 64m
        taskmanager.memory.network.min: 64m
        taskmanager.memory.network.max: 64m
        taskmanager.memory.managed.size: 64m
    deploy:
      resources:
        limits:
          memory: 1000M

  python:
    build:
      context: .
      dockerfile: Dockerfile.python
    container_name: module_7-python
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/workspace
    deploy:
      resources:
        limits:
          memory: 800M
    depends_on:
      redpanda:
        condition: service_healthy

volumes:
  postgres_data:
```

##### Check:
Redpanda: localhost:8082  
Jupiter: localhost:8888

### Tasks
Create a topic called green-trips:
```bash
docker exec -it module_7-redpanda-1 rpk topic create green-trips
```

Check all topics:
```bash
rpk topic list
```

Check data inside topic
```bash
rpk topic consume green-trips
```

Count of records in topic
```bash
rpk topic describe green-trips -p
```
Столбец HIGH-WATERMARK


#### Q4
#### PostgreSQL
```bash
docker exec -it module_7-postgres-1 psql -U postgres

# Create table
CREATE TABLE IF NOT EXISTS pickup_counts (
    window_start TIMESTAMP,
    PULocationID INT,
    num_trips BIGINT);
```

#### Create script Flink
```
/home/purogen/zoomcamp/module_7
$ ls
docker-compose.yml  Dockerfile.flink  Dockerfile.python  flink-conf.yaml  notebooks  src
$ cd src
$ ls
$ mkdir job
mkdir: cannot create directory ‘job’: Permission denied
$ cd ..
$ sudo chown -R $USER:$USER src
$ cd src
$ mkdir job
$ cd job
$ pwd
/home/purogen/zoomcamp/module_7/src/job
```

##### PyFlink script (/src/job/pickup_job.py)
```py
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
```

Execution
```bash
docker exec -it module_7-flink-1 flink run -py /opt/src/job/pickup_job.py
```

##### Result
```sql
SELECT PULocationID, num_trips
FROM pickup_counts
ORDER BY num_trips DESC
LIMIT 3;
```

#### Q5
#### PostgreSQL
```bash
docker exec -it module_7-postgres-1 psql -U postgres
```
# Create table
```sql
CREATE TABLE IF NOT EXISTS session_counts (
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    PULocationID INT,
    num_trips BIGINT);
```

##### PyFlink script (/src/job/session_job.py)
```py
from pyflink.table import EnvironmentSettings, TableEnvironment

def run_session_job():
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = TableEnvironment.create(settings)
    t_env.get_config().set_local_timezone("UTC")
    
    # Source
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
            'properties.group.id' = 'flink-session-group',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """
    t_env.execute_sql(source_ddl)

    # Destination
    sink_ddl = """
        CREATE TABLE jdbc_sink (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            PULocationID INT,
            num_trips BIGINT
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'session_counts',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        )
    """
    t_env.execute_sql(sink_ddl)

    # Session Window
    t_env.execute_sql("""
        INSERT INTO jdbc_sink
        SELECT 
            SESSION_START(event_timestamp, INTERVAL '5' MINUTE) AS window_start,
            SESSION_END(event_timestamp, INTERVAL '5' MINUTE) AS window_end,
            PULocationID,
            COUNT(*) AS num_trips
        FROM green_trips
        GROUP BY 
            PULocationID, 
            SESSION(event_timestamp, INTERVAL '5' MINUTE)
    """)

if __name__ == '__main__':
    run_session_job()
```

Execution
```bash
docker exec -it module_7-flink-1 flink run -py /opt/src/job/session_job.py
```

##### Result
```sql
SELECT PULocationID, num_trips
FROM session_counts
ORDER BY num_trips DESC
LIMIT 1;
```

#### Q6
#### PostgreSQL
```bash
docker exec -it module_7-postgres-1 psql -U postgres
```
# Create table
```sql
CREATE TABLE IF NOT EXISTS tip_stats (
    window_start TIMESTAMP,
    total_tip FLOAT);
```

##### PyFlink script (/src/job/tips_job.py)
```py
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
```

Execution
```bash
docker exec -it module_7-flink-1 flink run -py /opt/src/job/tips_job.py
```

##### Result
```sql
SELECT window_start, total_tip
FROM tip_stats
ORDER BY total_tip DESC
LIMIT 1;
```