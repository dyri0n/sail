from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago
from docker.types import Mount

# Definición de argumentos por defecto
default_args = {
    'owner': 'data-team',
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'etl_pesado_python_3_13',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Esta tarea levanta el contenedor ETL definido en la otra carpeta
    ejecutar_script_etl = DockerOperator(
        task_id='correr_script_pesado',
        # Nombre de la imagen que construiste en la carpeta /etl-worker
        image='mi-sistema/etl-worker:latest-py3.13',
        container_name='etl_worker_run_unique',
        api_version='auto',
        auto_remove=True, # Borra el contenedor al terminar para ahorrar espacio
        
        # El comando que ejecutará DENTRO del contenedor de Python 3.13
        command="python /app/scripts/proceso_pesado.py",
        
        # --- CONFIGURACIÓN DE RED Y CARGA ---
        
        # CASO 1: Si están en la misma máquina, usa el network de docker por defecto
        # network_mode='bridge',
        # docker_url='unix://var/run/docker.sock',
        
        # CASO 2: Si el ETL está en OTRA máquina (Red distinta)
        # Debes habilitar el puerto 2375 en el docker daemon de la máquina remota
        docker_url='tcp://192.168.X.Y:2375',
        network_mode='bridge',
        
        # Montar volúmenes si necesitas compartir archivos (logs, csvs)
        mounts=[
            Mount(source='/ruta/local/data', target='/app/data', type='bind'),
        ],
        
        # Límites para asegurar que no mate al host
        mem_limit='4g',
        cpus=2.0
    )

    ejecutar_script_etl