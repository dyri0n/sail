from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.schemas.files import FileUploadResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["Files"])


@router.post(
    "/upload/rotacion",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Carga archivo Excel de rotación"
)
async def upload_rotacion_file(
    file: UploadFile = File(...),
    service: FileService = Depends()
):
    """
    - Valida archivo Excel
    - Guarda en landing zone
    - Registra metadata
    - Dispara DAG de Airflow
    """
    return await service.upload_rotacion_file(file)
