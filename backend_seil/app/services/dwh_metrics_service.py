from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime, timedelta
from typing import List
from app.schemas.dwh_metrics import (
    AsistenciaMetrics,
    RotacionMetrics,
    SeleccionMetrics,
    CapacitacionMetrics,
    DashboardMetrics,
    MetricPoint
)


class DWHMetricsService:
    """Servicio para consultar métricas del Data Warehouse"""

    def __init__(self, db: Session):
        self.db = db

    def get_asistencia_metrics(self, start_date: date, end_date: date) -> AsistenciaMetrics:
        """Obtener métricas de asistencia"""
        
        # Tasa de ausentismo mensual
        query_ausentismo = text("""
            SELECT 
                dt.mes_nombre || ' ' || dt.anio as mes,
                ROUND(
                    COUNT(*) FILTER (WHERE fa.es_ausencia = 1) * 100.0 / 
                    NULLIF(COUNT(*), 0), 2
                ) as tasa
            FROM dwh.fact_asistencia fa
            JOIN dwh.dim_tiempo dt ON fa.fecha_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
            GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre
            ORDER BY dt.anio, dt.mes_numero
        """)
        
        result = self.db.execute(query_ausentismo, {
            'start_date': start_date,
            'end_date': end_date
        })
        tasa_ausentismo = [MetricPoint(label=row[0], value=row[1] or 0) for row in result]

        # Tasa de atrasos mensual
        query_atrasos = text("""
            SELECT 
                dt.mes_nombre || ' ' || dt.anio as mes,
                ROUND(
                    COUNT(*) FILTER (WHERE fa.es_atraso = 1) * 100.0 / 
                    NULLIF(COUNT(*), 0), 2
                ) as tasa
            FROM dwh.fact_asistencia fa
            JOIN dwh.dim_tiempo dt ON fa.fecha_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
            GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre
            ORDER BY dt.anio, dt.mes_numero
        """)
        
        result = self.db.execute(query_atrasos, {
            'start_date': start_date,
            'end_date': end_date
        })
        tasa_atrasos = [MetricPoint(label=row[0], value=row[1] or 0) for row in result]

        # Estadísticas generales
        query_stats = text("""
            SELECT 
                AVG(minutos_atraso) FILTER (WHERE es_atraso = 1) as promedio_atraso,
                COUNT(*) FILTER (WHERE es_ausencia = 1) as total_ausencias,
                COUNT(*) FILTER (WHERE es_atraso = 1) as total_atrasos
            FROM dwh.fact_asistencia fa
            JOIN dwh.dim_tiempo dt ON fa.fecha_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
        """)
        
        result = self.db.execute(query_stats, {
            'start_date': start_date,
            'end_date': end_date
        }).fetchone()

        return AsistenciaMetrics(
            tasa_ausentismo_mensual=tasa_ausentismo,
            tasa_atrasos_mensual=tasa_atrasos,
            promedio_minutos_atraso=round(result[0] or 0, 2),
            total_ausencias=result[1] or 0,
            total_atrasos=result[2] or 0
        )

    def get_rotacion_metrics(self, start_date: date, end_date: date) -> RotacionMetrics:
        """Obtener métricas de rotación"""
        
        # Headcount mensual (snapshot del último día de cada mes)
        query_headcount = text("""
            SELECT 
                dt.mes_nombre || ' ' || dt.anio as mes,
                SUM(fds.headcount) as headcount
            FROM dwh.fact_dotacion_snapshot fds
            JOIN dwh.dim_tiempo dt ON fds.mes_cierre_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
            GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre
            ORDER BY dt.anio, dt.mes_numero
        """)
        
        result = self.db.execute(query_headcount, {
            'start_date': start_date,
            'end_date': end_date
        })
        headcount_data = [MetricPoint(label=row[0], value=row[1] or 0) for row in result]

        # Altas y bajas mensuales
        query_movimientos = text("""
            SELECT 
                dt.mes_nombre || ' ' || dt.anio as mes,
                COUNT(*) FILTER (WHERE fr.variacion_headcount = 1) as altas,
                COUNT(*) FILTER (WHERE fr.variacion_headcount = -1) as bajas
            FROM dwh.fact_rotacion fr
            JOIN dwh.dim_tiempo dt ON fr.fecha_inicio_vigencia_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
            GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre
            ORDER BY dt.anio, dt.mes_numero
        """)
        
        result = self.db.execute(query_movimientos, {
            'start_date': start_date,
            'end_date': end_date
        })
        
        altas_data = []
        bajas_data = []
        for row in result:
            altas_data.append(MetricPoint(label=row[0], value=row[1] or 0))
            bajas_data.append(MetricPoint(label=row[0], value=row[2] or 0))

        # Estadísticas generales
        query_stats = text("""
            SELECT 
                COUNT(*) FILTER (WHERE variacion_headcount = 1) as total_altas,
                COUNT(*) FILTER (WHERE variacion_headcount = -1) as total_bajas
            FROM dwh.fact_rotacion fr
            JOIN dwh.dim_tiempo dt ON fr.fecha_inicio_vigencia_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
        """)
        
        result = self.db.execute(query_stats, {
            'start_date': start_date,
            'end_date': end_date
        }).fetchone()

        total_altas = result[0] or 0
        total_bajas = result[1] or 0
        
        # Headcount actual (último snapshot)
        query_headcount_actual = text("""
            SELECT SUM(headcount)
            FROM dwh.fact_dotacion_snapshot fds
            JOIN dwh.dim_tiempo dt ON fds.mes_cierre_sk = dt.tiempo_sk
            WHERE dt.fecha <= :end_date
            ORDER BY dt.fecha DESC
            LIMIT 1
        """)
        
        headcount_actual = self.db.execute(
            query_headcount_actual, 
            {'end_date': end_date}
        ).scalar() or 0

        # Calcular tasa de rotación
        promedio_headcount = headcount_actual if headcount_actual > 0 else 1
        tasa_rotacion = round((total_bajas / promedio_headcount) * 100, 2) if promedio_headcount > 0 else 0

        return RotacionMetrics(
            headcount_mensual=headcount_data,
            altas_mensuales=altas_data,
            bajas_mensuales=bajas_data,
            headcount_actual=headcount_actual,
            total_altas=total_altas,
            total_bajas=total_bajas,
            tasa_rotacion=tasa_rotacion
        )

    def get_seleccion_metrics(self, start_date: date, end_date: date) -> SeleccionMetrics:
        """Obtener métricas de selección"""
        
        # Fuentes de reclutamiento
        query_fuentes = text("""
            SELECT 
                fuente_reclutamiento,
                COUNT(*) as cantidad
            FROM dwh.fact_seleccion fs
            JOIN dwh.dim_tiempo dt ON fs.fecha_cierre_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
                AND fuente_reclutamiento IS NOT NULL
            GROUP BY fuente_reclutamiento
            ORDER BY cantidad DESC
        """)
        
        result = self.db.execute(query_fuentes, {
            'start_date': start_date,
            'end_date': end_date
        })
        fuentes = [MetricPoint(label=row[0], value=row[1]) for row in result]

        # Estadísticas generales
        query_stats = text("""
            SELECT 
                AVG(duracion_proceso_dias) as promedio_dias,
                AVG(cantidad_candidatos) as promedio_candidatos,
                COUNT(*) FILTER (WHERE estado_final_proceso = 'CERRADO') as procesos_cerrados,
                COUNT(*) FILTER (WHERE estado_final_proceso != 'CERRADO') as procesos_activos,
                AVG(tiene_continuidad) * 100 as tasa_continuidad
            FROM dwh.fact_seleccion fs
            JOIN dwh.dim_tiempo dt ON fs.fecha_cierre_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
        """)
        
        result = self.db.execute(query_stats, {
            'start_date': start_date,
            'end_date': end_date
        }).fetchone()

        return SeleccionMetrics(
            tiempo_contratacion_promedio=round(result[0] or 0, 1),
            candidatos_por_vacante=round(result[1] or 0, 1),
            procesos_cerrados=result[2] or 0,
            procesos_activos=result[3] or 0,
            fuentes_reclutamiento=fuentes,
            continuidad_rate=round(result[4] or 0, 2)
        )

    def get_capacitacion_metrics(self, start_date: date, end_date: date) -> CapacitacionMetrics:
        """Obtener métricas de capacitación"""
        
        # Horas de capacitación por mes
        query_horas = text("""
            SELECT 
                dt.mes_nombre || ' ' || dt.anio as mes,
                SUM(fpc.horas_capacitacion_recibidas) as horas
            FROM dwh.fact_participacion_capacitacion fpc
            JOIN dwh.dim_tiempo dt ON fpc.mes_realizacion_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
            GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre
            ORDER BY dt.anio, dt.mes_numero
        """)
        
        result = self.db.execute(query_horas, {
            'start_date': start_date,
            'end_date': end_date
        })
        horas_data = [MetricPoint(label=row[0], value=row[1] or 0) for row in result]

        # Participación por categoría temática
        query_categorias = text("""
            SELECT 
                dc.categoria_tematica,
                COUNT(DISTINCT fpc.empleado_sk) as participantes
            FROM dwh.fact_participacion_capacitacion fpc
            JOIN dwh.dim_curso dc ON fpc.curso_sk = dc.curso_sk
            JOIN dwh.dim_tiempo dt ON fpc.mes_realizacion_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
                AND dc.categoria_tematica IS NOT NULL
            GROUP BY dc.categoria_tematica
            ORDER BY participantes DESC
        """)
        
        result = self.db.execute(query_categorias, {
            'start_date': start_date,
            'end_date': end_date
        })
        categorias_data = [MetricPoint(label=row[0], value=row[1]) for row in result]

        # Estadísticas generales
        query_stats = text("""
            SELECT 
                SUM(fpc.horas_capacitacion_recibidas) as total_horas,
                COUNT(DISTINCT fpc.empleado_sk) as total_participantes,
                AVG(frc.satisfaccion_promedio) as promedio_satisfaccion,
                AVG(frc.nps_score) as promedio_nps
            FROM dwh.fact_participacion_capacitacion fpc
            LEFT JOIN dwh.fact_realizacion_capacitacion frc 
                ON fpc.realizacion_link_id = frc.realizacion_id
            JOIN dwh.dim_tiempo dt ON fpc.mes_realizacion_sk = dt.tiempo_sk
            WHERE dt.fecha BETWEEN :start_date AND :end_date
        """)
        
        result = self.db.execute(query_stats, {
            'start_date': start_date,
            'end_date': end_date
        }).fetchone()

        return CapacitacionMetrics(
            horas_capacitacion_mensual=horas_data,
            participacion_por_categoria=categorias_data,
            total_horas_capacitacion=round(result[0] or 0, 1),
            total_participantes=result[1] or 0,
            promedio_satisfaccion=round(result[2] or 0, 2),
            promedio_nps=round(result[3] or 0, 2)
        )

    def get_all_metrics(self, start_date: date, end_date: date) -> DashboardMetrics:
        """Obtener todas las métricas del dashboard"""
        return DashboardMetrics(
            asistencia=self.get_asistencia_metrics(start_date, end_date),
            rotacion=self.get_rotacion_metrics(start_date, end_date),
            seleccion=self.get_seleccion_metrics(start_date, end_date),
            capacitacion=self.get_capacitacion_metrics(start_date, end_date),
            periodo_inicio=start_date,
            periodo_fin=end_date
        )
