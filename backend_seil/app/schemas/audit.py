from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class AuditLogResponse(BaseModel):
    """Schema para un log individual de auditoría"""
    id: str
    timestamp: str
    nivel: str  # INFO, WARN, ERROR, SUCCESS, DEBUG, AUDIT
    modulo: str  # AUTH, ETL, ADMIN, API, DB, etc.
    mensaje: str
    usuario: str
    ip: Optional[str] = None
    detalles: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AuditStatsResponse(BaseModel):
    """Schema para estadísticas de auditoría"""
    total: int
    errores: int
    auditoria: int
    ultimo: str


class AuditFiltersResponse(BaseModel):
    """Schema para valores de filtros disponibles"""
    niveles: List[str]
    modulos: List[str]
    usuarios: List[str]


class AuditLogListResponse(BaseModel):
    """Schema para lista de logs con metadatos"""
    logs: List[AuditLogResponse]
    stats: AuditStatsResponse
    filters: AuditFiltersResponse
    metadata: Dict[str, Any]
