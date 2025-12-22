"""
DAG: 04_carga_proceso_seleccion
Descripción: Carga Snapshot de Selección y calcula Quality of Hire
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

from tasks.seleccion_tasks import create_seleccion_tasks

default_args = {
    "owner": "rrhh-reclutamiento",
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 1,
}

with DAG(
    "04_carga_proceso_seleccion",
    default_args=default_args,
    description="Carga Snapshot de Selección y calcula Quality of Hire",
    schedule="@daily",
    catchup=False,
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    start = EmptyOperator(task_id="inicio_seleccion")
    end = EmptyOperator(task_id="fin_seleccion")

    # Crear tasks usando el módulo reutilizable
    sel = create_seleccion_tasks(task_prefix="sel")

    # Flujo
    start >> sel["fact_seleccion"] >> end
