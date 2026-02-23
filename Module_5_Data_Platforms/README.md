# DE-zoomcamp
Data Engineering Zoomcamp

## Module 5: Data Platforms
Overview
In this module, you'll learn about data platforms - tools that help you manage the entire data lifecycle from ingestion to analytics.  

We'll use Bruin as an example of a data platform. Bruin puts multiple tools under one platform:  
- Data ingestion (extract from sources to your warehouse)  
- Data transformation (cleaning, modeling, aggregating)  
- Data orchestration (scheduling and dependency management)  
- Data quality (built-in checks and validation)  
- Metadata management (lineage, documentation)  

### Step 1: Install Bruin

#### Dockerfile
```
FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Bruin напрямую в системный путь
RUN curl -LsSf https://getbruin.com/install/cli | BINDIR=/usr/local/bin bash

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Проверяем наличие при сборке
RUN which bruin && bruin --version
```

#### docker-compose.yml
```
services:
  bruin:
    build: .
    image: bruin
    volumes:
      - ./project:/app
    working_dir: /app
    tty: true
    stdin_open: true
    command: sleep infinity
```

### Initialize Git
```
mkdir /module_5/project
cd project
Git init  
```

Build
```
docker compose build --no-cache
docker compose run --rm bruin bruin --version
docker compose up -d
```

### Basic Bruin`s commands
[Step-by-Step Tutorial](Module_5_Data_Platforms\Overview_End-to-End_Data_Platform.md)

