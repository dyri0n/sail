"""
DAG MAESTRO - Poblado Completo del Data Warehouse
==================================================
Importa y concatena todas las tasks de los DAGs individuales
para ejecutar el pipeline ETL completo en un solo DAG.

Orden de ejecución:
  00 → Carga Staging (Excel → stg)
  01 → Dimensiones Conformadas (stg → dwh.dim_*)
  02 → Hechos: Rotación y Dotación
  03 → Hechos: Asistencia
  04 → Hechos: Selección
  05 → Hechos: Capacitación

Duración estimada: ~10-15 minutos
"""

from datetime import datetime, timedelta

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import DAG
from tasks.asistencia_tasks import create_asistencia_tasks
from tasks.capacitacion_tasks import create_capacitacion_tasks
from tasks.dimension_tasks import create_dimension_tasks
from tasks.rotacion_tasks import create_rotacion_tasks
from tasks.seleccion_tasks import create_seleccion_tasks
from tasks.staging_tasks import create_staging_tasks

from config.settings import settings

# =============================================================================
# CONFIGURACIÓN DEL DAG
# =============================================================================
default_args = {
    "owner": "data-team",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="99_maestro_poblado_completo_dwh",
    default_args=default_args,
    description="DAG Maestro: Pipeline ETL completo concatenando todas las tasks",
    schedule=None,  # Solo ejecución manual
    catchup=False,
    tags=["maestro", "pipeline-completo", "dwh"],
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    # =========================================================================
    # MARCADORES DE SECCIÓN
    # =========================================================================
    inicio = EmptyOperator(task_id="inicio_pipeline")
    fin_staging = EmptyOperator(task_id="fin_00_staging")
    fin_dimensiones = EmptyOperator(task_id="fin_01_dimensiones")
    fin_rotacion = EmptyOperator(task_id="fin_02_rotacion")
    fin_asistencia = EmptyOperator(task_id="fin_03_asistencia")
    fin_seleccion = EmptyOperator(task_id="fin_04_seleccion")
    fin = EmptyOperator(task_id="fin_pipeline")

    # =========================================================================
    # CONTROL DE FOREIGN KEYS (TRIGGERS)
    # =========================================================================
    # Desactiva TODOS los triggers (incluye FK) en las tablas de hechos
    # Esto es necesario porque cada task puede usar una conexión diferente
    desactivar_fk = SQLExecuteQueryOperator(
        task_id="desactivar_foreign_keys",
        conn_id=settings.DWH_CONN_ID,
        sql="""
            ALTER TABLE dwh.fact_rotacion DISABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_dotacion_snapshot DISABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_asistencia DISABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_seleccion DISABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_realizacion_capacitacion DISABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_participacion_capacitacion DISABLE TRIGGER ALL;
        """,
    )

    # Reactiva los triggers al finalizar
    reactivar_fk = SQLExecuteQueryOperator(
        task_id="reactivar_foreign_keys",
        conn_id=settings.DWH_CONN_ID,
        sql="""
            ALTER TABLE dwh.fact_rotacion ENABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_dotacion_snapshot ENABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_asistencia ENABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_seleccion ENABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_realizacion_capacitacion ENABLE TRIGGER ALL;
            ALTER TABLE dwh.fact_participacion_capacitacion ENABLE TRIGGER ALL;
        """,
    )

    # =========================================================================
    # 00 - STAGING: Carga Excel → STG
    # =========================================================================
    stg = create_staging_tasks(task_prefix="00")

    # Invocar las tasks (las @task decoradas requieren ser llamadas)
    stg_verificar = stg["verificar"]()
    stg_cargar_sap = stg["cargar_sap"](stg_verificar)
    stg_cargar_cap = stg["cargar_capacitaciones"](stg_verificar)
    stg_cargar_asis_cap = stg["cargar_asistencia_cap"](stg_verificar)
    stg_cargar_asis = stg["cargar_asistencia"](stg_verificar)
    stg_resumen = stg["resumen"](
        [stg_cargar_sap, stg_cargar_cap, stg_cargar_asis_cap, stg_cargar_asis]
    )

    # Dependencias staging
    inicio >> desactivar_fk >> stg_verificar >> stg["truncar"]
    stg["truncar"] >> [stg_cargar_sap, stg_cargar_cap, stg_cargar_asis_cap, stg_cargar_asis]
    (
        [stg_cargar_sap, stg_cargar_cap, stg_cargar_asis_cap, stg_cargar_asis]
        >> stg_resumen
        >> fin_staging
    )

    # =========================================================================
    # 01 - DIMENSIONES CONFORMADAS
    # =========================================================================
    dim = create_dimension_tasks(task_prefix="01")

    # Dependencias dimensiones
    fin_staging >> dim["grupo_independientes"]
    dim["grupo_independientes"] >> dim["dim_empleado"] >> fin_dimensiones

    # =========================================================================
    # 02 - HECHOS ROTACIÓN Y DOTACIÓN
    # =========================================================================
    rot = create_rotacion_tasks(task_prefix="02")

    fin_dimensiones >> rot["dim_medida"] >> rot["fact_rotacion"] >> fin_rotacion

    # =========================================================================
    # 03 - HECHOS ASISTENCIA
    # =========================================================================
    asis = create_asistencia_tasks(task_prefix="03")

    fin_rotacion >> asis["dims_paralelas"]
    asis["dims_paralelas"] >> asis["fact_asistencia"] >> fin_asistencia

    # =========================================================================
    # 04 - HECHOS SELECCIÓN
    # =========================================================================
    sel = create_seleccion_tasks(task_prefix="04")

    fin_asistencia >> sel["fact_seleccion"] >> fin_seleccion

    # =========================================================================
    # 05 - HECHOS CAPACITACIÓN
    # =========================================================================
    cap = create_capacitacion_tasks(task_prefix="05")

    fin_seleccion >> cap["dims_paralelas"]
    (
        cap["dims_paralelas"]
        >> cap["fact_realizacion"]
        >> cap["fact_participacion"]
        >> reactivar_fk
        >> fin
    )
