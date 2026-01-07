-- =============================================================================
-- 04-VIEWS-ANALYTICS.SQL - Vistas Analíticas del Data Warehouse
-- =============================================================================
-- Vistas preconstruidas para dashboards y reportes de negocio.
-- Una vista principal por cada Fact Table.
-- =============================================================================

SET ROLE dwh_admin;
SET search_path TO dwh;

-- =============================================================================
-- 1. VISTA: EFECTIVIDAD DE RECLUTAMIENTO (FACT_SELECCION)
-- =============================================================================
-- Pregunta: ¿Cuál es la tasa de éxito de contrataciones por fuente de 
--           reclutamiento y cuántas lograron continuidad (+4 meses)?
-- Gráfico recomendado: Barras agrupadas (fuente vs contrataciones/continuidad)
-- =============================================================================

CREATE OR REPLACE VIEW vw_efectividad_reclutamiento AS
SELECT 
    fs.fuente_reclutamiento,
    COUNT(*) AS total_procesos,
    COUNT(fs.empleado_seleccionado_sk) AS contrataciones_exitosas,
    SUM(fs.tiene_continuidad) AS con_continuidad,
    ROUND(AVG(fs.duracion_proceso_dias), 1) AS dias_promedio_proceso,
    ROUND(SUM(fs.costo_proceso)::NUMERIC, 2) AS costo_total,
    ROUND(
        100.0 * SUM(fs.tiene_continuidad) / NULLIF(COUNT(fs.empleado_seleccionado_sk), 0), 
        1
    ) AS tasa_continuidad_pct,
    ROUND(
        100.0 * COUNT(fs.empleado_seleccionado_sk) / NULLIF(COUNT(*), 0), 
        1
    ) AS tasa_exito_pct,
    ROUND(
        SUM(fs.costo_proceso)::NUMERIC / NULLIF(COUNT(fs.empleado_seleccionado_sk), 0), 
        2
    ) AS costo_por_contratacion
FROM dwh.fact_seleccion fs
WHERE fs.estado_final_proceso = 'CERRADO'
GROUP BY fs.fuente_reclutamiento;

COMMENT ON VIEW vw_efectividad_reclutamiento IS 
'Análisis de efectividad del proceso de selección por fuente de reclutamiento. 
Incluye tasas de éxito, continuidad y costos asociados.';

-- =============================================================================
-- 2. VISTA: TENDENCIA DE PUNTUALIDAD (FACT_ASISTENCIA)
-- =============================================================================
-- Pregunta: ¿Cómo evoluciona la tasa de atrasos y ausencias por mes, 
--           y cuál es el impacto en horas perdidas?
-- Gráfico recomendado: Líneas temporales con doble eje Y
-- =============================================================================

CREATE OR REPLACE VIEW vw_tendencia_puntualidad AS
SELECT 
    dt.anio,
    dt.mes_numero,
    dt.mes_nombre,
    dt.trimestre,
    COUNT(*) AS total_registros,
    SUM(fa.es_atraso) AS cantidad_atrasos,
    SUM(fa.es_ausencia) AS cantidad_ausencias,
    SUM(fa.es_salida_anticipada) AS salidas_anticipadas,
    ROUND(100.0 * SUM(fa.es_atraso) / NULLIF(COUNT(*), 0), 2) AS tasa_atraso_pct,
    ROUND(100.0 * SUM(fa.es_ausencia) / NULLIF(COUNT(*), 0), 2) AS tasa_ausencia_pct,
    ROUND(SUM(fa.minutos_atraso)::NUMERIC / 60.0, 2) AS horas_perdidas_atrasos,
    ROUND(AVG(fa.horas_trabajadas)::NUMERIC, 2) AS horas_trabajadas_promedio,
    ROUND(SUM(fa.horas_trabajadas)::NUMERIC, 2) AS horas_trabajadas_totales,
    COUNT(DISTINCT fa.empleado_sk) AS empleados_unicos
FROM dwh.fact_asistencia fa
JOIN dwh.dim_tiempo dt ON fa.fecha_sk = dt.tiempo_sk
GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre, dt.trimestre
ORDER BY dt.anio, dt.mes_numero;

