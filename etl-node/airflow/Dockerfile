# Usamos la imagen específica que solicitaste
FROM apache/airflow:3.1.5-python3.13

USER root
# Instalamos utilidades si son necesarias (opcional)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean

USER airflow

# IMPORTANTE: Instalar el provider de Docker para poder orquestar contenedores externos
RUN pip install --no-cache-dir apache-airflow-providers-docker