# DE-zoomcamp
Data Engineering Zoomcamp

## Module 6: Batch Processing

### Step 1: Install Spark for low memory
#### Dockerfile
```
# ─────────────────────────────────────────────
# Spark 4.0.0 + Python 3 + Jupyter
# Java 17 (required by Spark 4.x)
# Optimized for minimum resources (≤1.5 GB RAM for Spark)
# ─────────────────────────────────────────────
FROM eclipse-temurin:17-jre-jammy

ARG SPARK_VERSION=4.0.0
ARG HADOOP_VERSION=3

# ── System dependences ──────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        curl \
        procps \
    && rm -rf /var/lib/apt/lists/*

# ── Python-modules ─────────────────────────────
RUN pip3 install --no-cache-dir \
    "pyspark==4.0.0" \
    "jupyter==1.1.1" \
    "notebook==7.3.2" \
    "ipykernel==6.29.5" \
    "pandas==2.2.3" \
    "pyarrow==19.0.1"

# ── Spark ──────────
RUN curl -fsSL \
    "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    -o /tmp/spark.tgz && \
    tar -xzf /tmp/spark.tgz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm /tmp/spark.tgz

# ── Environment ───────────────────────
ENV SPARK_HOME=/opt/spark
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# ── Java 17 module flags (need for Spark 4.x) ─
# Without these flags Spark will be closed with InaccessibleObjectException
ENV JAVA_TOOL_OPTIONS="\
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.lang.invoke=ALL-UNNAMED \
--add-opens=java.base/java.lang.reflect=ALL-UNNAMED \
--add-opens=java.base/java.io=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.nio=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED \
--add-opens=java.base/java.util.concurrent=ALL-UNNAMED \
--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED \
--add-opens=java.base/sun.nio.ch=ALL-UNNAMED \
--add-opens=java.base/sun.nio.cs=ALL-UNNAMED \
--add-opens=java.base/sun.security.action=ALL-UNNAMED \
--add-opens=java.base/sun.util.calendar=ALL-UNNAMED \
-Djdk.reflect.useDirectMethodHandle=false"

# ── Spark config: lomit of memory ───────────
RUN mkdir -p /opt/spark/conf && \
    echo "spark.driver.memory              1200m"   >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.executor.memory            1200m"   >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.driver.memoryOverhead      256m"    >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.sql.shuffle.partitions     4"       >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.ui.enabled                 true"    >> /opt/spark/conf/spark-defaults.conf && \
    echo "spark.ui.port                    4040"    >> /opt/spark/conf/spark-defaults.conf

# ── Jupyter configuration ───────────────────────
RUN jupyter notebook --generate-config && \
    echo "c.ServerApp.ip = '0.0.0.0'"                         >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.port = 8888"                            >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.open_browser = False"                   >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.allow_root = True"                      >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.token = ''"                             >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.password = ''"                          >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.ServerApp.allow_origin = '*'"                     >> /root/.jupyter/jupyter_notebook_config.py

WORKDIR /workspace

EXPOSE 8888 4040

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
```

#### docker-compose.yml
```
services:

  spark:
    build: .
    container_name: spark
    hostname: spark-local

    # ── Recources limit ──────────
    mem_limit: 2g
    memswap_limit: 2g

    volumes:
      # Dir for notebook
      - ./notebooks:/workspace

    ports:
      # Jupyter Notebook
      - "8888:8888"
      # Spark Web UI
      - "4040:4040"

    environment:
      SPARK_HOME: /opt/spark
      JAVA_HOME: /opt/java/openjdk
      PYSPARK_PYTHON: python3
      PYSPARK_DRIVER_PYTHON: python3

    restart: unless-stopped
```

Use Browser  
http://localhost:8888/  
  
If need token:  
```
docker logs module_6-spark
```
Find http://127.0.0.1:8888/tree?token=<token>
In Browser in first login use this token  

If need kernel  
In terminal -> pip install ipykernel  
Register Kernel -> python3 -m ipykernel install --user --name pyspark
  
##### Check
01_spark_test.ipynb  

