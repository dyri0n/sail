-- =============================================================================
-- FACT_PARTICIPACION.SQL - Carga de participación en capacitaciones
-- =============================================================================
-- IMPORTANTE: Este ETL requiere que dim_empleado tenga todos los empleados
-- de stg_participacion_capacitaciones. Si faltan, se insertan automáticamente.
-- =============================================================================

DO $$
DECLARE
    empleados_nuevos INTEGER;
    FECHA_VIGENCIA_DEFAULT CONSTANT DATE := '2020-01-01';
BEGIN
    -- =========================================================================
    -- PASO 0: Asegurar que todos los empleados de participación existan
    -- =========================================================================
    INSERT INTO dwh.dim_empleado (
        empleado_id_nk,
        rut,
        nombre_completo,
        estado_laboral_activo,
        scd_fecha_inicio_vigencia,
        scd_fecha_fin_vigencia,
        scd_es_actual
    )
    SELECT DISTINCT
        CAST(s.id_empleado AS VARCHAR),
        s.rut,
        COALESCE(TRIM(s.nombre) || ' ' || TRIM(s.apellidos), 'EMPLEADO ' || s.id_empleado),
        TRUE,
        FECHA_VIGENCIA_DEFAULT,
        '9999-12-31'::DATE,
        TRUE
    FROM stg.stg_participacion_capacitaciones s
    WHERE s.id_empleado IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM dwh.dim_empleado de 
        WHERE de.empleado_id_nk = CAST(s.id_empleado AS VARCHAR)
    );
    
    GET DIAGNOSTICS empleados_nuevos = ROW_COUNT;
    IF empleados_nuevos > 0 THEN
        RAISE NOTICE '[PARTICIPACION] Insertados % empleados faltantes en dim_empleado', empleados_nuevos;
    END IF;
END $$;

-- =========================================================================
-- Insertar participaciones (solo empleados que existen)
-- =========================================================================
INSERT INTO dwh.fact_participacion_capacitacion (
    mes_realizacion_sk,
    empleado_sk,
    curso_sk,
    realizacion_link_id,
    horas_capacitacion_recibidas,
    asistencia_count
)
SELECT DISTINCT ON (mes_sk, empleado_sk, curso_sk)
    mes_sk,
    empleado_sk,
    curso_sk,
    realizacion_link_id,
    total_horas_formacion,
    asistencia_count
FROM (
    SELECT 
        TO_CHAR(
            MAKE_DATE(
                EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER,
                CASE UPPER(TRIM(s.mes))
                    WHEN 'ENERO' THEN 1 WHEN 'FEBRERO' THEN 2 WHEN 'MARZO' THEN 3
                    WHEN 'ABRIL' THEN 4 WHEN 'MAYO' THEN 5 WHEN 'JUNIO' THEN 6
                    WHEN 'JULIO' THEN 7 WHEN 'AGOSTO' THEN 8 WHEN 'SEPTIEMBRE' THEN 9
                    WHEN 'OCTUBRE' THEN 10 WHEN 'NOVIEMBRE' THEN 11 WHEN 'DICIEMBRE' THEN 12
                    ELSE 1
                END,
                1
            ),
            'YYYYMMDD'
        )::INTEGER AS mes_sk,
        
        de.empleado_sk,  -- Ya no usamos COALESCE, el empleado DEBE existir
        COALESCE(dc.curso_sk, -1) AS curso_sk,
        fr.realizacion_id AS realizacion_link_id,
        s.total_horas_formacion,
        1 AS asistencia_count

    FROM stg.stg_participacion_capacitaciones s

    -- INNER JOIN: solo cargar si el empleado existe
    INNER JOIN dwh.dim_empleado de 
        ON s.id_empleado::VARCHAR = de.empleado_id_nk
        AND de.scd_es_actual = TRUE

    LEFT JOIN dwh.dim_curso dc 
        ON TRIM(UPPER(s.nombre_curso)) = dc.nombre_curso

    LEFT JOIN dwh.fact_realizacion_capacitacion fr
        ON fr.curso_sk = dc.curso_sk
        
    WHERE s.id_empleado IS NOT NULL  -- Ignorar registros sin ID
) subq

ON CONFLICT (mes_realizacion_sk, empleado_sk, curso_sk) DO UPDATE SET
    horas_capacitacion_recibidas = EXCLUDED.horas_capacitacion_recibidas,
    realizacion_link_id = EXCLUDED.realizacion_link_id;