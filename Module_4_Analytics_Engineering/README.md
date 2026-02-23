# DE-zoomcamp
Data Engineering Zoomcamp

## Module 4: Analytics Engineering
Goal: Transforming the data loaded in DWH into Analytical Views developing a dbt project.  

### Step 1: Install DuckDB
mkdir models  
mkdir data  

nano Dockerfile
```
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем dbt-duckdb
RUN pip install --no-cache-dir dbt-duckdb==1.7.1

# Рабочая директория
WORKDIR /usr/app

# Копируем проект
COPY . .

# Создаем папку для базы если её нет
RUN mkdir -p /usr/app/data

# Переменная окружения для профиля
ENV DBT_PROFILES_DIR=/usr/app

CMD ["bash"]
```

nano profiles.yml
```
taxi_rides_ny:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /usr/app/data/taxi_rides_ny.duckdb
      schema: dev
      threads: 1
      extensions:
        - parquet
      settings:
        memory_limit: '1GB'
        preserve_insertion_order: false

    prod:
      type: duckdb
      path: /usr/app/data/taxi_rides_ny.duckdb
      schema: prod
      threads: 1
      extensions:
        - parquet
      settings:
        memory_limit: '1GB'
        preserve_insertion_order: false

```

nano docker-compose.yml
```
version: '3.8'

services:
  dbt:
    build: .
    container_name: dbt_duckdb
    volumes:
      - .:/usr/app
    working_dir: /usr/app
    stdin_open: true
    tty: true
```

docker compose up -d  

Установка nano внутри контейнера
apt update && apt install nano -y

Внутри контрейнера создание проекта, если не создался сам
nano dbt_project.yml
```
name: 'taxi_rides_ny'
version: '1.0.0'
config-version: 2

profile: 'taxi_rides_ny'

model-paths: ["models"]
analysis-paths: ["analysis"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  taxi_rides_ny:
    +materialized: table

```

Перезапуск контейнера

Проверка работы dbt
dbt debug

Внцтри контейнера должен появится файл
/usr/app/data/taxi_rides_ny.duckdb

### Step 2: Download and Ingest Data
Скрипт загрузки (внутри контейнера в папке /usr/app)
#### Пряма полная загрузка
```
import duckdb
import requests
from pathlib import Path

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

def download_and_convert_files(taxi_type):
    data_dir = Path("data") / taxi_type
    data_dir.mkdir(exist_ok=True, parents=True)

    for year in [2019, 2020]:
        for month in range(1, 13):
            parquet_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            parquet_filepath = data_dir / parquet_filename

            if parquet_filepath.exists():
                print(f"Skipping {parquet_filename} (already exists)")
                continue

            # Download CSV.gz file
            csv_gz_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.csv.gz"
            csv_gz_filepath = data_dir / csv_gz_filename

            response = requests.get(f"{BASE_URL}/{taxi_type}/{csv_gz_filename}", stream=True)
            response.raise_for_status()

            with open(csv_gz_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Converting {csv_gz_filename} to Parquet...")
            con = duckdb.connect()
            con.execute(f"""
                COPY (SELECT * FROM read_csv_auto('{csv_gz_filepath}'))
                TO '{parquet_filepath}' (FORMAT PARQUET)
            """)
            con.close()

            # Remove the CSV.gz file to save space
            csv_gz_filepath.unlink()
            print(f"Completed {parquet_filename}")

def update_gitignore():
    gitignore_path = Path(".gitignore")

    # Read existing content or start with empty string
    content = gitignore_path.read_text() if gitignore_path.exists() else ""

    # Add data/ if not already present
    if 'data/' not in content:
        with open(gitignore_path, 'a') as f:
            f.write('\n# Data directory\ndata/\n' if content else '# Data directory\ndata/\n')

if __name__ == "__main__":
    # Update .gitignore to exclude data directory
    update_gitignore()

    for taxi_type in ["yellow", "green"]:
        download_and_convert_files(taxi_type)

    con = duckdb.connect("data/taxi_rides_ny.duckdb")
    con.execute("CREATE SCHEMA IF NOT EXISTS prod")

### Не хватило ресурсов сервера, полная загрузка не прошла
    for taxi_type in ["yellow", "green"]:
        con.execute(f"""
            CREATE OR REPLACE TABLE prod.{taxi_type}_tripdata AS
            SELECT * FROM read_parquet('data/{taxi_type}/*.parquet', union_by_name=true)
        """)

    con.close()
```

