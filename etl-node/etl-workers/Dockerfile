# Imagen base Python 3.11 (compatible con Airflow)
# Nota: Cambiar a 3.13 cuando Airflow lo soporte oficialmente
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar scripts de ETL
COPY ./scripts ./scripts

# Healthcheck básico para testing
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python --version || exit 1

# El comando por defecto - útil para testing
CMD ["python", "--version"]