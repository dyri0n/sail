from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator

DB_CONN_ID = "dwh_postgres_conn"

default_args = {
    "owner": "rrhh-team",
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 1,
}

with DAG(
    "03_carga_asistencia_geovictoria",
    default_args=default_args,
    description="Procesa asistencia diaria, calcula atrasos y cruza con turnos",
    schedule="@daily",
    catchup=False,
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    start = EmptyOperator(task_id="inicio_asistencia")

    # 1. Poblar Dimensiones Específicas de Asistencia (Paralelo)
    t_dim_turno = SQLExecuteQueryOperator(
        task_id="merge_dim_turno", conn_id=DB_CONN_ID, sql="dimensiones/dim_turno.sql"
    )

    t_dim_permiso = SQLExecuteQueryOperator(
        task_id="merge_dim_permiso", conn_id=DB_CONN_ID, sql="dimensiones/dim_permiso.sql"
    )

    # 2. Cargar Hechos (Depende de dimensiones)
    t_fact_asistencia = SQLExecuteQueryOperator(
        task_id="carga_fact_asistencia", conn_id=DB_CONN_ID, sql="fact-tables/fact_asistencia.sql"
    )

    end = EmptyOperator(task_id="fin_asistencia")

    # Definición de dependencias
    start >> [t_dim_turno, t_dim_permiso] >> t_fact_asistencia >> end
