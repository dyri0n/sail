"""
DAG: 05_carga_formacion_desarrollo
Descripción: Carga Facts de Capacitación (Oferta y Demanda)
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

from tasks.capacitacion_tasks import create_capacitacion_tasks

default_args = {
    "owner": "rrhh-formacion",
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 1,
}

with DAG(
    "05_carga_formacion_desarrollo",
    default_args=default_args,
    description="Carga Facts de Capacitación (Oferta y Demanda)",
    schedule="@daily",
    catchup=False,
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    start = EmptyOperator(task_id="inicio_formacion")
    end = EmptyOperator(task_id="fin_formacion")

    # Crear tasks usando el módulo reutilizable
    cap = create_capacitacion_tasks(task_prefix="cap")

    # Flujo
    start >> cap["dims_paralelas"]
    cap["dims_paralelas"] >> cap["fact_realizacion"] >> cap["fact_participacion"] >> end