COMMENT ON VIEW vw_tendencia_puntualidad IS 
'Evolución mensual de indicadores de puntualidad y ausentismo. 
Útil para identificar patrones estacionales y tendencias.';

-- Vista complementaria: Detalle por día de semana
CREATE OR REPLACE VIEW vw_puntualidad_por_dia_semana AS
SELECT 
    dt.dia_semana,
    dt.es_fin_de_semana,
    COUNT(*) AS total_registros,
    SUM(fa.es_atraso) AS cantidad_atrasos,
    SUM(fa.es_ausencia) AS cantidad_ausencias,
    ROUND(100.0 * SUM(fa.es_atraso) / NULLIF(COUNT(*), 0), 2) AS tasa_atraso_pct,
    ROUND(AVG(fa.minutos_atraso)::NUMERIC, 1) AS minutos_atraso_promedio
FROM dwh.fact_asistencia fa
JOIN dwh.dim_tiempo dt ON fa.fecha_sk = dt.tiempo_sk
GROUP BY dt.dia_semana, dt.es_fin_de_semana
ORDER BY 
    CASE dt.dia_semana 
        WHEN 'Lunes' THEN 1 
        WHEN 'Martes' THEN 2 
        WHEN 'Miércoles' THEN 3 
        WHEN 'Jueves' THEN 4 
        WHEN 'Viernes' THEN 5 
        WHEN 'Sábado' THEN 6 
        WHEN 'Domingo' THEN 7 
    END;

COMMENT ON VIEW vw_puntualidad_por_dia_semana IS 
'Análisis de puntualidad segmentado por día de la semana para identificar patrones.';

-- =============================================================================
-- 3. VISTA: FLUJO DE ROTACIÓN (FACT_ROTACION)
-- =============================================================================
-- Pregunta: ¿Cuál es el balance neto de headcount (altas vs bajas) por empresa 
--           y tipo de movimiento?
-- Gráfico recomendado: Waterfall o Sankey para visualizar flujos
-- =============================================================================

CREATE OR REPLACE VIEW vw_flujo_rotacion AS
SELECT 
    dt.anio,
    dt.mes_numero,
    dt.mes_nombre,
    de.nombre AS empresa,
    dma.tipo_movimiento,
    CASE WHEN dma.es_voluntario THEN 'Voluntario' ELSE 'Involuntario' END AS tipo_salida,
    COUNT(*) AS cantidad_movimientos,
    SUM(fr.variacion_headcount) AS impacto_headcount,
    ROUND(AVG(fr.sueldo_base_intervalo)::NUMERIC, 2) AS sueldo_promedio_afectado,
    ROUND(SUM(fr.sueldo_base_intervalo)::NUMERIC, 2) AS masa_salarial_afectada
FROM dwh.fact_rotacion fr
JOIN dwh.dim_empresa de ON fr.empresa_sk = de.empresa_sk
JOIN dwh.dim_medida_aplicada dma ON fr.medida_sk = dma.medida_sk
JOIN dwh.dim_tiempo dt ON fr.fecha_inicio_vigencia_sk = dt.tiempo_sk
GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre, de.nombre, dma.tipo_movimiento, dma.es_voluntario
ORDER BY dt.anio, dt.mes_numero, de.nombre;

COMMENT ON VIEW vw_flujo_rotacion IS 
'Balance de altas y bajas por empresa y tipo de movimiento. 
Variacion_headcount: +1 (Alta), -1 (Baja), 0 (Cambio interno).';

-- Vista complementaria: Resumen anual de rotación
CREATE OR REPLACE VIEW vw_rotacion_resumen_anual AS
SELECT 
    dt.anio,
    de.nombre AS empresa,
    SUM(CASE WHEN fr.variacion_headcount = 1 THEN 1 ELSE 0 END) AS total_altas,
    SUM(CASE WHEN fr.variacion_headcount = -1 THEN 1 ELSE 0 END) AS total_bajas,
    SUM(CASE WHEN fr.variacion_headcount = 0 THEN 1 ELSE 0 END) AS total_cambios,
    SUM(fr.variacion_headcount) AS variacion_neta,
    SUM(CASE WHEN fr.variacion_headcount = -1 AND dma.es_voluntario THEN 1 ELSE 0 END) AS bajas_voluntarias,
    SUM(CASE WHEN fr.variacion_headcount = -1 AND NOT dma.es_voluntario THEN 1 ELSE 0 END) AS bajas_involuntarias,
    ROUND(
        100.0 * SUM(CASE WHEN fr.variacion_headcount = -1 AND dma.es_voluntario THEN 1 ELSE 0 END) / 
        NULLIF(SUM(CASE WHEN fr.variacion_headcount = -1 THEN 1 ELSE 0 END), 0), 
        1
    ) AS pct_bajas_voluntarias
