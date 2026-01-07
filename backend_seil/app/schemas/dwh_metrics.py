from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class MetricPoint(BaseModel):
    """Punto de datos para gráficos"""
    label: str  # Fecha o categoría
    value: float


class AsistenciaMetrics(BaseModel):
    """Métricas de asistencia y puntualidad"""
    tasa_ausentismo_mensual: List[MetricPoint]
    tasa_atrasos_mensual: List[MetricPoint]
    promedio_minutos_atraso: float
    total_ausencias: int
    total_atrasos: int


class RotacionMetrics(BaseModel):
    """Métricas de rotación y headcount"""
    headcount_mensual: List[MetricPoint]
    altas_mensuales: List[MetricPoint]
    bajas_mensuales: List[MetricPoint]
    headcount_actual: int
    total_altas: int
    total_bajas: int
    tasa_rotacion: float  # Porcentaje


class SeleccionMetrics(BaseModel):
    """Métricas de selección y reclutamiento"""
    tiempo_contratacion_promedio: float  # Días
    candidatos_por_vacante: float
    procesos_cerrados: int
    procesos_activos: int
    fuentes_reclutamiento: List[MetricPoint]  # Distribución por fuente
    continuidad_rate: float  # Porcentaje de empleados que continúan después de 3 meses


class CapacitacionMetrics(BaseModel):
    """Métricas de capacitación"""
    horas_capacitacion_mensual: List[MetricPoint]
    participacion_por_categoria: List[MetricPoint]
    total_horas_capacitacion: float
    total_participantes: int
    promedio_satisfaccion: float
    promedio_nps: float


class DashboardMetrics(BaseModel):
    """Conjunto completo de métricas para el dashboard"""
    asistencia: AsistenciaMetrics
    rotacion: RotacionMetrics
    seleccion: SeleccionMetrics
    capacitacion: CapacitacionMetrics
    periodo_inicio: date
    periodo_fin: date
