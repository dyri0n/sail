from config.settings import settings
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

# Configuración centralizada
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Definición de argumentos por defecto
default_args = {
    'owner': 'data-team',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    'etl_pesado_python',
    default_args=default_args,
    schedule='@daily',
    catchup=False,
    tags=["etl", "worker", "python"],
) as dag:

    # Esta tarea levanta el contenedor ETL definido en la otra carpeta
    ejecutar_script_etl = DockerOperator(
        task_id='correr_script_pesado',
        # Imagen configurada centralizadamente
        image=settings.ETL_WORKER_IMAGE,
        # Nombre único por ejecución
        container_name='etl_worker_run_{{ ts_nodash }}',
        api_version='auto',
        # Borra el contenedor al terminar exitosamente (Airflow 3.x)
        auto_remove='success',

        # El comando que ejecutará DENTRO del contenedor
        command="python /app/scripts/proceso_pesado.py",

        # --- CONFIGURACIÓN DE RED Y CARGA (desde settings) ---
        docker_url=settings.get_worker_docker_url(),
        network_mode=settings.DOCKER_NETWORK_MODE,

        # Variables de entorno para el script (URIs de conexión)
        environment=settings.get_worker_environment(),

        # Montar volúmenes si necesitas compartir archivos (logs, csvs)
        mounts=[
            Mount(
                source=settings.DATA_MOUNT_SOURCE,
                target=settings.DATA_MOUNT_TARGET,
                type='bind'
            ),
        ],

        # Límites para asegurar que no mate al host
        mem_limit=settings.WORKER_MEM_LIMIT,
        cpus=settings.WORKER_CPUS,
    )

    ejecutar_script_etl