FROM dwh.fact_rotacion fr
JOIN dwh.dim_empresa de ON fr.empresa_sk = de.empresa_sk
JOIN dwh.dim_medida_aplicada dma ON fr.medida_sk = dma.medida_sk
JOIN dwh.dim_tiempo dt ON fr.fecha_inicio_vigencia_sk = dt.tiempo_sk
GROUP BY dt.anio, de.nombre
ORDER BY dt.anio, de.nombre;

COMMENT ON VIEW vw_rotacion_resumen_anual IS 
'Resumen anual de rotación con desglose de altas, bajas voluntarias e involuntarias.';

-- =============================================================================
-- 4. VISTA: EVOLUCIÓN DE DOTACIÓN (FACT_DOTACION_SNAPSHOT)
-- =============================================================================
-- Pregunta: ¿Cómo ha evolucionado el headcount y el costo salarial por 
--           modalidad de contrato mes a mes?
-- Gráfico recomendado: Área apilada (evolución temporal por modalidad)
-- =============================================================================

CREATE OR REPLACE VIEW vw_evolucion_dotacion AS
SELECT 
    dt.anio,
    dt.mes_numero,
    dt.mes_nombre,
    dt.trimestre,
    dmc.tipo_vinculo_legal,
    dmc.regimen_horario,
    SUM(fds.headcount) AS total_headcount,
    ROUND(SUM(fds.fte_real)::NUMERIC, 2) AS total_fte,
    ROUND(SUM(fds.sueldo_base_mensual)::NUMERIC, 2) AS masa_salarial,
    ROUND(AVG(fds.antiguedad_meses)::NUMERIC, 1) AS antiguedad_promedio_meses,
    SUM(fds.horas_capacidad_mensual) AS horas_capacidad_total,
    ROUND(
        SUM(fds.sueldo_base_mensual)::NUMERIC / NULLIF(SUM(fds.headcount), 0), 
        2
    ) AS sueldo_promedio
FROM dwh.fact_dotacion_snapshot fds
JOIN dwh.dim_tiempo dt ON fds.mes_cierre_sk = dt.tiempo_sk
JOIN dwh.dim_modalidad_contrato dmc ON fds.modalidad_sk = dmc.modalidad_sk
GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre, dt.trimestre, 
         dmc.tipo_vinculo_legal, dmc.regimen_horario
ORDER BY dt.anio, dt.mes_numero;

COMMENT ON VIEW vw_evolucion_dotacion IS 
'Snapshot mensual de dotación por modalidad de contrato. 
Incluye headcount, FTE, masa salarial y antigüedad.';

-- Vista complementaria: Dotación por empresa y cargo
CREATE OR REPLACE VIEW vw_dotacion_empresa_cargo AS
SELECT 
    dt.anio,
    dt.mes_numero,
    de.nombre AS empresa,
    dc.area_funcional,
    dc.nombre_cargo,
    SUM(fds.headcount) AS total_headcount,
    ROUND(SUM(fds.fte_real)::NUMERIC, 2) AS total_fte,
    ROUND(SUM(fds.sueldo_base_mensual)::NUMERIC, 2) AS masa_salarial,
    ROUND(AVG(fds.antiguedad_meses)::NUMERIC, 1) AS antiguedad_promedio
FROM dwh.fact_dotacion_snapshot fds
JOIN dwh.dim_tiempo dt ON fds.mes_cierre_sk = dt.tiempo_sk
JOIN dwh.dim_empresa de ON fds.empresa_sk = de.empresa_sk
JOIN dwh.dim_cargo dc ON fds.cargo_sk = dc.cargo_sk
GROUP BY dt.anio, dt.mes_numero, de.nombre, dc.area_funcional, dc.nombre_cargo
ORDER BY dt.anio, dt.mes_numero, de.nombre, masa_salarial DESC;

