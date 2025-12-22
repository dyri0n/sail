"""
Tasks para carga de Hechos de Rotación y Dotación (DAG 02).
"""

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

DWH_CONN_ID = "dwh_postgres_conn"


def create_rotacion_tasks(task_prefix: str = "rot"):
    """
    Crea y retorna todas las tasks de rotación/dotación.

    Returns:
        dict con: dim_medida, fact_rotacion
    """
    dim_medida = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_dim_medida",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_medida_aplicada.sql",
    )

    fact_rotacion = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_fact_rotacion",
        conn_id=DWH_CONN_ID,
        sql="fact-tables/fact_rotacion.sql",
    )

    return {
        "dim_medida": dim_medida,
        "fact_rotacion": fact_rotacion,
    }
