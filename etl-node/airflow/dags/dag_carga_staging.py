"""
DAG: Carga de Archivos Excel a Tablas de Staging
=================================================
Este DAG procesa archivos Excel de la landing zone y los carga
en las tablas de staging correspondientes.

Fuentes de datos (hojas de archivos Excel):
    - data_capacitaciones.xlsx[Informe 202X] → stg.stg_realizacion_capacitaciones
    - data_capacitaciones.xlsx[Participantes] → stg.stg_participacion_capacitaciones
    - data_asistencias.xlsx[Días]             → stg.stg_asistencia_diaria
    - data_rotacion.xlsx[Hoja1]               → stg.stg_rotacion_empleados

Flujo:
    1. Verificar formato de los archivos y hojas Excel
    2. Truncar tablas de staging
    3. Cargar y transformar datos de cada hoja
    4. Subir a base de datos
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

from tasks.staging_tasks_v2 import create_staging_tasks

# =============================================================================
# ARGUMENTOS POR DEFECTO
# =============================================================================
default_args = {
    "owner": "data-team",
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 2,
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

    # Cargar cada hoja Excel a su tabla destino
    resultado_cap_realizacion = stg["cargar_capacitaciones_realizacion"](file_info)
    resultado_cap_participantes = stg["cargar_capacitaciones_participantes"](file_info)
    resultado_asistencia = stg["cargar_asistencia"](file_info)
    resultado_rotacion = stg["cargar_rotacion"](file_info)

    # Consolidar resultados
    resultados = [
        resultado_cap_realizacion,
        resultado_cap_participantes,
        resultado_asistencia,
        resultado_rotacion,
    ]
    resumen = stg["resumen"](resultados)

    # Definir flujo
    inicio >> file_info >> stg["truncar"]
    stg["truncar"] >> resultados
    resultados >> resumen >> fin
