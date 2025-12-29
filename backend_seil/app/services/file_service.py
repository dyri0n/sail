from fastapi import UploadFile, HTTPException, status
from uuid import uuid4
from datetime import datetime
from pathlib import Path

from app.repositories.file_repository import FileRepository
from app.services.airflow_service import AirflowService
from app.utils.excel_validator import validate_rotacion_excel
from app.core.config import settings


class FileService:

    def __init__(
        self,
        file_repo: FileRepository = FileRepository(),
        airflow: AirflowService = AirflowService()
    ):
        self.file_repo = file_repo
        self.airflow = airflow

    async def upload_rotacion_file(self, file: UploadFile):

        if not file.filename.endswith(".xlsx"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten archivos .xlsx"
            )

        # 1️⃣ Validar estructura Excel
        await validate_rotacion_excel(file)

        # 2️⃣ Guardar archivo en landing zone
        file_id = uuid4()
        landing_path = Path(settings.INPUT_DATA_PATH) / "rotacion"
        landing_path.mkdir(parents=True, exist_ok=True)

        final_path = landing_path / f"{file_id}_{file.filename}"

        with open(final_path, "wb") as f:
            f.write(await file.read())

        # 3️⃣ Registrar metadata
        self.file_repo.create(
            file_id=file_id,
            file_name=file.filename,
            source_type="rotacion",
            path=str(final_path)
        )

        # 4️⃣ Disparar DAG
        dag_id = "02_carga_hechos_movimientos_dotacion"
        dag_run = self.airflow.trigger_dag(
            dag_id=dag_id,
            conf={
                "file_id": str(file_id),
                "file_path": str(final_path),
                "source": "rotacion"
            }
        )

        return {
            "file_id": file_id,
            "file_name": file.filename,
            "dag_id": dag_id,
            "airflow_run_id": dag_run["dag_run_id"],
            "uploaded_at": datetime.utcnow()
        }
