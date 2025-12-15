from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago

default_args = {
    "owner": "data-team",
    "start_date": days_ago(1),
    "retries": 1,
}

# String de conexión para que Python Worker escriba en Staging
# OJO: En producción usa Airflow Variables o Secrets Backend
STAGING_DB_URI = "postgresql+psycopg2://airflow:airflow@postgres/airflow"

with DAG(
    "02_actualizar_feriados",
    default_args=default_args,
    schedule_interval="@yearly",  # Correr 1 vez al año o a demanda
    catchup=False,
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    # Paso 1: Python Worker descarga API -> Staging
    extraer_api = DockerOperator(
        task_id="extract_feriados_api",
        image="mi-sistema/etl-worker:latest",
        api_version="auto",
        auto_remove=True,
        network_mode="host",  # O la red donde esté la DB
        # Pasamos la URI como argumento al script
        command=f"python /app/scripts/extract_feriados.py '{STAGING_DB_URI}'",
    )

    # Paso 2: SQL actualiza dim_tiempo
    actualizar_dim = SQLExecuteQueryOperator(
        task_id="update_dim_tiempo_feriados",
        conn_id="dwh_postgres_conn",  # Tu conexión definida en Airflow
        sql="dimensiones/update_feriados.sql",
    )

    extraer_api >> actualizar_dim
