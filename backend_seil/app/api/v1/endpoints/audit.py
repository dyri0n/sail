from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.audit_service import AuditService
from app.schemas.audit import AuditLogListResponse, AuditStatsResponse, AuditFiltersResponse
from app.core.permissions import require_role

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get(
    "/logs",
    response_model=AuditLogListResponse,
    dependencies=[Depends(require_role("ADMIN"))],
    summary="Obtener logs de auditoría"
)
def get_audit_logs(
    nivel: Optional[str] = Query(None, description="Filtrar por nivel: INFO, WARN, ERROR, etc."),
    modulo: Optional[str] = Query(None, description="Filtrar por módulo: AUTH, ETL, ADMIN, etc."),
    usuario: Optional[str] = Query(None, description="Filtrar por username"),
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio (ISO format)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin (ISO format)"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de logs"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    Obtiene logs de auditoría con filtros opcionales.
    
    Requiere rol ADMIN.
    """
    service = AuditService()
    
    logs = service.get_logs(
        nivel=nivel,
        modulo=modulo,
        usuario=usuario,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=limit,
        offset=offset
    )
    
    stats = service.get_stats()
    filters = service.get_filter_values()
    
    from app.utils.datetime_utils import now_chile
    
    return {
        "logs": logs,
        "stats": stats,
        "filters": filters,
        "metadata": {
            "title": "Logs y Auditoría",
            "description": "Sistema de logs y auditoría",
            "lastUpdated": now_chile().isoformat()
        }
    }


@router.get(
    "/stats",
    response_model=AuditStatsResponse,
    dependencies=[Depends(require_role("ADMIN"))],
    summary="Obtener estadísticas de auditoría"
)
def get_audit_stats():
    """
    Obtiene estadísticas de auditoría.
    
    Requiere rol ADMIN.
    """
    service = AuditService()
    return service.get_stats()


@router.get(
    "/filters",
    response_model=AuditFiltersResponse,
    dependencies=[Depends(require_role("ADMIN"))],
    summary="Obtener valores para filtros"
)
def get_audit_filters():
    """
    Obtiene valores únicos disponibles para los filtros.
    
    Requiere rol ADMIN.
    """
    service = AuditService()
    return service.get_filter_values()