COMMENT ON VIEW vw_dotacion_empresa_cargo IS 
'Detalle de dotación por empresa, área funcional y cargo.';

-- =============================================================================
-- 5. VISTA: ROI DE CAPACITACIONES (FACT_REALIZACION_CAPACITACION)
-- =============================================================================
-- Pregunta: ¿Cuál es la relación costo-beneficio de los cursos por categoría 
--           temática y cuál tiene mejor satisfacción?
-- Gráfico recomendado: Burbujas (X: costo, Y: satisfacción, tamaño: participantes)
-- =============================================================================

CREATE OR REPLACE VIEW vw_roi_capacitaciones AS
SELECT 
    dc.categoria_tematica,
    dc.modalidad AS modalidad_curso,
    dp.nombre_proveedor,
    COUNT(*) AS cursos_realizados,
    SUM(frc.total_asistentes) AS total_participantes,
    ROUND(SUM(frc.costo_total_curso)::NUMERIC, 2) AS inversion_total,
    ROUND(
        SUM(frc.costo_total_curso)::NUMERIC / NULLIF(SUM(frc.total_asistentes), 0), 
        2
    ) AS costo_por_asistente,
    ROUND(AVG(frc.satisfaccion_promedio)::NUMERIC, 2) AS satisfaccion_promedio,
    ROUND(AVG(frc.nps_score)::NUMERIC, 1) AS nps_promedio,
    ROUND(AVG(frc.valoracion_formador)::NUMERIC, 2) AS valoracion_formador_promedio,
    SUM(frc.duracion_horas_total) AS horas_formacion_total,
    ROUND(
        SUM(frc.costo_total_curso)::NUMERIC / NULLIF(SUM(frc.duracion_horas_total), 0), 
        2
    ) AS costo_por_hora
FROM dwh.fact_realizacion_capacitacion frc
JOIN dwh.dim_curso dc ON frc.curso_sk = dc.curso_sk
LEFT JOIN dwh.dim_proveedor dp ON frc.proveedor_sk = dp.proveedor_sk
GROUP BY dc.categoria_tematica, dc.modalidad, dp.nombre_proveedor;

COMMENT ON VIEW vw_roi_capacitaciones IS 
'Análisis de retorno de inversión en capacitaciones por categoría temática. 
Incluye costos, satisfacción y NPS.';

-- Vista complementaria: Tendencia temporal de capacitaciones
CREATE OR REPLACE VIEW vw_capacitaciones_tendencia AS
SELECT 
    dt.anio,
    dt.mes_numero,
    dt.mes_nombre,
    dt.trimestre,
    COUNT(*) AS cursos_realizados,
    SUM(frc.total_asistentes) AS total_participantes,
    ROUND(SUM(frc.costo_total_curso)::NUMERIC, 2) AS inversion_mensual,
    ROUND(AVG(frc.satisfaccion_promedio)::NUMERIC, 2) AS satisfaccion_promedio,
    SUM(frc.duracion_horas_total) AS horas_formacion
FROM dwh.fact_realizacion_capacitacion frc
JOIN dwh.dim_tiempo dt ON frc.fecha_inicio_sk = dt.tiempo_sk
GROUP BY dt.anio, dt.mes_numero, dt.mes_nombre, dt.trimestre
ORDER BY dt.anio, dt.mes_numero;

COMMENT ON VIEW vw_capacitaciones_tendencia IS 
'Evolución mensual de la actividad de capacitación.';

-- =============================================================================
-- 6. VISTA: COBERTURA DE CAPACITACIÓN (FACT_PARTICIPACION_CAPACITACION)
-- =============================================================================
-- Pregunta: ¿Cuál es la distribución de horas de capacitación por empleado 
--           y categoría temática?
-- Gráfico recomendado: Treemap o Heatmap
-- =============================================================================

