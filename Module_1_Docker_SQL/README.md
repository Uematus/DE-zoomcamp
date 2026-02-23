# DE-zoomcamp
Data Engineering Zoomcamp

## Instalation

### on server
mrdir zoomcamp  
cd zoomcamp  

### Create Python + PostgreSQL + PgAdmin for Zoomcamp

nano docker-compose.yml  

```
services:  
  python_app:  
    image: python:3.12-slim  
    container_name: de_python_app  
    restart: unless-stopped  
    working_dir: /workspace  
    volumes:  
      - /home/purogen/zoomcamp/share:/workspace  
    command: sleep infinity  
    networks:  
      - de_net  
  
  db:  
    image: postgres:16  
    container_name: de_postgres_db  
    restart: unless-stopped  
    env_file:  
      - .env  
    ports:  
      - "${NEW_POSTGRES_PORT}:5432"  
    volumes:  
      - de-postgres-data:/var/lib/postgresql/data  
    networks:  
      - de_net  

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: de_pgadmin
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "5050:80"
    volumes:
      - pgadmin-data:/var/lib/pgadmin
    networks:
      - de_net
  
volumes:  
  de-postgres-data:  
  pgadmin-data:  
  
networks:  
  de_net:  
    driver: bridge  
```

#### Create .env
nano .env
```
POSTGRES_DB=de_db
POSTGRES_USER=de_user
POSTGRES_PASSWORD=de_password
NEW_POSTGRES_PORT=5433

PGADMIN_DEFAULT_EMAIL=admin@local.dev
PGADMIN_DEFAULT_PASSWORD=pgadmin_pass
```

#### Start container
docker compose up -d  

#### Connect to cantainer
docker exec -it \<name of container\> bash  

---
### Update
Inside container  
apt update  

Install Git  
apt install git  

Clone Repository  
git clone https://github.com/Uematus/DE-zoomcamp.git  

---

### Connect with VS Code
Install extension **Remote Development**  

Create config file:  
```
Host de_zoomcamp_remote
    HostName \<IP\>
    User \<username on server\>
    IdentityFile "C:\Temp\vm_openssh"
```

Click left buttom in VS Code  
**Connect to Host - Remote-SSH**  
Provide link to config file  

After connecting **F1** Dev Containers - for connecting to any containers on the server.  


### Install modules in container  
pip install pandas  
pip install sqlalchemy  
pip install psycopg2-binary  
pip install tqdm  


### PostgreSQL  
Connect to container  
Connect to Postgre  
psql -U \<de_user\> -d postgres  
  
CREATE DATABASE ny_taxi;  

Exit from postgres and connect to new DB.  
psql -U \<de_user\> -d ny_taxi  
  
List tables  
\dt  

List DB  
\l  


### pgAdmin  
Create SSH tunnel for port 5050  
In browser: http://localhost:5050  

login/pass from .env  

Right-click "Servers" → Register → Server  
Configure:  
  General tab: Name: Local DE Docker  
Connection tab:  
  Host: de_postgres_db (the container name)  
  Port: 5432  
  Username: from .env  
  Password: from .env  
Save  


## Using Dockerfile
### Create requirements.txt
nano requirements.txt  
```
pandas  
sqlalchemy  
psycopg2-binary  
tqdm  
```

### Create Dockerfile  
nano Dockerfile  

```
# 1. Base image — as in docker-compose.yml
FROM python:3.12-slim

# 2. Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# 3. Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Set work directory
WORKDIR /workspace

# 5. Default container mode
CMD ["sleep", "infinity"]
```

Change docker-compose.yml  
```
python_app:
    build: .                 # ← build from Dockerfile
    container_name: de_python_app
```

docker compose down  
docker compose -d --build  


## ETL from file  
#### Connection to DB  
engine = create_engine('postgresql://de_user:de_password@de_postgres_db:5432/ny_taxi')  

#### Create table  
##### View all columns in df  
print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))  

##### Create table in DB  
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')  

##### Read csv  
```
df = pd.read_csv(
    '/workspace/yellow_tripdata_2021-01.csv.gz',
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
)

##### Load data
for df_chunk in df:

    if first:
        # Create table schema (no data)
        df_chunk.head(0).to_sql(
            name="yellow_taxi_data",
            con=engine,
            if_exists="replace"
        )
        first = False
        print("Table created")

    # Insert chunk
    df_chunk.to_sql(
        name="yellow_taxi_data",
        con=engine,
        if_exists="append"
    )

    print("Inserted:", len(df_chunk))
```
  

# Cleanup

When you're done with the workshop, clean up Docker resources to free up disk space.

### Stop All Running Containers

```bash
docker-compose down
```

### Remove Specific Containers

```bash
# List all containers
docker ps -a

# Remove specific container
docker rm <container_id>

# Remove all stopped containers
docker container prune
```

### Remove Docker Images

```bash
# List all images
docker images

# Remove specific image
docker rmi taxi_ingest:v001

# Remove all unused images
docker image prune -a
```

### Remove Docker Volumes

```bash
# List volumes
docker volume ls

# Remove specific volumes
docker volume rm ny_taxi_postgres_data
docker volume rm pgadmin_data

# Remove all unused volumes
docker volume prune
```

### Remove Docker Networks

```bash
# List networks
docker network ls

# Remove specific network
docker network rm pg-network

# Remove all unused networks
docker network prune
```

### Complete Cleanup

Removes ALL Docker resources - use with caution!

```bash
# ⚠️ Warning: This removes ALL Docker resources!
docker system prune -a --volumes
```

### Clean Up Local Files

```bash
# Remove parquet files
rm *.parquet

# Remove Python cache
rm -rf __pycache__ .pytest_cache

# Remove virtual environment (if using venv)
rm -rf .venv
```

### Check size for every container
```
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```