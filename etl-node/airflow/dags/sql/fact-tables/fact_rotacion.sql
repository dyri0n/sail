-- =================================================================
-- CONFIGURACIÓN: CLASES DE MEDIDA PARA HEADCOUNT
-- =================================================================
-- Valores reales del Excel (data_rotaciones.xlsx):
--   - "Contratación"           -> +1 (alta)
--   - "Reingreso a la empresa" -> +1 (alta)
--   - "Baja"                   -> -1 (baja)
--   - "Cambio de contrato"     ->  0 (sin cambio headcount)
-- =================================================================
DO $$
DECLARE
    -- Clases que suman headcount (+1)
    CLASES_ALTA CONSTANT TEXT[] := ARRAY[
        'CONTRATACIÓN',
        'REINGRESO A LA EMPRESA'
    ];
    
    -- Clases que restan headcount (-1)
    CLASES_BAJA CONSTANT TEXT[] := ARRAY[
        'BAJA'
    ];
    
    fecha_rec RECORD;
    count_stg INTEGER;
    count_dwh INTEGER;
    meses_afectados DATE[];
BEGIN
    -- =================================================================
    -- PASO 1: SMART LOAD - Comparar volúmenes por fecha
    -- =================================================================
    meses_afectados := ARRAY[]::DATE[];
    
    FOR fecha_rec IN SELECT DISTINCT desde3 FROM stg.stg_rotacion_empleados WHERE desde3 IS NOT NULL LOOP
        
        SELECT COUNT(*) INTO count_stg 
        FROM stg.stg_rotacion_empleados 
        WHERE desde3 = fecha_rec.desde3;
        
        SELECT COUNT(*) INTO count_dwh 
        FROM dwh.fact_rotacion 
        WHERE fecha_inicio_vigencia_sk = TO_CHAR(fecha_rec.desde3, 'YYYYMMDD')::INTEGER;
        
        -- Recargar si hay datos en staging (diferencia de volumen O datos nuevos)
        -- Nota: Si count_stg > 0, siempre procesamos porque staging se trunca post-ETL
        IF count_stg > 0 THEN
            
            RAISE NOTICE 'Procesando fecha % (Stg: %, Dwh: %)', fecha_rec.desde3, count_stg, count_dwh;
            
            -- Registrar el mes afectado para regenerar snapshot después
            meses_afectados := array_append(meses_afectados, DATE_TRUNC('month', fecha_rec.desde3)::DATE);
            
            -- A. Limpiar el día conflictivo
            DELETE FROM dwh.fact_rotacion 
            WHERE fecha_inicio_vigencia_sk = TO_CHAR(fecha_rec.desde3, 'YYYYMMDD')::INTEGER;
            
            -- B. Insertar data limpia
            INSERT INTO dwh.fact_rotacion (
                fecha_inicio_vigencia_sk, fecha_fin_vigencia_sk,
                modalidad_sk, empleado_sk, empresa_sk, ceco_sk, cargo_sk, medida_sk,
                sueldo_base_intervalo, variacion_headcount
            )
            SELECT 
                TO_CHAR(s.desde3, 'YYYYMMDD')::INTEGER,
                TO_CHAR(COALESCE(s.hasta3, '9999-12-31'::DATE), 'YYYYMMDD')::INTEGER,
                COALESCE(dm.modalidad_sk, -1),
                COALESCE(de.empleado_sk, -1),
                COALESCE(demp.empresa_sk, -1),
                COALESCE(dcc.ceco_sk, -1),
                COALESCE(dc.cargo_sk, -1),
                COALESCE(dma.medida_sk, -1),
                0, -- Sueldo Base (mapear si existe columna)
                
                -- Lógica Variación Headcount con arrays configurables
                CASE
                    WHEN TRIM(UPPER(s.clase_medida)) = ANY(CLASES_ALTA) THEN 1
                    WHEN TRIM(UPPER(s.clase_medida)) = ANY(CLASES_BAJA) THEN -1
                    ELSE 0
                END
            FROM stg.stg_rotacion_empleados s
            -- JOIN Empleado: Usar MIN para evitar duplicados si hay múltiples scd_es_actual = TRUE
            LEFT JOIN LATERAL (
                SELECT MIN(empleado_sk) AS empleado_sk 
                FROM dwh.dim_empleado 
                WHERE empleado_id_nk = s.id_empleado::VARCHAR
                AND scd_es_actual = TRUE
            ) de ON TRUE
            -- JOIN Modalidad Contrato
            LEFT JOIN dwh.dim_modalidad_contrato dm 
                ON UPPER(TRIM(s.tipo_empleo)) = UPPER(dm.tipo_vinculo_legal)
                AND UPPER(TRIM(s.jornada)) = UPPER(dm.regimen_horario)
            -- JOIN Empresa
            LEFT JOIN dwh.dim_empresa demp 
                ON s.id_empresa::VARCHAR = demp.codigo
            -- JOIN Centro de Costo
            LEFT JOIN dwh.dim_centro_costo dcc 
                ON UPPER(TRIM(s.ceco)) = UPPER(TRIM(dcc.nombre_ceco))
            -- JOIN Cargo: Usar MIN para evitar duplicados por area_funcional
            LEFT JOIN LATERAL (
                SELECT MIN(cargo_sk) AS cargo_sk 
                FROM dwh.dim_cargo 
                WHERE UPPER(nombre_cargo) = UPPER(TRIM(s.cargo))
            ) dc ON TRUE
            -- JOIN Medida Aplicada (por tipo_movimiento Y razon_detallada)
            LEFT JOIN dwh.dim_medida_aplicada dma 
                ON UPPER(TRIM(s.clase_medida)) = UPPER(dma.tipo_movimiento)
                AND UPPER(TRIM(COALESCE(s.motivo_medida, ''))) = UPPER(COALESCE(dma.razon_detallada, ''))
            WHERE s.desde3 = fecha_rec.desde3;
            
        END IF;
        
    END LOOP;
    
    -- =================================================================
    -- PASO 2: REGENERAR SNAPSHOTS INCREMENTALMENTE
    -- =================================================================
    -- Estrategia: Regenerar desde el mes más antiguo afectado hasta el mes actual.
    -- Esto cubre tanto los meses donde hubo movimientos como los meses futuros
    -- donde los empleados siguen vigentes.
    
    IF array_length(meses_afectados, 1) > 0 THEN
        DECLARE
            mes_minimo DATE;
            mes_maximo DATE;
        BEGIN
            -- Obtener el rango de meses a regenerar
            mes_minimo := (SELECT MIN(m) FROM unnest(meses_afectados) AS m);
            mes_maximo := DATE_TRUNC('month', CURRENT_DATE)::DATE;
            
            RAISE NOTICE 'Regenerando snapshots desde % hasta %', mes_minimo, mes_maximo;
            
            -- Borrar snapshots desde el mes mínimo afectado en adelante
            DELETE FROM dwh.fact_dotacion_snapshot 
            WHERE mes_cierre_sk >= TO_CHAR((mes_minimo + INTERVAL '1 month - 1 day')::DATE, 'YYYYMMDD')::INTEGER;
            
            -- Regenerar snapshots para el rango afectado
            -- Considera TODOS los empleados vigentes en cada mes, no solo los que iniciaron ahí
            INSERT INTO dwh.fact_dotacion_snapshot (
                mes_cierre_sk, empleado_sk, cargo_sk, empresa_sk, modalidad_sk,
                headcount, fte_real, horas_capacidad_mensual, sueldo_base_mensual, antiguedad_meses
            )
            SELECT DISTINCT ON (t.tiempo_sk, f.empleado_sk)
                t.tiempo_sk AS mes_cierre_sk,
                f.empleado_sk,
                f.cargo_sk,
                f.empresa_sk,
                f.modalidad_sk,
                1 AS headcount,
                COALESCE(dmod.fte_estandar, 1.0) AS fte_real,
                ROUND(180 * COALESCE(dmod.fte_estandar, 1.0)) AS horas_capacidad,
                f.sueldo_base_intervalo,
                (EXTRACT(YEAR FROM t.fecha) - EXTRACT(YEAR FROM TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD'))) * 12 +
                (EXTRACT(MONTH FROM t.fecha) - EXTRACT(MONTH FROM TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD')))
            FROM dwh.fact_rotacion f
            JOIN dwh.dim_tiempo t 
                ON t.fecha >= TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD')
                AND t.fecha <= LEAST(
                    TO_DATE(f.fecha_fin_vigencia_sk::text, 'YYYYMMDD'),
                    (mes_maximo + INTERVAL '1 month - 1 day')::DATE
                )
                -- Solo fechas de fin de mes
                AND EXTRACT(MONTH FROM t.fecha) != EXTRACT(MONTH FROM (t.fecha + INTERVAL '1 day'))
                -- Solo meses desde el mínimo afectado en adelante
                AND t.fecha >= (mes_minimo + INTERVAL '1 month - 1 day')::DATE
            JOIN dwh.dim_modalidad_contrato dmod ON f.modalidad_sk = dmod.modalidad_sk
            JOIN dwh.dim_medida_aplicada dma ON f.medida_sk = dma.medida_sk
            WHERE 
                f.empleado_sk > 0
                AND UPPER(dma.tipo_movimiento) NOT IN ('BAJA')
            ORDER BY t.tiempo_sk, f.empleado_sk, f.fecha_inicio_vigencia_sk DESC;
            
            RAISE NOTICE 'Snapshots regenerados incrementalmente';
        END;
    ELSE
        RAISE NOTICE 'Sin meses afectados, no se regeneran snapshots';
    END IF;
    
END $$;