CREATE OR REPLACE VIEW vw_cobertura_capacitacion AS
SELECT 
    dc.categoria_tematica,
    dc.modalidad AS modalidad_curso,
    dt.anio,
    COUNT(DISTINCT fpc.empleado_sk) AS empleados_capacitados,
    COUNT(*) AS total_participaciones,
    ROUND(SUM(fpc.horas_capacitacion_recibidas)::NUMERIC, 2) AS horas_totales,
    ROUND(
        AVG(fpc.horas_capacitacion_recibidas)::NUMERIC, 
        2
    ) AS horas_promedio_por_participacion,
    ROUND(
        SUM(fpc.horas_capacitacion_recibidas)::NUMERIC / 
        NULLIF(COUNT(DISTINCT fpc.empleado_sk), 0), 
        2
    ) AS horas_promedio_por_empleado,
    SUM(fpc.asistencia_count) AS asistencias_totales
FROM dwh.fact_participacion_capacitacion fpc
JOIN dwh.dim_curso dc ON fpc.curso_sk = dc.curso_sk
JOIN dwh.dim_tiempo dt ON fpc.mes_realizacion_sk = dt.tiempo_sk
GROUP BY dc.categoria_tematica, dc.modalidad, dt.anio
ORDER BY dt.anio, horas_totales DESC;

COMMENT ON VIEW vw_cobertura_capacitacion IS 
'Distribución de horas de capacitación por categoría temática y año.';

-- Vista complementaria: Top empleados más capacitados
CREATE OR REPLACE VIEW vw_top_empleados_capacitados AS
SELECT 
    de.empleado_id_nk,
    de.nombre_completo,
    de.estado_laboral_activo,
    dt.anio,
    COUNT(DISTINCT fpc.curso_sk) AS cursos_distintos,
    COUNT(*) AS total_participaciones,
    ROUND(SUM(fpc.horas_capacitacion_recibidas)::NUMERIC, 2) AS horas_totales,
    STRING_AGG(DISTINCT dc.categoria_tematica, ', ' ORDER BY dc.categoria_tematica) AS categorias_cursadas
FROM dwh.fact_participacion_capacitacion fpc
JOIN dwh.dim_empleado de ON fpc.empleado_sk = de.empleado_sk
JOIN dwh.dim_curso dc ON fpc.curso_sk = dc.curso_sk
JOIN dwh.dim_tiempo dt ON fpc.mes_realizacion_sk = dt.tiempo_sk
WHERE de.scd_es_actual = TRUE
GROUP BY de.empleado_id_nk, de.nombre_completo, de.estado_laboral_activo, dt.anio
ORDER BY horas_totales DESC;

COMMENT ON VIEW vw_top_empleados_capacitados IS 
'Ranking de empleados por horas de capacitación recibidas.';

-- =============================================================================
-- 7. VISTAS EJECUTIVAS (DASHBOARDS C-LEVEL)
-- =============================================================================

