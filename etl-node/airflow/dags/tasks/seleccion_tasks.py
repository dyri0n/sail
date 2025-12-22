"""
Tasks para carga de Hechos de Selección (DAG 04).
"""

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

DWH_CONN_ID = "dwh_postgres_conn"


def create_seleccion_tasks(task_prefix: str = "sel"):
    """
    Crea y retorna todas las tasks de selección.

    Returns:
        dict con: fact_seleccion
    """
    fact_seleccion = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_fact_seleccion",
        conn_id=DWH_CONN_ID,
        sql="fact-tables/fact_seleccion.sql",
    )

    return {
        "fact_seleccion": fact_seleccion,
    }
