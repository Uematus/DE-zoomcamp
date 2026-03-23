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

# CMD ["bruin", "--help"]
