from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta
from app.db.dwh_session import get_dwh_db
from app.services.dwh_metrics_service import DWHMetricsService
from app.schemas.dwh_metrics import (
    AsistenciaMetrics,
    RotacionMetrics,
    SeleccionMetrics,
    CapacitacionMetrics,
    DashboardMetrics
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/metrics", tags=["metrics"])


def get_default_date_range():
    """Retorna un rango de fechas por defecto (últimos 6 meses)"""
    end_date = date.today()
    start_date = end_date - timedelta(days=180)
    return start_date, end_date


@router.get("/asistencia", response_model=AsistenciaMetrics)
async def get_asistencia_metrics(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_dwh_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener métricas de asistencia y puntualidad.
    
    - **start_date**: Fecha de inicio (opcional, default: 6 meses atrás)
    - **end_date**: Fecha de fin (opcional, default: hoy)
    """
    if not start_date or not end_date:
        start_date, end_date = get_default_date_range()
    
    try:
        service = DWHMetricsService(db)
        return service.get_asistencia_metrics(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas de asistencia: {str(e)}")


@router.get("/rotacion", response_model=RotacionMetrics)
async def get_rotacion_metrics(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_dwh_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener métricas de rotación y headcount.
    
    - **start_date**: Fecha de inicio (opcional, default: 6 meses atrás)
    - **end_date**: Fecha de fin (opcional, default: hoy)
    """
    if not start_date or not end_date:
        start_date, end_date = get_default_date_range()
    
    try:
        service = DWHMetricsService(db)
        return service.get_rotacion_metrics(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas de rotación: {str(e)}")


@router.get("/seleccion", response_model=SeleccionMetrics)
async def get_seleccion_metrics(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_dwh_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener métricas de selección y reclutamiento.
    
    - **start_date**: Fecha de inicio (opcional, default: 6 meses atrás)
    - **end_date**: Fecha de fin (opcional, default: hoy)
    """
    if not start_date or not end_date:
        start_date, end_date = get_default_date_range()
    
    try:
        service = DWHMetricsService(db)
        return service.get_seleccion_metrics(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas de selección: {str(e)}")


@router.get("/capacitacion", response_model=CapacitacionMetrics)
async def get_capacitacion_metrics(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_dwh_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener métricas de capacitación.
    
    - **start_date**: Fecha de inicio (opcional, default: 6 meses atrás)
    - **end_date**: Fecha de fin (opcional, default: hoy)
    """
    if not start_date or not end_date:
        start_date, end_date = get_default_date_range()
    
    try:
        service = DWHMetricsService(db)
        return service.get_capacitacion_metrics(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas de capacitación: {str(e)}")


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_dwh_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener todas las métricas del dashboard en una sola llamada.
    
    - **start_date**: Fecha de inicio (opcional, default: 6 meses atrás)
    - **end_date**: Fecha de fin (opcional, default: hoy)
    """
    if not start_date or not end_date:
        start_date, end_date = get_default_date_range()
    
    try:
        print(f"[METRICS DEBUG] Fetching metrics for period: {start_date} to {end_date}")
        print(f"[METRICS DEBUG] User: {current_user.get('sub', 'unknown')}")
        
        service = DWHMetricsService(db)
        
        # Test database connection
        try:
            db.execute(text("SELECT 1"))
            print("[METRICS DEBUG] Database connection successful")
        except Exception as db_error:
            print(f"[METRICS DEBUG] Database connection failed: {str(db_error)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error de conexión al DWH: {str(db_error)}"
            )
        
        metrics = service.get_all_metrics(start_date, end_date)
        print("[METRICS DEBUG] Metrics fetched successfully")
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[METRICS DEBUG] Error fetching dashboard metrics:")
        print(error_details)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener métricas del dashboard: {str(e)}"
        )
