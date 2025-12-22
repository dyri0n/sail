"""
DAG: 01_carga_dimensiones_conformadas
Descripción: Orquesta la carga de todas las dimensiones maestras del DWH.
Estrategia:
    1. Ejecución paralela de dimensiones independientes (Tiempo, Empresa, Cargo, Ceco, Modalidad, Gerencia).
    2. Ejecución dependiente de Dimensión Empleado (SCD Tipo 2) una vez que las referencias base están listas.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

from tasks.dimension_tasks import create_dimension_tasks

default_args = {
    "owner": "data-team",
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 1,
    "email_on_failure": False,
}

with DAG(
    "01_carga_dimensiones_conformadas",
    default_args=default_args,
    description="Carga Full/Merge de dimensiones conformadas",
    schedule="@daily",
    catchup=False,
    tags=["dwh", "dimensiones", "produccion"],
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    start = EmptyOperator(task_id="inicio_carga")
    fin = EmptyOperator(task_id="fin_carga_dims")

    # Crear tasks usando el módulo reutilizable
    dim = create_dimension_tasks(task_prefix="merge")

    # Flujo de dependencias
    start >> dim["grupo_independientes"]
    dim["grupo_independientes"] >> dim["dim_empleado"] >> fin
