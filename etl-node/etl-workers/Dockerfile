# Imagen base Python 3.13 (Ligera)
FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del sistema si hacen falta
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copiar requirements y scripts
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./scripts ./scripts

# El comando por defecto deja el contenedor esperando, o se sobreescribe desde Airflow
CMD ["python", "--version"]