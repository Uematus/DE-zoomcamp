# DE-zoomcamp
Data Engineering Zoomcamp

## Workshop - dlt
### From APIs to Warehouses: AI-Assisted Data Ingestion with dlt

In this workshop, you'll use an AI-powered IDE to build a complete data pipeline. Using simple prompts, you can go from an API to a local data warehouse with dlt (data load tool). The AI handles the code generation. You focus on the results.

### Step 1: Install dlt

#### Dockerfile
```
FROM python:3.13-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Setup Python
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Project`s workdir
WORKDIR /app

# Update pip and install dlt with DuckDB
RUN pip install --upgrade pip && \
    pip install "dlt[duckdb]"
    pip install "dlt[workspace]"

# Check dlt instalation
RUN python -c "import dlt; print(f'dlt version: {dlt.__version__}')"

CMD ["sleep", "infinity"]
```

#### docker-compose.yml
```
services:
  dlt:
    build: .
    image: dlt-duckdb
    container_name: dlt

    volumes:
      - ./project:/app

    working_dir: /app

    tty: true
    stdin_open: true

    command: sleep infinity
```


### Init a project
```
dlt init dlthub:taxi_pipeline duckdb
```

### Pipeline
nano taxi_pipeline.py
```
import dlt
from dlt.sources.rest_api import rest_api_source
from dlt.sources.rest_api.config_setup import PageNumberPaginator

def get_taxi_source():
    return rest_api_source(
        {
            "client": {
                "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
            },
            "resources": [
                {
                    "name": "taxi_data",
                    "endpoint": {
                        "path": "/",
                        "params": {
                            "page_size": 1000
                        },
                        "paginator": PageNumberPaginator(
                            page_param="page",
                            base_page=1,
                            stop_after_empty_page=True,
                            total_path=None,
                        ),
                    },
                }
            ],
        }
    )

pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    refresh="drop_sources",
    progress="log",
)

if __name__ == "__main__":
    load_info = pipeline.run(get_taxi_source())
    print(load_info)
```

#### Run pipeline
```
python taxi_pipeline.py
```

#### Show pipeline details and run SQL Query
```
dlt pipeline taxi_pipeline show
```