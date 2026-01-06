DO $$
DECLARE
    -- === CONFIGURACIÓN ===
    TOLERANCIA_MIN CONSTANT INTEGER := 5;
    
    fecha_rec RECORD;
    count_stg INTEGER;
    count_dwh INTEGER;
BEGIN
    -- 1. Iteramos por cada fecha distinta presente en el Staging
    FOR fecha_rec IN SELECT DISTINCT asistio_en FROM stg.stg_asistencia_diaria LOOP
        
        -- 2. Obtenemos conteos
        SELECT COUNT(*) INTO count_stg 
        FROM stg.stg_asistencia_diaria 
        WHERE asistio_en = fecha_rec.asistio_en;
        
        SELECT COUNT(*) INTO count_dwh 
        FROM dwh.fact_asistencia 
        WHERE fecha_sk = TO_CHAR(fecha_rec.asistio_en, 'YYYYMMDD')::INTEGER;
        
        -- 3. VALIDACIÓN (Smart Load)
        -- Si los conteos son distintos (o DWH es 0), procedemos a recargar esa fecha
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
                COALESCE(de.empleado_sk, -1),
                COALESCE(dt.turno_sk, -1),

                -- Timestamps (Fecha + Hora 24hr)
                (s.asistio_en || ' ' || s.hora_ingreso)::TIMESTAMP,
                (s.asistio_en || ' ' || s.hora_salida)::TIMESTAMP,

                -- Horas trabajadas (formato decimal o nulo)
                CAST(REPLACE(CAST(s.total_horas AS VARCHAR), ',', '.') AS DECIMAL(5,2)),

                -- Conversión Duración Atraso (H:MM a Minutos Enteros)
                -- 1:30 -> 90 min, 0:15 -> 15 min, 0:00 -> 0
                CASE 
                    WHEN s.atraso IS NULL OR s.atraso = '0:00' THEN 0
                    ELSE (SPLIT_PART(s.atraso, ':', 1)::INT * 60) + SPLIT_PART(s.atraso, ':', 2)::INT
                END,

                -- Conversión Duración Adelanto
                CASE 
                    WHEN s.adelanto IS NULL OR s.adelanto = '0:00' THEN 0
                    ELSE (SPLIT_PART(s.adelanto, ':', 1)::INT * 60) + SPLIT_PART(s.adelanto, ':', 2)::INT
                END,

                s.tipo_permiso,

                -- Flag Atraso (Usando la constante)
                CASE 
                    WHEN ((SPLIT_PART(s.atraso, ':', 1)::INT * 60) + SPLIT_PART(s.atraso, ':', 2)::INT) > TOLERANCIA_MIN THEN 1 
                    ELSE 0 
                END,

                -- Flag Salida Anticipada
                CASE 
                    WHEN ((SPLIT_PART(s.adelanto, ':', 1)::INT * 60) + SPLIT_PART(s.adelanto, ':', 2)::INT) > 0 THEN 1 
                    ELSE 0 
                END,

                -- Flag Ausencia
                CASE 
                    WHEN LOWER(s.tipo_permiso) LIKE '%inasistente%' OR LOWER(s.tipo_permiso) LIKE '%falla%' THEN 1
                    ELSE 0 
                END,

                TOLERANCIA_MIN -- Guardamos qué regla se aplicó

            FROM stg.stg_asistencia_diaria s
            LEFT JOIN dwh.dim_permiso dp ON TRIM(s.tipo_permiso) = dp.codigo_permiso_nk
            LEFT JOIN dwh.dim_turno dt ON TRIM(s.tipo_turno) = dt.nombre_turno
            -- Join SCD2 Empleado
            LEFT JOIN dwh.dim_empleado de 
                ON CAST(s.id_empleado AS VARCHAR) = de.empleado_id_nk 
                AND s.asistio_en BETWEEN de.scd_fecha_inicio_vigencia AND de.scd_fecha_fin_vigencia
            
            WHERE s.asistio_en = fecha_rec.asistio_en; -- Solo insertamos la fecha del bucle
            
        ELSE
            RAISE NOTICE 'Fecha % sin cambios en volumen (Stg: %, Dwh: %). OMITIDA.', fecha_rec.asistio_en, count_stg, count_dwh;
        END IF;

    END LOOP;
END $$;