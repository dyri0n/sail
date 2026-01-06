"""
DAG: Carga de Archivos Excel a Tablas de Staging
=================================================
Este DAG procesa archivos Excel de la landing zone y los carga
en las tablas de staging correspondientes.

Fuentes de datos (archivos Excel separados):
    - data_sap.xlsx → stg.stg_rotacion_empleados
    - data_capacitaciones.xlsx → stg.stg_capacitaciones_resumen
    - data_asistencia_capacitaciones.xlsx → stg.stg_capacitaciones_participantes
    - data_gestion_asistencia.xlsx → stg.stg_asistencia_diaria_geovictoria

Flujo:
    1. Verificar formato de los archivos Excel
    2. Truncar tablas de staging
    3. Parsear datos de Excel
    4. Subir a base de datos
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

from tasks.staging_tasks import create_staging_tasks

# =============================================================================
# ARGUMENTOS POR DEFECTO
# =============================================================================
default_args = {
    "owner": "data-team",
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 5,
    "retry_delay": timedelta(minutes=5),
}

# =============================================================================
# DEFINICIÓN DEL DAG
# =============================================================================
with DAG(
    "00_carga_excel_staging",
    default_args=default_args,
    description="Carga archivos Excel de landing zone a tablas de staging",
    schedule=None,
    catchup=False,
    tags=["staging", "excel", "etl"],
    doc_md=__doc__,
) as dag:
    inicio = EmptyOperator(task_id="inicio_carga_staging")
    fin = EmptyOperator(task_id="fin_carga_staging")

    # Crear tasks usando el módulo reutilizable
    stg = create_staging_tasks(task_prefix="stg")

    # Invocar las tasks
    file_info = stg["verificar"]()
    resultado_sap = stg["cargar_sap"](file_info)
    resultado_cap = stg["cargar_capacitaciones"](file_info)
    resultado_asis_cap = stg["cargar_asistencia_cap"](file_info)
    resultado_asis = stg["cargar_asistencia"](file_info)
    resumen = stg["resumen"]([resultado_sap, resultado_cap, resultado_asis_cap, resultado_asis])

    # Definir flujo
    inicio >> file_info >> stg["truncar"]
    stg["truncar"] >> [resultado_sap, resultado_cap, resultado_asis_cap, resultado_asis]
    [resultado_sap, resultado_cap, resultado_asis_cap, resultado_asis] >> resumen >> fin
