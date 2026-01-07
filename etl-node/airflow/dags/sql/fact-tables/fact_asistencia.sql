-- =============================================================================
-- FACT_ASISTENCIA.SQL - Carga de hechos de asistencia diaria
-- =============================================================================
-- IMPORTANTE: Este ETL requiere que dim_empleado tenga todos los empleados
-- de stg_asistencia_diaria. Si faltan empleados, primero se insertan en la
-- dimensión con datos mínimos para evitar pérdida de datos.
-- =============================================================================

DO $$
DECLARE
    -- === CONFIGURACIÓN ===
    TOLERANCIA_MIN CONSTANT INTEGER := 5;
    FECHA_VIGENCIA_DEFAULT CONSTANT DATE := '2020-01-01';
    
    fecha_rec RECORD;
    count_stg INTEGER;
    count_dwh INTEGER;
    empleados_nuevos INTEGER;
BEGIN
    -- =========================================================================
    -- PASO 0: Asegurar que todos los empleados de asistencia existan en dim_empleado
    -- =========================================================================
    INSERT INTO dwh.dim_empleado (
        empleado_id_nk,
        nombre_completo,
        estado_laboral_activo,
        scd_fecha_inicio_vigencia,
        scd_fecha_fin_vigencia,
        scd_es_actual
    )
    SELECT DISTINCT
        CAST(s.id_empleado AS VARCHAR),
        'EMPLEADO ' || s.id_empleado || ' (PENDIENTE SINCRONIZAR)',
        TRUE,
        FECHA_VIGENCIA_DEFAULT,
        '9999-12-31'::DATE,
        TRUE
    FROM stg.stg_asistencia_diaria s
    WHERE NOT EXISTS (
        SELECT 1 FROM dwh.dim_empleado de 
        WHERE de.empleado_id_nk = CAST(s.id_empleado AS VARCHAR)
    );
    
    GET DIAGNOSTICS empleados_nuevos = ROW_COUNT;
    IF empleados_nuevos > 0 THEN
        RAISE NOTICE '[ASISTENCIA] Insertados % empleados faltantes en dim_empleado', empleados_nuevos;
    END IF;

    -- =========================================================================
    -- PASO 1: Iterar por cada fecha en Staging
    -- =========================================================================
    FOR fecha_rec IN SELECT DISTINCT asistio_en FROM stg.stg_asistencia_diaria LOOP
        
        -- 2. Obtenemos conteos
        SELECT COUNT(*) INTO count_stg 
        FROM stg.stg_asistencia_diaria 
        WHERE asistio_en = fecha_rec.asistio_en;
        
        SELECT COUNT(*) INTO count_dwh 
        FROM dwh.fact_asistencia 
        WHERE fecha_sk = TO_CHAR(fecha_rec.asistio_en, 'YYYYMMDD')::INTEGER;
        
        -- 3. VALIDACIÓN (Smart Load)
        IF count_stg <> count_dwh THEN
            
            RAISE NOTICE 'Recargando fecha % (Stg: %, Dwh: %)', fecha_rec.asistio_en, count_stg, count_dwh;

            -- A. Borrar datos viejos de esa fecha específica
            DELETE FROM dwh.fact_asistencia 
            WHERE fecha_sk = TO_CHAR(fecha_rec.asistio_en, 'YYYYMMDD')::INTEGER;

            -- B. Insertar datos nuevos
            INSERT INTO dwh.fact_asistencia (
                fecha_sk, permiso_sk, empleado_sk, turno_planificado_sk,
                hora_entrada_real, hora_salida_real,
                horas_trabajadas, minutos_atraso, minutos_adelanto_salida,
                permiso_aplicado,
                es_atraso, es_salida_anticipada, es_ausencia, tolerancia_aplicada_min
            )
            SELECT 
                TO_CHAR(s.asistio_en, 'YYYYMMDD')::INTEGER,
                COALESCE(dp.permiso_sk, -1),
                de.empleado_sk,  -- Ya no usamos COALESCE, el empleado DEBE existir
                COALESCE(dt.turno_sk, -1),

                -- Timestamps (Fecha + Hora)
                CASE WHEN s.hora_ingreso IS NOT NULL THEN s.asistio_en + s.hora_ingreso ELSE NULL END,
                CASE WHEN s.hora_salida IS NOT NULL THEN s.asistio_en + s.hora_salida ELSE NULL END,

                -- Horas trabajadas (extraer de interval a decimal)
                CASE 
                    WHEN s.total_horas IS NULL THEN NULL
                    ELSE EXTRACT(EPOCH FROM s.total_horas) / 3600.0
                END::DECIMAL(5,2),

                -- Minutos de atraso (extraer de interval)
                CASE 
                    WHEN s.atraso IS NULL THEN 0
                    ELSE EXTRACT(EPOCH FROM s.atraso) / 60
                END::INTEGER,

                -- Minutos de adelanto (extraer de interval)
                CASE 
                    WHEN s.adelanto IS NULL THEN 0
                    ELSE EXTRACT(EPOCH FROM s.adelanto) / 60
                END::INTEGER,

                s.tipo_permiso,

                -- Flag Atraso (Usando la constante)
                CASE 
                    WHEN s.atraso IS NULL THEN 0
                    WHEN (EXTRACT(EPOCH FROM s.atraso) / 60) > TOLERANCIA_MIN THEN 1 
                    ELSE 0 
                END,

                -- Flag Salida Anticipada
                CASE 
                    WHEN s.adelanto IS NULL THEN 0
                    WHEN (EXTRACT(EPOCH FROM s.adelanto) / 60) > 0 THEN 1 
                    ELSE 0 
                END,

                -- Flag Ausencia
                CASE 
                    WHEN LOWER(s.tipo_permiso) LIKE '%inasistente%' OR LOWER(s.tipo_permiso) LIKE '%falla%' THEN 1
                    ELSE 0 
                END,

                TOLERANCIA_MIN

            FROM stg.stg_asistencia_diaria s
            LEFT JOIN dwh.dim_permiso dp ON TRIM(s.tipo_permiso) = dp.codigo_permiso_nk
            LEFT JOIN dwh.dim_turno dt ON TRIM(s.tipo_turno) = dt.nombre_turno
            -- JOIN con scd_es_actual (más robusto que BETWEEN con fechas)
            INNER JOIN dwh.dim_empleado de 
                ON CAST(s.id_empleado AS VARCHAR) = de.empleado_id_nk 
                AND de.scd_es_actual = TRUE
            
            WHERE s.asistio_en = fecha_rec.asistio_en;
            
        ELSE
            RAISE NOTICE 'Fecha % sin cambios (Stg: %, Dwh: %). OMITIDA.', fecha_rec.asistio_en, count_stg, count_dwh;
        END IF;

    END LOOP;
END $$;