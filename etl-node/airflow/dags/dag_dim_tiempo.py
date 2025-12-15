from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.utils.dates import days_ago

# Definir argumentos por defecto
default_args = {
    "owner": "data-team",
    "start_date": days_ago(1),
    "retries": 1,
}

# ID de la conexión configurada en Airflow (Admin -> Connections)
# Debe apuntar a tu DWH (Nodo 1)
DB_CONN_ID = "dwh_postgres_conn"

with DAG(
    "00_carga_dim_tiempo",  # El 00 sugiere que debe correr antes que todo
    default_args=default_args,
    description="Regenera la dimensión tiempo desde 2010 hasta Current+3 años",
    schedule_interval="@yearly",  # Correr una vez al año para agregar días nuevos
    catchup=False,
    template_searchpath=["/opt/airflow/dags/sql"],  # Ruta donde Airflow busca los .sql
) as dag:
    # Tarea única: Ejecutar el script SQL
    poblar_tiempo = SQLExecuteQueryOperator(
        task_id="ejecutar_sql_dim_tiempo",
        conn_id=DB_CONN_ID,
        sql="dimensiones/poblar_dim_tiempo.sql",
        show_return_value_in_logs=True,
    )

    poblar_tiempo
