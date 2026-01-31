# DE-zoomcamp
Data Engineering Zoomcamp

## Instalation Kestra

### Create Python + PostgreSQL + PgAdmin + Kestra for Zoomcamp

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

  kestra_postgres:
    image: postgres:16
    container_name: de_kestra_postgres
    restart: unless-stopped
    volumes:
      - kestra-postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${KESTRA_DB_NAME}
      POSTGRES_USER: ${KESTRA_DB_USER}
      POSTGRES_PASSWORD: ${KESTRA_DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 10

    networks:
      - de_net

  kestra:
    image: kestra/kestra:v1.1
    container_name: de_kestra
    restart: unless-stopped
    pull_policy: always
    user: "root"
    command: server standalone
    volumes:
      - kestra-data:/app/storage
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/kestra-wd:/tmp/kestra-wd
    env_file:
      - .env
    environment:
      KESTRA_CONFIGURATION: |
        datasources:
          postgres:
            url: jdbc:postgresql://kestra_postgres:5432/${KESTRA_DB_NAME}
            driverClassName: org.postgresql.Driver
            username: ${KESTRA_DB_USER}
            password: ${KESTRA_DB_PASSWORD}
        kestra:
          server:
            basicAuth:
              username: "$${KESTRA_ADMIN_USER}"
              password: "$${KESTRA_ADMIN_PASSWORD}"
          repository:
            type: postgres
          storage:
            type: local
            local:
              basePath: "/app/storage"
          queue:
            type: postgres
          tasks:
            tmpDir:
              path: /tmp/kestra-wd/tmp
          url: http://localhost:8080/
    ports:
      - "8080:8080"  # UI
      - "8081:8081"  # Executor API
    depends_on:
      kestra_postgres:
        condition: service_healthy
    networks:
      - de_net
  
volumes:  
  de-postgres-data:  
  pgadmin-data: 
  kestra-postgres-data:
  kestra-data: 
  
networks:  
  de_net:  
    driver: bridge  
```

#### Append .env
nano .env
```
POSTGRES_DB=de_db
POSTGRES_USER=de_user
POSTGRES_PASSWORD=de_password
NEW_POSTGRES_PORT=5433

PGADMIN_DEFAULT_EMAIL=admin@local.dev
PGADMIN_DEFAULT_PASSWORD=pgadmin_pass

# PostgreSQL для Kestra
KESTRA_DB_NAME=kestra
KESTRA_DB_USER=kestra_pg
KESTRA_DB_PASSWORD=kestra_pg_pass

# Аутентификация Kestra UI
KESTRA_ADMIN_USER=admin@kestra.io
KESTRA_ADMIN_PASSWORD=Admin1234
```

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


