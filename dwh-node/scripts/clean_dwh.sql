-- ============================================================================
-- SCRIPT DE LIMPIEZA TOTAL - DWH RRHH
-- ============================================================================
-- Este script vacía todas las tablas del DWH y Staging para empezar limpio
-- ADVERTENCIA: Esto eliminará TODOS los datos. Usar solo en desarrollo.
-- ============================================================================

-- 1. LIMPIAR STAGING (schema stg)
-- ============================================================================
TRUNCATE TABLE stg.stg_rotacion_empleados CASCADE;
TRUNCATE TABLE stg.stg_capacitaciones_resumen CASCADE;
TRUNCATE TABLE stg.stg_capacitaciones_participantes CASCADE;
TRUNCATE TABLE stg.stg_asistencia_diaria_geovictoria CASCADE;
TRUNCATE TABLE stg.stg_feriados CASCADE;

-- 2. LIMPIAR FACT TABLES (schema dwh)
-- ============================================================================
TRUNCATE TABLE dwh.fact_asistencia CASCADE;
TRUNCATE TABLE dwh.fact_rotacion CASCADE;
TRUNCATE TABLE dwh.fact_dotacion_snapshot CASCADE;
TRUNCATE TABLE dwh.fact_seleccion CASCADE;
TRUNCATE TABLE dwh.fact_realizacion_capacitacion CASCADE;
TRUNCATE TABLE dwh.fact_participacion_capacitacion CASCADE;

-- 3. LIMPIAR DIMENSION TABLES (schema dwh)
-- ============================================================================
-- IMPORTANTE: Mantener dim_tiempo porque tiene datos precargados
-- Solo limpiar dimensiones que vienen de fuentes externas

TRUNCATE TABLE dwh.dim_empleado CASCADE;
TRUNCATE TABLE dwh.dim_cargo CASCADE;
TRUNCATE TABLE dwh.dim_empresa CASCADE;
TRUNCATE TABLE dwh.dim_gerencia CASCADE;
TRUNCATE TABLE dwh.dim_centro_costo CASCADE;
TRUNCATE TABLE dwh.dim_modalidad_contrato CASCADE;
TRUNCATE TABLE dwh.dim_curso CASCADE;
TRUNCATE TABLE dwh.dim_medida_aplicada CASCADE;

-- dim_tiempo NO se trunca porque tiene el calendario precargado
-- dim_turno y dim_permiso tampoco se truncan (tablas de referencia)

-- 4. RESETEAR SEQUENCES (opcional, para IDs desde 1)
-- ============================================================================
ALTER SEQUENCE dwh.dim_empleado_empleado_sk_seq RESTART WITH 1;
ALTER SEQUENCE dwh.dim_cargo_cargo_sk_seq RESTART WITH 1;
ALTER SEQUENCE dwh.dim_empresa_empresa_sk_seq RESTART WITH 1;
ALTER SEQUENCE dwh.dim_gerencia_gerencia_sk_seq RESTART WITH 1;
ALTER SEQUENCE dwh.dim_centro_costo_ceco_sk_seq RESTART WITH 1;
ALTER SEQUENCE dwh.dim_modalidad_contrato_modalidad_sk_seq RESTART WITH 1;
ALTER SEQUENCE dwh.dim_curso_curso_sk_seq RESTART WITH 1;
ALTER SEQUENCE dwh.dim_medida_aplicada_medida_sk_seq RESTART WITH 1;

ALTER SEQUENCE dwh.fact_asistencia_asistencia_id_seq RESTART WITH 1;
ALTER SEQUENCE dwh.fact_rotacion_rotacion_id_seq RESTART WITH 1;
ALTER SEQUENCE dwh.fact_seleccion_seleccion_id_seq RESTART WITH 1;
ALTER SEQUENCE dwh.fact_realizacion_capacitacion_realizacion_id_seq RESTART WITH 1;
ALTER SEQUENCE dwh.fact_participacion_capacitacion_participacion_id_seq RESTART WITH 1;

-- ============================================================================
-- RESUMEN
-- ============================================================================
SELECT 'Staging limpiado' as status;
SELECT 'DWH Facts limpiadas' as status;
SELECT 'DWH Dimensions limpiadas' as status;
SELECT 'Sequences reiniciadas' as status;
SELECT '✅ Base de datos lista para datos sintéticos' as status;
