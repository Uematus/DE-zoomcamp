# DE-zoomcamp
Data Engineering Zoomcamp

# Instalation

### on server
mrdir zoomcamp  
cd zoomcamp

### Create Python + PostgreSQL for Zoomcamp

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
  
volumes:  
  de-postgres-data:  
  
networks:  
  de_net:  
    driver: bridge  
```

#### Start container
docker compose up -d

#### Connect to cantainer
docker exec -it \<name of container\> bash

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
