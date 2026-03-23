# 1. Базовый образ
FROM python:3.12-slim

# 2. Устанавливаем системные зависимости (git и зависимости для psycopg2)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# 3. Устанавливаем зависимости Python из requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Устанавливаем рабочую директорию
WORKDIR /workspace

# 5. По умолчанию контейнер будет ждать (как "sleep infinity")
CMD ["sleep", "infinity"]