-- KPIs consolidados para dashboard ejecutivo
CREATE OR REPLACE VIEW vw_kpis_ejecutivos AS
SELECT 
    dt.anio,
    dt.mes_numero,
    dt.mes_nombre,
    
    -- KPIs Dotación
    (SELECT SUM(headcount) FROM dwh.fact_dotacion_snapshot 
     WHERE mes_cierre_sk = dt.tiempo_sk) AS headcount_total,
    (SELECT ROUND(SUM(fte_real)::NUMERIC, 2) FROM dwh.fact_dotacion_snapshot 
     WHERE mes_cierre_sk = dt.tiempo_sk) AS fte_total,
    (SELECT ROUND(SUM(sueldo_base_mensual)::NUMERIC, 2) FROM dwh.fact_dotacion_snapshot 
     WHERE mes_cierre_sk = dt.tiempo_sk) AS masa_salarial,
    
    -- KPIs Rotación (del mes)
    (SELECT SUM(CASE WHEN variacion_headcount = 1 THEN 1 ELSE 0 END) 
     FROM dwh.fact_rotacion fr2
     JOIN dwh.dim_tiempo dt2 ON fr2.fecha_inicio_vigencia_sk = dt2.tiempo_sk
     WHERE dt2.anio = dt.anio AND dt2.mes_numero = dt.mes_numero) AS altas_mes,
    (SELECT SUM(CASE WHEN variacion_headcount = -1 THEN 1 ELSE 0 END) 
     FROM dwh.fact_rotacion fr2
     JOIN dwh.dim_tiempo dt2 ON fr2.fecha_inicio_vigencia_sk = dt2.tiempo_sk
     WHERE dt2.anio = dt.anio AND dt2.mes_numero = dt.mes_numero) AS bajas_mes,
    
    -- KPIs Asistencia (del mes)
    (SELECT ROUND(100.0 * SUM(es_atraso) / NULLIF(COUNT(*), 0), 2)
     FROM dwh.fact_asistencia fa2
     JOIN dwh.dim_tiempo dt2 ON fa2.fecha_sk = dt2.tiempo_sk
     WHERE dt2.anio = dt.anio AND dt2.mes_numero = dt.mes_numero) AS tasa_atraso_pct,
    (SELECT ROUND(100.0 * SUM(es_ausencia) / NULLIF(COUNT(*), 0), 2)
     FROM dwh.fact_asistencia fa2
     JOIN dwh.dim_tiempo dt2 ON fa2.fecha_sk = dt2.tiempo_sk
     WHERE dt2.anio = dt.anio AND dt2.mes_numero = dt.mes_numero) AS tasa_ausencia_pct,
    
    -- KPIs Capacitación (del mes)
    (SELECT COUNT(DISTINCT empleado_sk)
     FROM dwh.fact_participacion_capacitacion fpc2
     JOIN dwh.dim_tiempo dt2 ON fpc2.mes_realizacion_sk = dt2.tiempo_sk
     WHERE dt2.anio = dt.anio AND dt2.mes_numero = dt.mes_numero) AS empleados_capacitados,
    (SELECT ROUND(SUM(horas_capacitacion_recibidas)::NUMERIC, 2)
     FROM dwh.fact_participacion_capacitacion fpc2
     JOIN dwh.dim_tiempo dt2 ON fpc2.mes_realizacion_sk = dt2.tiempo_sk
     WHERE dt2.anio = dt.anio AND dt2.mes_numero = dt.mes_numero) AS horas_capacitacion_mes
     
FROM dwh.dim_tiempo dt
WHERE dt.fecha = DATE_TRUNC('month', dt.fecha) -- Solo primer día de cada mes
ORDER BY dt.anio, dt.mes_numero;

COMMENT ON VIEW vw_kpis_ejecutivos IS 
'Dashboard ejecutivo consolidado con KPIs mensuales de todas las áreas de RRHH.';

-- =============================================================================
-- 8. PERMISOS DE LECTURA PARA LAS VISTAS
-- =============================================================================

-- Otorgar permisos de lectura al rol de reporting (si existe)
-- GRANT SELECT ON ALL TABLES IN SCHEMA dwh TO dwh_readonly;

-- Restaurar rol
RESET ROLE;

-- =============================================================================
-- RESUMEN DE VISTAS CREADAS
-- =============================================================================
/*
| Vista                          | Fact Table                      | Propósito                                    |
|--------------------------------|---------------------------------|----------------------------------------------|
| vw_efectividad_reclutamiento   | fact_seleccion                  | Efectividad por fuente de reclutamiento      |
| vw_tendencia_puntualidad       | fact_asistencia                 | Evolución mensual de atrasos/ausencias       |
| vw_puntualidad_por_dia_semana  | fact_asistencia                 | Patrones por día de la semana                |
| vw_flujo_rotacion              | fact_rotacion                   | Balance altas/bajas por empresa              |
| vw_rotacion_resumen_anual      | fact_rotacion                   | Resumen anual de rotación                    |
| vw_evolucion_dotacion          | fact_dotacion_snapshot          | Headcount por modalidad de contrato          |
| vw_dotacion_empresa_cargo      | fact_dotacion_snapshot          | Dotación por empresa y cargo                 |
| vw_roi_capacitaciones          | fact_realizacion_capacitacion   | ROI por categoría temática                   |
| vw_capacitaciones_tendencia    | fact_realizacion_capacitacion   | Tendencia temporal de capacitaciones         |
| vw_cobertura_capacitacion      | fact_participacion_capacitacion | Horas por categoría y año                    |
| vw_top_empleados_capacitados   | fact_participacion_capacitacion | Ranking de empleados capacitados             |
| vw_kpis_ejecutivos             | Todas                           | Dashboard C-Level consolidado                |
*/
