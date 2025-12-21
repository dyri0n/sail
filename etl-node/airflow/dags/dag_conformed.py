"""
DAG: 01_carga_dimensiones_conformadas
Descripción: Orquesta la carga de todas las dimensiones maestras del DWH.
Estrategia:
    1. Ejecución paralela de dimensiones independientes (Tiempo, Empresa, Cargo, Ceco, Modalidad, Gerencia).
    2. Ejecución dependiente de Dimensión Empleado (SCD Tipo 2) una vez que las referencias base están listas.
"""

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.empty import EmptyOperator

from config.settings import settings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    schedule="@daily",  # Se ejecuta una vez al día (ej: 02:00 AM)
    catchup=False,
    tags=["dwh", "dimensiones", "produccion"],
    # Ruta base donde Airflow buscará los archivos .sql
    template_searchpath=["/opt/airflow/dags/sql"],
) as dag:
    start = EmptyOperator(task_id="inicio_carga")

    # ==============================================================================
    # GRUPO 1: DIMENSIONES INDEPENDIENTES (PARALELAS)
    # ==============================================================================

    # 1. Dimensión Tiempo (Generación Matemática 2010-2028)
    t_dim_tiempo = SQLExecuteQueryOperator(
        task_id="merge_dim_tiempo",
        conn_id=settings.DWH_CONN_ID,
        sql="dimensiones/poblar_dim_tiempo.sql",
        show_return_value_in_logs=True,
    )

    # --- STUB: API FERIADOS (Integración Futura) ---
    # Esta tarea usaría el worker de Python para ir a la API de Boostr,
    # poblar staging y luego actualizar dim_tiempo.
    # Se descomenta cuando tengas el script 'extract_feriados.py' listo en el worker.
    """
    t_api_feriados = DockerOperator(
        task_id='worker_api_feriados',
        image=settings.ETL_WORKER_IMAGE,
        api_version='auto',
        auto_remove=True,
        docker_url=settings.get_worker_docker_url(),
        network_mode=settings.DOCKER_NETWORK_MODE,
        environment=settings.get_worker_environment(),
        command="python /app/scripts/extract_feriados.py",
        mounts=[Mount(source=settings.DATA_MOUNT_SOURCE, target=settings.DATA_MOUNT_TARGET, type='bind')],
        mem_limit=settings.WORKER_MEM_LIMIT,
        cpus=settings.WORKER_CPUS,
    )

    t_update_feriados_sql = SQLExecuteQueryOperator(
        task_id='update_feriados_sql',
        conn_id=settings.DWH_CONN_ID,
        sql='dimensiones/update_feriados.sql'
    )

    # Flujo del Stub: Tiempo -> API -> Update SQL
    t_dim_tiempo >> t_api_feriados >> t_update_feriados_sql
    """

    # 2. Dimensión Empresa (Valores Fijos / Merge)
    t_dim_empresa = SQLExecuteQueryOperator(
        task_id="merge_dim_empresa",
        conn_id=settings.DWH_CONN_ID,
        sql="dimensiones/dim_empresa.sql",
    )

    # 3. Dimensión Cargo (Lookup desde Rotación)
    t_dim_cargo = SQLExecuteQueryOperator(
        task_id="merge_dim_cargo", conn_id=settings.DWH_CONN_ID, sql="dimensiones/dim_cargo.sql"
    )

    # 4. Dimensión Gerencia (Unión Selección + Capacitación)
    t_dim_gerencia = SQLExecuteQueryOperator(
        task_id="merge_dim_gerencia",
        conn_id=settings.DWH_CONN_ID,
        sql="dimensiones/dim_gerencia.sql",  # PENDIENTE: Crear este archivo
    )

    # 5. Dimensión Centro Costo
    t_dim_ceco = SQLExecuteQueryOperator(
        task_id="merge_dim_ceco",
        conn_id=settings.DWH_CONN_ID,
        sql="dimensiones/dim_centro_costo.sql",
    )

    # 6. Dimensión Modalidad (Lógica FTE)
    t_dim_modalidad = SQLExecuteQueryOperator(
        task_id="merge_dim_modalidad",
        conn_id=settings.DWH_CONN_ID,
        sql="dimensiones/dim_modalidad_contrato.sql",
    )

    # ==============================================================================
    # GRUPO 2: DIMENSIONES DEPENDIENTES / COMPLEJAS
    # ==============================================================================

    # 7. Dimensión Empleado (SCD Tipo 2 - Híbrido)
    t_dim_empleado = SQLExecuteQueryOperator(
        task_id="merge_dim_empleado_scd2",
        conn_id=settings.DWH_CONN_ID,
        sql="dimensiones/merge_dim_empleado.sql",
    )

    fin = EmptyOperator(task_id="fin_carga_dims")

    # ==============================================================================
    # FLUJO DE DEPENDENCIAS
    # ==============================================================================

    # Paso 1: Inicio -> Grupo 1 (Paralelo)
    start >> [
        t_dim_tiempo,
        t_dim_empresa,
        t_dim_cargo,
        t_dim_gerencia,
        t_dim_ceco,
        t_dim_modalidad,
    ]

    # Paso 2: Grupo 1 -> Dimensión Empleado (Convergen)
    [
        t_dim_tiempo,
        t_dim_empresa,
        t_dim_cargo,
        t_dim_gerencia,
        t_dim_ceco,
        t_dim_modalidad,
    ] >> t_dim_empleado

    # Paso 3: Fin
    t_dim_empleado >> fin
