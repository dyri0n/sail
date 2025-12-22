# Imagen base de Airflow - versión estable con Python 3.11
# Nota: Python 3.13 aún no tiene soporte oficial en Airflow
FROM apache/airflow:3.1.5

USER root

# Instalamos utilidades necesarias para desarrollo y testing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# IMPORTANTE: Instalar el provider de Docker para poder orquestar contenedores externos
# También instalamos providers adicionales útiles para testing
RUN pip install --no-cache-dir \
    apache-airflow-providers-docker \
    apache-airflow-providers-common-sql \
    apache-airflow-providers-postgres \
    pandas \
    openpyxl \
    sqlalchemy \
    psycopg2-binary