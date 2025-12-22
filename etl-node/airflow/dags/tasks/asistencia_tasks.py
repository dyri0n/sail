"""
Tasks para carga de Hechos de Asistencia (DAG 03).
"""

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

DWH_CONN_ID = "dwh_postgres_conn"


def create_asistencia_tasks(task_prefix: str = "asis"):
    """
    Crea y retorna todas las tasks de asistencia.

    Returns:
        dict con: dim_turno, dim_permiso, fact_asistencia
    """
    dim_turno = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_dim_turno",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_turno.sql",
    )

    dim_permiso = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_dim_permiso",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_permiso.sql",
    )

    fact_asistencia = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_fact_asistencia",
        conn_id=DWH_CONN_ID,
        sql="fact-tables/fact_asistencia.sql",
    )

    return {
        "dim_turno": dim_turno,
        "dim_permiso": dim_permiso,
        "fact_asistencia": fact_asistencia,
        "dims_paralelas": [dim_turno, dim_permiso],
    }
