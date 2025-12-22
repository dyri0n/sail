"""
Tasks para carga de Dimensiones Conformadas (DAG 01).
"""

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from config.settings import settings


def create_dimension_tasks(task_prefix: str = "dim"):
    """
    Crea y retorna todas las tasks de dimensiones conformadas.

    Returns:
        dict con: dim_tiempo, dim_empresa, dim_cargo, dim_gerencia,
                  dim_ceco, dim_modalidad, dim_empleado
    """
    DWH_CONN_ID = settings.DWH_CONN_ID

    dim_tiempo = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_tiempo",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/poblar_dim_tiempo.sql",
        show_return_value_in_logs=True,
    )

    dim_empresa = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_empresa",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_empresa.sql",
    )

    dim_cargo = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_cargo",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_cargo.sql",
    )

    dim_gerencia = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_gerencia",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_gerencia.sql",
    )

    dim_ceco = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_ceco",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_centro_costo.sql",
    )

    dim_modalidad = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_modalidad",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/dim_modalidad_contrato.sql",
    )

    dim_empleado = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_empleado_scd2",
        conn_id=DWH_CONN_ID,
        sql="dimensiones/merge_dim_empleado.sql",
    )

    return {
        "dim_tiempo": dim_tiempo,
        "dim_empresa": dim_empresa,
        "dim_cargo": dim_cargo,
        "dim_gerencia": dim_gerencia,
        "dim_ceco": dim_ceco,
        "dim_modalidad": dim_modalidad,
        "dim_empleado": dim_empleado,
        # Listas para facilitar dependencias
        "grupo_independientes": [
            dim_tiempo,
            dim_empresa,
            dim_cargo,
            dim_gerencia,
            dim_ceco,
            dim_modalidad,
        ],
    }
