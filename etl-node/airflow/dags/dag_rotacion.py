from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

DB_CONN_ID = "dwh_postgres_conn"

default_args = {
    "owner": "data-team",
    "start_date": days_ago(1),
    "retries": 1,
}

with DAG(
    "02_carga_hechos_movimientos_dotacion",
    default_args=default_args,
    description="Carga Facts de Rotación y Snapshot de Dotación",
    schedule_interval="@daily",
    catchup=False,
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    start = EmptyOperator(task_id="inicio_facts")

    # 1. Cargar Dimensión Medida (Pequeña, requisito para Fact)
    t_dim_medida = SQLExecuteQueryOperator(
        task_id="dim_medida", conn_id=DB_CONN_ID, sql="hechos/poblar_dim_medida.sql"
    )

    # 2. Cargar Fact Rotación (Historia de Intervalos)
    t_fact_rotacion = SQLExecuteQueryOperator(
        task_id="fact_rotacion_transaccional",
        conn_id=DB_CONN_ID,
        sql="hechos/carga_fact_rotacion.sql",
    )

    # 3. Generar Snapshot Mensual (Stock)
    t_fact_snapshot = SQLExecuteQueryOperator(
        task_id="fact_dotacion_snapshot",
        conn_id=DB_CONN_ID,
        sql="hechos/carga_fact_dotacion_snapshot.sql",
    )

    end = EmptyOperator(task_id="fin_facts")

    # Flujo
    # Primero aseguramos la dim medida
    start >> t_dim_medida

    # Luego cargamos la historia de movimientos
    t_dim_medida >> t_fact_rotacion

    # Finalmente, basándonos en la historia, generamos la foto mensual
    t_fact_rotacion >> t_fact_snapshot >> end
