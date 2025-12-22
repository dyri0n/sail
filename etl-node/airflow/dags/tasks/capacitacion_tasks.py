"""
Tasks para carga de Hechos de Capacitación (DAG 05).
"""

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

DWH_CONN_ID = "dwh_postgres_conn"


def create_capacitacion_tasks(task_prefix: str = "cap"):
    """
    Crea y retorna todas las tasks de capacitación.

    Returns:
        dict con: dim_proveedor, dim_lugar, dim_curso, fact_realizacion, fact_participacion
    """
    dim_proveedor = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_dim_proveedor",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_proveedor.sql",
    )

    dim_lugar = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_dim_lugar",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_lugar.sql",
    )

    dim_curso = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_dim_curso",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_curso.sql",
    )

    fact_realizacion = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_fact_realizacion",
        conn_id=DWH_CONN_ID,
        sql="fact-tables/fact_realizacion.sql",
    )

    fact_participacion = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_fact_participacion",
        conn_id=DWH_CONN_ID,
        sql="fact-tables/fact_participacion.sql",
    )

    return {
        "dim_proveedor": dim_proveedor,
        "dim_lugar": dim_lugar,
        "dim_curso": dim_curso,
        "fact_realizacion": fact_realizacion,
        "fact_participacion": fact_participacion,
        "dims_paralelas": [dim_proveedor, dim_lugar, dim_curso],
    }
