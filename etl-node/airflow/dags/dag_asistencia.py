"""
DAG: 03_carga_asistencia_geovictoria
Descripción: Procesa asistencia diaria, calcula atrasos y cruza con turnos
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from tasks.asistencia_tasks import create_asistencia_tasks

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
    end = EmptyOperator(task_id="fin_asistencia")

    # Crear tasks usando el módulo reutilizable
    asis = create_asistencia_tasks(task_prefix="asis")

    # Flujo
    start >> asis["dims_paralelas"] >> asis["fact_asistencia"] >> end
