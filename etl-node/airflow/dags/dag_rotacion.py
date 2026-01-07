"""
DAG: 02_carga_hechos_movimientos_dotacion
Descripción: Carga Facts de Rotación y Snapshot de Dotación (Smart Load)
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from tasks.rotacion_tasks import create_rotacion_tasks

default_args = {
    "owner": "data-team",
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 1,
}

with DAG(
    "02_carga_hechos_movimientos_dotacion",
    default_args=default_args,
    description="Carga Facts de Rotación y Snapshot de Dotación (Smart Load)",
    schedule="@daily",
    catchup=False,
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    start = EmptyOperator(task_id="inicio_facts")
    end = EmptyOperator(task_id="fin_facts")

    # Crear tasks usando el módulo reutilizable
    rot = create_rotacion_tasks(task_prefix="fact")

    # Flujo
    start >> rot["dim_medida"] >> rot["fact_rotacion"] >> end
