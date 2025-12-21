"""
Configuración Centralizada para DAGs de Airflow
================================================
Este módulo provee acceso a todas las configuraciones de conexión
y parámetros del sistema de manera centralizada.

Uso:
    from config.settings import Settings
    settings = Settings()

    # Obtener Connection ID para SQLOperators
    conn_id = settings.DWH_CONN_ID

    # Obtener URI para scripts Python (DockerOperator)
    uri = settings.get_dwh_uri()

Arquitectura:
    - DWH y Staging están en la misma base de datos (rrhh_prod)
    - Schema 'dwh' contiene las tablas dimensionales y de hechos
    - Schema 'stg' contiene las tablas de staging (temporales)
    - Una sola conexión (dwh_postgres_conn) accede a ambos schemas
"""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Configuración centralizada del sistema ETL.

    Las variables se cargan desde variables de entorno con valores por defecto
    para desarrollo/testing local.
    """

    # =========================================================================
    # CONNECTION IDs (Para SQLExecuteQueryOperator - referencia a Airflow Connections)
    # =========================================================================
    # Una sola conexión para DWH + Staging (misma BD, diferentes schemas)
    DWH_CONN_ID: str = os.getenv("AIRFLOW_DWH_CONN_ID", "dwh_postgres_conn")

    # =========================================================================
    # URIs DE CONEXIÓN (Para scripts Python en DockerOperator)
    # =========================================================================
    # Data Warehouse (contiene schemas: dwh, stg)
    DWH_HOST: str = os.getenv("DWH_HOST", "dwh_rrhh_container")
    DWH_PORT: str = os.getenv("DWH_PORT", "5432")
    DWH_USER: str = os.getenv("DWH_USER", "dwh_admin")
    DWH_PASSWORD: str = os.getenv("DWH_PASSWORD", "sail-rrhh-p4")
    DWH_DATABASE: str = os.getenv("DWH_DATABASE", "rrhh_prod")

    # =========================================================================
    # CONFIGURACIÓN DE WORKERS (Para DockerOperator)
    # =========================================================================
    ETL_WORKER_IMAGE: str = os.getenv("ETL_WORKER_IMAGE", "mi-sistema/etl-worker:latest")

    # URL del Docker daemon del nodo worker
    # - Local: unix://var/run/docker.sock
    # - Remoto: tcp://192.168.1.100:2375
    DOCKER_WORKER_URL: str = os.getenv("DOCKER_WORKER_URL", "unix://var/run/docker.sock")

    # Network mode para contenedores worker
    DOCKER_NETWORK_MODE: str = os.getenv("DOCKER_NETWORK_MODE", "sail-network")

    # Límites de recursos para workers
    WORKER_MEM_LIMIT: str = os.getenv("WORKER_MEM_LIMIT", "4g")
    WORKER_CPUS: float = float(os.getenv("WORKER_CPUS", "2.0"))

    # =========================================================================
    # RUTAS DE DATOS
    # =========================================================================
    # Ruta donde se montan los datos en el worker
    DATA_MOUNT_SOURCE: str = os.getenv("DATA_MOUNT_SOURCE", "/data/etl")
    DATA_MOUNT_TARGET: str = os.getenv("DATA_MOUNT_TARGET", "/app/data")

    # =========================================================================
    # MÉTODOS DE UTILIDAD
    # =========================================================================

    def get_dwh_uri(self) -> str:
        """Construye la URI de conexión al Data Warehouse (incluye staging)."""
        return (
            f"postgresql+psycopg2://{self.DWH_USER}:{self.DWH_PASSWORD}"
            f"@{self.DWH_HOST}:{self.DWH_PORT}/{self.DWH_DATABASE}"
        )

    def get_worker_docker_url(self) -> str:
        """Retorna la URL del Docker daemon para el worker."""
        return self.DOCKER_WORKER_URL

    def get_worker_environment(self, extra_env: dict | None = None) -> dict:
        """
        Genera el diccionario de variables de entorno para pasar al DockerOperator.

        Args:
            extra_env: Variables adicionales a incluir

        Returns:
            dict con las variables de entorno para el contenedor worker
        """
        env = {
            "DWH_URI": self.get_dwh_uri(),
            "DWH_HOST": self.DWH_HOST,
            "DWH_PORT": self.DWH_PORT,
            "DWH_DATABASE": self.DWH_DATABASE,
        }
        if extra_env:
            env.update(extra_env)
        return env


# Instancia global para importar directamente
settings = Settings()
