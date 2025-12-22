"""
Módulo de tasks reutilizables para el pipeline ETL del DWH.
Cada función retorna operadores que pueden ser usados en cualquier DAG.
"""

from tasks.staging_tasks import create_staging_tasks
from tasks.dimension_tasks import create_dimension_tasks
from tasks.rotacion_tasks import create_rotacion_tasks
from tasks.asistencia_tasks import create_asistencia_tasks
from tasks.seleccion_tasks import create_seleccion_tasks
from tasks.capacitacion_tasks import create_capacitacion_tasks

__all__ = [
    "create_staging_tasks",
    "create_dimension_tasks",
    "create_rotacion_tasks",
    "create_asistencia_tasks",
    "create_seleccion_tasks",
    "create_capacitacion_tasks",
]