#### Для снижения нагрузки на RAM
```
import duckdb
import requests
from pathlib import Path
import gc

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

def download_and_convert_files(taxi_type):
    data_dir = Path("data") / taxi_type
    data_dir.mkdir(exist_ok=True, parents=True)

    for year in [2019, 2020]:
        for month in range(1, 13):
            parquet_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            parquet_filepath = data_dir / parquet_filename

            if parquet_filepath.exists():
                print(f"Skipping {parquet_filename} (already exists)")
                continue

            # Download CSV.gz file
            csv_gz_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.csv.gz"
            csv_gz_filepath = data_dir / csv_gz_filename

            response = requests.get(f"{BASE_URL}/{taxi_type}/{csv_gz_filename}", stream=True)
            response.raise_for_status()

            with open(csv_gz_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Converting {csv_gz_filename} to Parquet...")
            con = duckdb.connect()
            con.execute(f"""
                COPY (SELECT * FROM read_csv_auto('{csv_gz_filepath}'))
                TO '{parquet_filepath}' (FORMAT PARQUET)
            """)
            con.close()

            # Remove the CSV.gz file to save space
            csv_gz_filepath.unlink()
            print(f"Completed {parquet_filename}")

def update_gitignore():
    gitignore_path = Path(".gitignore")

    # Read existing content or start with empty string
    content = gitignore_path.read_text() if gitignore_path.exists() else ""

    # Add data/ if not already present
    if 'data/' not in content:
        with open(gitignore_path, 'a') as f:
            f.write('\n# Data directory\ndata/\n' if content else '# Data directory\ndata/\n')

if __name__ == "__main__":
    # Update .gitignore to exclude data directory
    update_gitignore()

    for taxi_type in ["yellow", "green"]:
        download_and_convert_files(taxi_type)

    con = duckdb.connect("data/taxi_rides_ny.duckdb")
    
    # Уменьшаем лимит памяти для безопасности
    con.execute("SET memory_limit='500MB'")  # Снижено с 1000MB
    con.execute("SET threads=1")
    
    # ИЗМЕНЕНИЕ 3: Настраиваем временную директорию для spill to disk
    Path("data/tmp").mkdir(exist_ok=True, parents=True)
    con.execute("SET temp_directory='data/tmp'")
    
    # ИЗМЕНЕНИЕ 4: Отключаем кэширование для минимизации использования памяти
    con.execute("SET enable_object_cache=false")
    
    con.execute("CREATE SCHEMA IF NOT EXISTS prod")

    for taxi_type in ["yellow", "green"]:
        parquet_files = sorted(Path(f"data/{taxi_type}").glob("*.parquet"))

        if not parquet_files:
            continue

        print(f"\nProcessing {taxi_type}")

        # ИЗМЕНЕНИЕ 5: Создаём таблицу с явной схемой из первого файла
        con.execute(f"""
            CREATE OR REPLACE TABLE prod.{taxi_type}_tripdata AS
            SELECT * FROM read_parquet('{parquet_files[0]}')
            LIMIT 0
        """)

        # ИЗМЕНЕНИЕ 6: Обрабатываем каждый файл по отдельности
        for file in parquet_files:
            print(f"Loading {file.name}")

            # ИЗМЕНЕНИЕ 7: Используем одну атомарную операцию вместо BEGIN/COMMIT
            # DuckDB автоматически управляет транзакциями эффективнее
            con.execute(f"""
                INSERT INTO prod.{taxi_type}_tripdata
                SELECT * FROM read_parquet('{file}')
            """)

            # ИЗМЕНЕНИЕ 8: Принудительно сбрасываем данные на диск
            con.execute("CHECKPOINT")
            
            # ИЗМЕНЕНИЕ 9: Очищаем кэши и неиспользуемые блоки памяти
            con.execute("PRAGMA force_checkpoint")
            
            # ИЗМЕНЕНИЕ 10: Принудительная очистка памяти Python
            gc.collect()
            
            print(f"  ✓ Loaded {file.name}, memory released")

    # ИЗМЕНЕНИЕ 11: Финальная оптимизация базы данных
    print("\nOptimizing database...")
    con.execute("VACUUM")
    con.execute("ANALYZE")
    
    print("Done.")
    con.close()
    
    # Финальная очистка памяти
    gc.collect()
```

