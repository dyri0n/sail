from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class FileUploadResponse(BaseModel):
    """
    - Valida archivo Excel
    - Guarda en landing zone
    - Registra metadata
    - Dispara DAG de Airflow
    """
    file_id: UUID
    file_name: str
    dag_id: str
    airflow_run_id: str
    uploaded_at: datetime
